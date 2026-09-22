/* Reconstruction of dumpHTTPResponse() (historical httpget.c lines 48..53, 99 bytes at 0x405e2c).
 * Line table: 48 prologue, 49 fprintf, 50 loop guard + back edge, 51 fprintf, 53 epilogue.
 * The back edge compares with `ja`, an UNSIGNED compare, because iNumHeaders is `unsigned int`
 * and the usual arithmetic conversions make the `int i` comparison unsigned.  The element address
 * is `shl $0x3` + pHeaders (HTTPHeader is 8 bytes: char *pHeader @0, char *pValue @4), and the
 * two loaded members are at +0 and +4.  DWARF lexical block 80170 (0x405e51..0x405e87) owns `i`,
 * so the declaration lives in a brace block of its own rather than at function scope. */
void dumpHTTPResponse(FILE *pOut, HTTPResponse *pResponse)
{
    fprintf(pOut, "HTTP/1.1 %d\n", pResponse->iStatusCode);
    {
        int i;

        for (i = 0; i < pResponse->iNumHeaders; i++) {
            fprintf(pOut, "%s: %s\n", pResponse->pHeaders[i].pHeader,
                    pResponse->pHeaders[i].pValue);
        }
    }
}
