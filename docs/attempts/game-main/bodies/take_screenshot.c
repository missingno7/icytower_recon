void take_screenshot(BITMAP *bmp)
{
    static int number;
    PALETTE p;
    BITMAP *b;
    char buf[256];
    int found;

    for (;;) {
        sprintf(buf, "screenshots/icytower_%04d.png", number++);
        found = exists(buf);
        if (number > 9999) {
            log2file("*** Too many screenshots in the screenshot folder! Delete some and try again.");
            return;
        }
        if (!found)
            break;
    }
    get_palette(p);
    b = create_sub_bitmap(bmp, 0, 0, bmp->w, bmp->h);
    save_bitmap(buf, b, p);
    destroy_bitmap(b);
    while (key[KEY_F1])
        ;
}
