/* Synthetic link entry only. This is not a reconstructed game entry point. */
extern int logg_get_buffer_size(void);
int main(void)
{
    return logg_get_buffer_size() == 65536 ? 0 : 1;
}
