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
