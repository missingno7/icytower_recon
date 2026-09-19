/* Synthetic link entry only. This is not a reconstructed game entry point. */
extern int logg_get_buffer_size(void);

/* The partial main CU references UI loading progress; this probe never runs. */
void draw_progress_bar(void)
{
}

int main(void)
{
    return logg_get_buffer_size() == 65536 ? 0 : 1;
}
