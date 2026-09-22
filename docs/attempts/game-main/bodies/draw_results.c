void draw_results(BITMAP *bmp, BITMAP *logo, int y, int *qualified,
                  int *qValues, int showQ)
{
    int categories[5] = { 0, 2, 1 };
    int numCats = 3;
    int padding = 30;
    int dist;
    int pos = 0;
    int i;

    draw_sprite(bmp,logo,320-logo->w/2,y);
    for (i=0; i<numCats; i++) {
        textprintf_ex(bmp,data[52].dat,200,y+logo->h+3+pos,-1,-1,"%s:",
                      result_categories[categories[i]]);
        textprintf_right_ex(bmp,data[52].dat,440,y+logo->h+3+pos,-1,-1,"%d",
                            qValues[categories[i]]);
        if (showQ) {
            if (new_personal_best[categories[i]]>0 &&
                stricmp(profile->handle,"guest")) {
                draw_sprite(bmp,data[69].dat,476,y+logo->h+13+pos);
                dist = 18;
            }
            else
                dist = -4;
            if (qualified[categories[i]]>0) {
                draw_sprite(bmp,data[68].dat,480+dist,y+logo->h+13+pos);
                textprintf_ex(bmp,data[53].dat,480+dist+7,y+logo->h+18+pos,
                              makecol(0,0,0),-1,"%d",qualified[categories[i]]);
            }
        }
        pos += padding;
    }
}
