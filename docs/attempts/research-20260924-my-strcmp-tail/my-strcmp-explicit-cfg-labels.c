int my_strcmp(const void *c, const void *d)
{
    Treplay_post *a;
    Treplay_post *b;
    int av, bv;

    a = (Treplay_post *)c;
    b = (Treplay_post *)d;
    if (a->directory != b->directory)
        goto directory_order;
    if (a->directory == 0)
        goto property_order;

path_order:
    return stricmp(a->full_path, b->full_path);

property_order:
    if ((unsigned int)(sort_method - 2) > 2U)
        goto path_order;
    av = get_replay_property(a->full_path, sort_method);
    bv = get_replay_property(b->full_path, sort_method);
    if (av > bv)
        return -1;
    return 1;

directory_order:
    if (a->directory != 1)
        return 1;
    return -1;
}
