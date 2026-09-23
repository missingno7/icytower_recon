Treplay *load_replay(const char *filename)
{
    void *pf;
    Treplay r_temp;
    Treplay *r;
    int i;
    int sum;
    int cs;

    pf = pack_fopen(filename, "rb");
    if (!pf)
        return 0;
    pack_fread(r_temp.header, 6, pf);
    pack_fread(&r_temp.size, 4, pf);
    pack_fclose(pf);
    if (memcmp(r_temp.header, replay_header, 6))
        return 0;
    r = create_replay(r_temp.size);
    if (!r)
        return 0;
    pf = pack_fopen(filename, "rb");
    if (!pf)
        goto error;
    pack_fread(r->header, 6, pf);
    pack_fread(&r->size, 4, pf);
    pack_fread(r->name, 32, pf);
    pack_fread(r->date, 32, pf);
    pack_fread(&r->score, 4, pf);
    pack_fread(&r->floor, 4, pf);
    pack_fread(&r->combo, 4, pf);
    pack_fread(&r->no_combo_top_floor, 4, pf);
    pack_fread(&r->biggest_lost_combo, 4, pf);
    for (i = 0; i < 20; i += 4)
        pack_fread((char *)r->ccc + i, 4, pf);
    for (i = 0; i < 20; i += 4)
        pack_fread((char *)r->jc + i, 4, pf);
    pack_fread(&r->floor_shrink, 4, pf);
    pack_fread(&r->floor_size, 4, pf);
    pack_fread(&r->start_speed, 4, pf);
    pack_fread(&r->speed_increase, 4, pf);
    pack_fread(&r->gravity, 4, pf);
    pack_fread(&r->rejump, 4, pf);
    pack_fread(&r->random_seed, 4, pf);
    pack_fread(r->comment, 42, pf);
    pack_fread(&r->checksum, 4, pf);
    pack_fread(&r->tc_posts, 4, pf);
    for (i = 0; i < 100; i++) {
        pack_fread(&r->tc_c_data[i], 4, pf);
        pack_fread(&r->tc_q_data[i], 4, pf);
        pack_fread(&r->tc_t_data[i], 4, pf);
        pack_fread(&r->tc_s_data[i], 4, pf);
        pack_fread(&r->tc_f_data[i], 4, pf);
    }
    for (i = 0; i < r->size; i++) {
        pack_fread(&r->data[i].cycle_count, 4, pf);
        pack_fread(&r->data[i].key_flags, 1, pf);
    }
    pack_fclose(pf);
    cs = r->checksum;
    r->checksum = 0;
    sum = calc_replay_checksum(r);
    if (cs == sum)
        return r;
    log2file("Checksum failed for %s: got %d, expected %d", filename, sum, cs);
error:
    destroy_replay(r);
    return 0;
}
