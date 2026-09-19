/* Synthetic link entry only. This is not a reconstructed game entry point. */
extern int logg_get_buffer_size(void);

/* The partial main CU references UI loading progress; this probe never runs. */
void draw_progress_bar(void)
{
}

/* Menu sound mixing belongs to the still-partial main CU; this probe never runs. */
void play_sound(void *sound, int randomized, int panned)
{
}

int main(void)
{
    return logg_get_buffer_size() == 65536 ? 0 : 1;
}
