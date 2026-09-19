# `httpget.c` recovery map

`src/httpget.c` remains recovery-owned. The historical compilation unit spans
`0x405890` through `0x4061af` in the original executable. Seven independently
recovered functions now compile in its ordinary partial-object target; the
remaining source is deliberately absent. This document records the
oracle-derived map needed to continue without importing a substitute HTTP
implementation.

The public response is a 20-byte allocation with this layout:

```c
typedef struct HTTPResponse {
    int iStatusCode;
    int iNumHeaders;
    HTTPHeader *pHeaders;
    unsigned char *pPayload;
    int iPayloadSize;
} HTTPResponse;
```

`HTTPHeader` is an eight-byte pair of separately allocated name and value
strings. The 116-byte `destroyHTTPResponse` recovery frees both strings for
every header, then the header array, payload, and response.
`httpGetLastModified` searches the header array for the exact
`"Last-Modified"` name and converts its value using the format
`"%a, %e %b %Y %H:%M:%S"`, `strptime`, and `timegm`; a null response, no
headers, or no matching header returns zero. Its 126-byte body is recovered
with independently resolved string, `strptime`, and `timegm` relocations.

The 35-byte public `strptime` wrapper is recovered separately with its
historical `regparm(3)` parser ABI; its 2028-byte `__strptime` body remains a
dependency for the timestamp helper. The 84-byte `timegm` compatibility unit
is separately recovered with whole-text equality.

The two 27-byte public request wrappers are complete:

```c
HTTPResponse *HTTPHead(char *pURL) { return HTTPRequest(pURL, "HEAD"); }
HTTPResponse *HTTPGet(char *pURL)  { return HTTPRequest(pURL, "GET"); }
```

Their original entry addresses are `0x406178` and `0x406194`. Both call the
136-byte `HTTPRequest` helper at `0x4060f0`. That helper splits a URL into
host, path, and port; on success it calls `HTTPFetchInternal(host, port, path,
method)`, releases the host and path strings, and returns the parsed response.
For an invalid URL it logs `"Could not split URL \"%s\""` and returns null.

`HTTPFetchInternal` is the 594-byte Winsock transport at `0x405e9c`: it creates
a TCP socket, applies a five-second receive timeout (`SO_RCVTIMEO`), resolves
the host, connects,
formats the fixed `"GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n"` request, sends it,
accumulates 1024-byte receives, parses the response, and closes the socket.
The fourth `HTTPRequest` argument is passed through as an additional fetch
argument, but has no observed use in this body; the `HEAD` wrapper therefore
preserves the original call shape without claiming a corrected request method.
Its error paths log the original socket errors. The 267-byte `SplitURL`
recovery initializes all output pointers, accepts the optional `http://`
prefix, extracts the host on `:` or `/`, converts a colon-prefixed port with
`strtol`, and releases both output allocations on failure.
`extractHTTPResponse` remains the 923-byte recovery body, with exact DWARF
extent and oracle disassembly available.

DWARF records a one-byte initial response allocation, 512-byte send and
1024-byte receive buffers, and the local order `sendbuff`, `sprintf`,
`recvbuff`, then `send`. The receive buffer is therefore allocated before the
send call even though it is first consumed in the receive loop. These details
are preserved here as an implementation boundary; the transport body remains
unrecovered until an ordinary C candidate matches all 594 historical bytes.

The line program fixes the original source shape more tightly than the
disassembly alone. `HTTPFetchInternal` begins at source line 149, with
`dataPtr`, `sBufferSize`, `rBufferSize`, and `sock` on lines 150--153. Four
success scopes begin at lines 155, 161, 167, and 172: valid socket, resolved
host, successful connect, and successful send. `totBytes` and `bytesRead` are
lines 174--175; the realloc, null test, copy, and increment are lines
177--185; `rtv`, `free(dataPtr)`, and the successful return are lines
190--194. The four logged failure paths belong to lines 202, 207, 212, and
217, and their shared null return is line 220. This rules out candidates that
give the receive VLA a separate lifetime.

The parser call itself uses the target's observed two-register ABI:
`extractHTTPResponse(dataPtr, totBytes)` receives `dataPtr` in `EAX` and the
byte count in `EDX`, consistent with a GCC `regparm(2)` declaration. A scoped
candidate with that declaration reproduces the 594-byte extent, all external
relocation targets, the VLA layout, and the receive loop. It is still not
admitted: its stack-alignment filler after `gethostbyname` is `push %ebx`,
where the oracle has `push %ecx`. Candidates that reproduce the latter
instruction rearrange the failure blocks and differ elsewhere. This one-byte
difference is retained as a source-form constraint, never normalized or
patched.

The cold-block layout provides one further scope check. In the oracle, the
send-failure handler calls `getSocketError` and `log2file` before the saved
variable-length stack pointer is restored at the shared exit. A candidate that
uses labels outside the VLA scope emits that restore before `getSocketError`;
it is rejected even though it has the same error messages and total transport
behavior. The source must keep that handler within the VLA lifetime while also
producing the oracle's cold-block ordering.

This map gives the next implementation a closed evidence boundary: recover the
entire unit from the executable oracle and its DWARF, then compile and compare
it as `game-httpget`. Do not replace it with a modern HTTP client, a stub, or
the original program code.

The current `game-httpget` TDM-2 build verifies seven of the ten historical
functions as `FUNCTION_MATCH`: `httpGetLastModified` (126 bytes),
`destroyHTTPResponse` (116), `SplitURL` (267), `getSocketError` (12),
`HTTPRequest` (136), `HTTPHead` (27), and `HTTPGet` (27). The comparison
resolves all five `free` calls, the URL parser's `strptime`/`timegm` calls, the
URL parsing helper's allocator and string-library calls, the Winsock tail
jump, each unique method literal, the original failure string, and every
request-helper call independently. Its 714-byte partial text cannot
establish a complete-CU match; the full record is
in `docs/experiments/game-httpget-O2.json`.
