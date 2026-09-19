/* Historical CU: F:\projects\icytower\trunk\source\hisc.c
 * Ownership: GAME
 * UNKNOWN: qualify_hisc_table @ 0x00404994, 39 bytes
 * UNKNOWN: sort_hisc_table @ 0x004049bc, 147 bytes
 * UNKNOWN: generate_checksum @ 0x00404a50, 44 bytes
 * UNKNOWN: draw_table @ 0x00404a7c, 441 bytes
 * UNKNOWN: view_scores @ 0x00404c38, 2552 bytes
 * UNKNOWN: save_hisc_table @ 0x00405630, 129 bytes
 * UNKNOWN: load_hisc_table @ 0x004056b4, 155 bytes
 * UNKNOWN: reset_hisc_table @ 0x00405750, 64 bytes
 * UNKNOWN: enter_hisc_table @ 0x00405790, 136 bytes
 * UNKNOWN: make_hisc_table @ 0x0040583c, 84 bytes
 */

typedef struct {
    char name[32];
    void *posts;
} Thisc_table;

extern void free(void *ptr);

void destroy_hisc_table(Thisc_table *table)
{
    free(table->posts);
    free(table);
}
