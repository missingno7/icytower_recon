/* Historical CU: F:\projects\icytower\trunk\source\hisc.c
 * Ownership: GAME
 * UNKNOWN: draw_table @ 0x00404a7c, 441 bytes
 * UNKNOWN: view_scores @ 0x00404c38, 2552 bytes
 * UNKNOWN: save_hisc_table @ 0x00405630, 129 bytes
 * UNKNOWN: load_hisc_table @ 0x004056b4, 155 bytes
 * UNKNOWN: enter_hisc_table @ 0x00405790, 136 bytes
 */

typedef struct {
    char name[32];
    unsigned int value;
} Thisc_post;

typedef struct {
    char name[32];
    Thisc_post *posts;
} Thisc_table;

extern void free(void *ptr);
extern void *malloc(unsigned int size);
extern char *strcpy(char *dst,const char *src);

void destroy_hisc_table(Thisc_table *table)
{
    free(table->posts);
    free(table);
}

Thisc_table *make_hisc_table(char *name)
{
    Thisc_table *table;

    table=malloc(sizeof(Thisc_table));
    if (table) {
        table->posts=malloc(180);
        if (table->posts) {
            strcpy(table->name,name);
            return table;
        }
    }
    return 0;
}

void reset_hisc_table(Thisc_table *table,char *name,int hi,int lo)
{
    int i;
    int d;

    for (i=0;i<5;i++) {
        strcpy(table->posts[i].name,name);
        table->posts[i].value=0;
    }
}

int generate_checksum(Thisc_post *entry)
{
    int i;
    char *s;

    i=entry->value;
    s=entry->name;
    while (*s) {
        i=i*140+*s;
        s++;
    }
    return i;
}

int qualify_hisc_table(Thisc_table *table,int value)
{
    int i;

    if (value)
        for (i=0;i<5;i++)
            if (table->posts[i].value<value) return i+1;
    return 0;
}

void sort_hisc_table(Thisc_table *table)
{
    int i,j;
    Thisc_post post;

    for (i=1;i<5;i++) {
        post=table->posts[i];
        for (j=i;j>0 && table->posts[j-1].value<post.value;j--)
            table->posts[j]=table->posts[j-1];
        table->posts[j]=post;
    }
}
