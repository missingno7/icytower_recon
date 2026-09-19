/* Historical CU: F:\projects\icytower\trunk\source\httpget.c
 * Ownership: AMBIGUOUS. Only functions independently recovered from the
 * executable oracle are emitted here; the remaining historical bodies are
 * deliberately absent.
 */
#include <winsock2.h>
#include <stdlib.h>
#include <string.h>

typedef struct HTTPHeader {
    char *pHeader;
    char *pValue;
} HTTPHeader;

typedef struct HTTPResponse {
    int iStatusCode;
    unsigned int iNumHeaders;
    HTTPHeader *pHeaders;
    unsigned char *pPayload;
    unsigned int iPayloadSize;
} HTTPResponse;

HTTPResponse *HTTPRequest(char *pURL, char *pMethod);
int SplitURL(char *pURL, char **ppHost, char **ppPath, int *piPort);
HTTPResponse *HTTPFetchInternal(char *pHost, int iPort, char *pPathToFile,
                                char *pMethod);
void log2file(char *fmt, ...);

int SplitURL(char *pURL, char **ppHost, char **ppPath, int *piPort)
{
    char *p;

    *ppHost = NULL;
    *ppPath = NULL;
    *piPort = 80;
    if (!strncmp(pURL, "http://", 7))
        pURL += 7;
    p = pURL;
    while (*p) {
        if (*p == ':' || *p == '/') {
            int iHostLen = p - pURL;

            *ppHost = malloc(iHostLen + 1);
            memcpy(*ppHost, pURL, iHostLen);
            (*ppHost)[iHostLen] = 0;
            if (*p == ':')
                *piPort = strtol(p, &p, 10);
            *ppPath = strdup(p);
            return 1;
        }
        p++;
    }
    free(*ppHost);
    free(*ppPath);
    return 0;
}

void destroyHTTPResponse(HTTPResponse *pResponse)
{
    if (pResponse) {
        int i;

        for (i = 0; i < pResponse->iNumHeaders; i++) {
            free(pResponse->pHeaders[i].pHeader);
            free(pResponse->pHeaders[i].pValue);
        }
        free(pResponse->pHeaders);
        free(pResponse->pPayload);
        free(pResponse);
    }
}

int getSocketError(void)
{
    return WSAGetLastError();
}

HTTPResponse *HTTPHead(char *pURL)
{
    return HTTPRequest(pURL, "HEAD");
}

HTTPResponse *HTTPGet(char *pURL)
{
    return HTTPRequest(pURL, "GET");
}

HTTPResponse *HTTPRequest(char *pURL, char *pMethod)
{
    char *pHost;
    char *pPath;
    int iPort;

    if (SplitURL(pURL, &pHost, &pPath, &iPort)) {
        HTTPResponse *pResponse = HTTPFetchInternal(pHost, iPort, pPath,
                                                     pMethod);
        free(pHost);
        free(pPath);
        return pResponse;
    }

    log2file("Could not split URL \"%s\"", pURL);
    return NULL;
}
