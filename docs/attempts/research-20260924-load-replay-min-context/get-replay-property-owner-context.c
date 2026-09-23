int get_replay_property(const char *filename, int property)
{
    void *pf;
    Treplay r_temp;
    Treplay *r;
    int i;
    int retval;

    pf = pack_fopen(filename, "rb");
    if (!pf) {
        log2file("Couldn't open %s", filename);
        return 0;
    }
    pack_fread(r_temp.header, 6, pf);
    pack_fread(&r_temp.size, 4, pf);
    pack_fclose(pf);
    if (memcmp(r_temp.header, replay_header, 3)) {
        log2file("%s has wrong first 3 bytes of header", filename);
        return -1000;
    }
    if (r_temp.header[3] != '1' || r_temp.header[4] != '4' ||
        r_temp.header[5] != '0') {
        log2file("%s has wrong header version", filename);
        if (r_temp.header[3] == '0' && r_temp.header[4] == '0' &&
            r_temp.header[5] == '1')
            return -1001;
        if (r_temp.header[3] == '1' && r_temp.header[4] == '3' &&
            r_temp.header[5] == '0')
            return -1130;
        return -1000;
    }
    r = create_replay(r_temp.size);
    if (!r) {
        log2file("Couldn't create a replay object");
        return -1;
    }
    pf = pack_fopen(filename, "rb");
    if (!pf) {
        log2file("Can't open %s", filename);
        destroy_replay(r);
        return -1;
    }
    pack_fread(r->header, 6, pf);
    pack_fread(&r->size, 4, pf);
    pack_fread(r->name, 32, pf);
    pack_fread(r->date, 32, pf);
    pack_fread(&r->score, 4, pf);
    pack_fread(&r->floor, 4, pf);
    pack_fread(&r->combo, 4, pf);
    pack_fread(&r->no_combo_top_floor, 4, pf);
    pack_fread(&r->biggest_lost_combo, 4, pf);
    for (i = 0; i < 5; i++)
        pack_fread(&r->ccc[i], 4, pf);
    for (i = 0; i < 5; i++)
        pack_fread(&r->jc[i], 4, pf);
    pack_fread(&r->floor_shrink, 4, pf);
    pack_fread(&r->floor_size, 4, pf);
    pack_fread(&r->start_speed, 4, pf);
    pack_fread(&r->speed_increase, 4, pf);
    pack_fread(&r->gravity, 4, pf);
    pack_fclose(pf);
    retval = 0;
    switch (property) {
    case 2:
        retval = r->score;
        log2file("%s:score=%d", filename, retval);
        break;
    case 4:
        retval = r->floor;
        log2file("%s:floor=%d", filename, retval);
        break;
    case 3:
        retval = r->combo;
        log2file("%s:combo=%d", filename, retval);
        break;
    }
    destroy_replay(r);
    return retval;
}