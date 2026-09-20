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
HTTPResponse *HTTPFetchInternal(const char *pHost, int iPort, const char *pPathToFile,
                                const char *pMethod);
void log2file(char *fmt, ...);
char *strptime(const char *s, const char *format, struct tm *tm);
time_t timegm(struct tm *tm);

int getSocketError(void)
{
    return WSAGetLastError();
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

static inline int extractLine(char *pBuffer, int iDataLeft, char *pOutBuffer,
                              int iOutSize)
{
    int bytesRead = 0;
    char last = 0;

    pOutBuffer[0] = 0;
    while (iDataLeft - bytesRead > 0) {
        char c = pBuffer[bytesRead++];

        if (c == '\n' && last == '\r')
            break;
        if (c != '\r') {
            *pOutBuffer++ = c;
            *pOutBuffer = 0;
            if (--iOutSize == 1)
                break;
        }
        last = c;
    }
    pOutBuffer[--iOutSize] = 0;
    return bytesRead;
}

HTTPResponse *__attribute__((regparm(2))) extractHTTPResponse(char *pHTTPData,
                                                                int iResponseBytesCount)
{
    char slaskbuf[1024];
    char linebuf[1024];
    int i;
    HTTPResponse *pResponse = malloc(sizeof(HTTPResponse));

    memset(pResponse, 0, sizeof(HTTPResponse));
    i = extractLine(pHTTPData, iResponseBytesCount, linebuf, sizeof(linebuf));
    if (sscanf(linebuf, "HTTP/%s %d", slaskbuf, &pResponse->iStatusCode) != 2) {
        log2file("Malformed HTTP response:\n%s", pHTTPData);
        destroyHTTPResponse(pResponse);
        return NULL;
    }

    while (1) {
        int bytesRead = extractLine(pHTTPData + i, iResponseBytesCount - i,
                                    linebuf, sizeof(linebuf));
        HTTPHeader *header;
        int j;

        i += bytesRead;
        if (bytesRead == 2)
            break;
        pResponse->iNumHeaders++;
        pResponse->pHeaders = realloc(pResponse->pHeaders,
                                      pResponse->iNumHeaders * sizeof(HTTPHeader));
        header = &pResponse->pHeaders[pResponse->iNumHeaders - 1];
        if (linebuf[0] == ':') {
            j = 0;
        } else {
            for (j = 1; j < bytesRead; j++) {
                if (linebuf[j] == ':')
                    break;
            }
        }
        header->pHeader = malloc(j + 1);
        memcpy(header->pHeader, linebuf, j);
        header->pHeader[j] = 0;
        header->pValue = malloc(bytesRead - j - 1);
        memcpy(header->pValue, linebuf + j + 2, bytesRead - j - 2);
        header->pValue[bytesRead - j - 2] = 0;
    }

    pResponse->iPayloadSize = iResponseBytesCount - i;
    if (pResponse->iPayloadSize) {
        pResponse->pPayload = malloc(pResponse->iPayloadSize + 1);
        memcpy(pResponse->pPayload, pHTTPData + i, pResponse->iPayloadSize);
        pResponse->pPayload[pResponse->iPayloadSize] = 0;
    }
    return pResponse;
}

HTTPResponse *HTTPFetchInternal(const char *pHost, int iPort, const char *pPathToFile,
                                const char *pMethod)
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

HTTPResponse *HTTPGet(char *pURL)
{
    return HTTPRequest(pURL, "GET");
}

/* The line reader was inlined twice into extractHTTPResponse in the original
 * object. It returns consumed input bytes while omitting CR/LF from output. */
HTTPResponse *HTTPHead(char *pURL)
{
    return HTTPRequest(pURL, "HEAD");
}

/* The parser's historical call ABI passes its two arguments in EAX and EDX. */
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
