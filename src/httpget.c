/* Historical CU: F:\projects\icytower\trunk\source\httpget.c
 * Ownership: AMBIGUOUS. Only functions independently recovered from the
 * executable oracle are emitted here; the remaining historical bodies are
 * deliberately absent.
 */
#include <winsock2.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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
char *strptime(const char *s, const char *format, struct tm *tm);
time_t timegm(struct tm *tm);

time_t httpGetLastModified(HTTPResponse *pResponse)
{
    if (pResponse) {
        int i;

        for (i = 0; i < pResponse->iNumHeaders; i++) {
            if (!strcmp(pResponse->pHeaders[i].pHeader, "Last-Modified")) {
                struct tm stm;

                strptime(pResponse->pHeaders[i].pValue,
                         "%a, %e %b %Y %H:%M:%S", &stm);
                return timegm(&stm);
            }
        }
    }
    return 0;
}

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

/* The parser's historical call ABI passes its two arguments in EAX and EDX.
 * The transport is source-recovered but remains a code-generation DIFFER. */
HTTPResponse *__attribute__((regparm(2))) extractHTTPResponse(char *pHTTPData,
                                                                int iResponseBytesCount);

HTTPResponse *HTTPFetchInternal(char *pHost, int iPort, char *pPathToFile,
                                char *pMethod)
{
    register char *dataPtr = malloc(1);
    int sBufferSize = 512;
    int rBufferSize = 1024;
    SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);

    if (sock != INVALID_SOCKET) {
        struct timeval tv;
        struct hostent *host;

        tv.tv_sec = 5;
        setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (char *)&tv, sizeof(tv));
        host = gethostbyname(pHost);
        if (host) {
            struct sockaddr_in service;

            service.sin_family = AF_INET;
            service.sin_addr.s_addr = *(unsigned long *)host->h_addr_list[0];
            service.sin_port = htons(iPort);
            if (connect(sock, (struct sockaddr *)&service, sizeof(service)) != SOCKET_ERROR) {
                char sendbuff[sBufferSize];

                sprintf(sendbuff, "GET /%s HTTP/1.1\r\nHost: %s\r\n\r\n",
                        pPathToFile, pHost);
                char recvbuff[rBufferSize];
                if (send(sock, sendbuff, strlen(sendbuff), 0) != SOCKET_ERROR) {
                    int totBytes = 0;
                    int bytesRead;

                    while ((bytesRead = recv(sock, recvbuff, rBufferSize, 0)) > 0) {
                        dataPtr = realloc(dataPtr, totBytes + bytesRead);
                        if (!dataPtr) {
                            log2file(">>> HTTP: Failed to allocate %d bytes for http response",
                                     totBytes + bytesRead);
                            free(NULL);
                            return NULL;
                        }
                        memcpy(dataPtr + totBytes, recvbuff, bytesRead);
                        totBytes += bytesRead;
                    }
                    {
                        HTTPResponse *rtv = extractHTTPResponse(dataPtr, totBytes);

                        free(dataPtr);
                        closesocket(sock);
                        return rtv;
                    }
                }
                log2file(">>> HTTP:  Sending data failed: %d\n", getSocketError());
                return NULL;
            }
            log2file(">>> HTTP:  Failed to connect to service: %d\n", getSocketError());
            return NULL;
        }
        log2file(">>> HTTP:  Host lookup failed: %s\n", pHost);
        return NULL;
    }
    log2file(">>> HTTP:  Socket creation failed: %d\n", getSocketError());
    return NULL;
}
