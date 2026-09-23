int draw_buffer(BITMAP *bmp, char *buffer, int x, int y)
{
    int pos;
    char tempBuf[256];
    int tempPos;

    pos = y;
    tempPos = 0;
    while (*buffer) {
        if (*buffer == '\n') {
            tempBuf[tempPos] = 0;
            textprintf_ex(bmp, data[53].dat, x, pos, makecol(30, 20, 10),
                          -1, "%s", tempBuf);
            pos += 10;
            tempPos = 0;
        } else {
            tempBuf[tempPos] = *buffer;
            tempPos++;
        }
        buffer++;
    }
    return pos;
}
