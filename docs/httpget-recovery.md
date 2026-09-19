# `httpget.c` recovery map

`src/httpget.c` remains recovery-owned. The historical compilation unit spans
`0x405890` through `0x4061af` in the original executable. Five independently
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
headers, or no matching header returns zero.

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
a TCP socket, applies a five-second send timeout, resolves the host, connects,
formats the fixed `"GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n"` request, sends it,
accumulates 1024-byte receives, parses the response, and closes the socket.
The fourth `HTTPRequest` argument is passed through as an additional fetch
argument, but has no observed use in this body; the `HEAD` wrapper therefore
preserves the original call shape without claiming a corrected request method.
Its error paths log the original socket errors. `SplitURL` and
`extractHTTPResponse` remain the larger recovery bodies (267 and 923 bytes),
with exact DWARF extents and oracle disassembly available.

This map gives the next implementation a closed evidence boundary: recover the
entire unit from the executable oracle and its DWARF, then compile and compare
it as `game-httpget`. Do not replace it with a modern HTTP client, a stub, or
the original program code.

The current `game-httpget` TDM-2 build verifies five of the ten historical
functions as `FUNCTION_MATCH`: `destroyHTTPResponse` (116 bytes),
`getSocketError` (12), `HTTPRequest` (136), `HTTPHead` (27), and `HTTPGet`
(27). The comparison resolves all five `free` calls, the Winsock tail jump,
each unique method literal, the original failure string, and every
request-helper call independently. Its 320-byte partial text cannot
establish a complete-CU match; the full record is
in `docs/experiments/game-httpget-O2.json`.
