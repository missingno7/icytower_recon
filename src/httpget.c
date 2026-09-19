/* Historical CU: F:\projects\icytower\trunk\source\httpget.c
 * Ownership: AMBIGUOUS. Only functions independently recovered from the
 * executable oracle are emitted here; the remaining historical bodies are
 * deliberately absent.
 */
#include <winsock2.h>

typedef struct HTTPResponse HTTPResponse;

HTTPResponse *HTTPRequest(char *pURL, char *pMethod);

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
