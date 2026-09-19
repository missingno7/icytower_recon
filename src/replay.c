#include <stdio.h>

/* Partial historical replay.c recovery.
 * Ownership: GAME.
 *
 * The remaining functions below are still pending reconstruction:
 * PARTIAL: calc_replay_checksum_131 @ 0x0041ba10, 177 bytes
 * UNKNOWN: calc_replay_checksum @ 0x0041bac4, 676 bytes
 * UNKNOWN: update_file_list @ 0x0041bda0, 184 bytes
 * UNKNOWN: draw_replay_selector @ 0x0041be58, 3726 bytes
 * UNKNOWN: create_replay @ 0x0041cce8, 254 bytes
 * UNKNOWN: load_replay @ 0x0041cde8, 1136 bytes
 * UNKNOWN: replay_selector @ 0x0041d258, 2845 bytes
 * UNKNOWN: save_replay @ 0x0041dd78, 1227 bytes
 * UNKNOWN: get_replay_property @ 0x0041e244, 1147 bytes
 * UNKNOWN: my_strcmp @ 0x0041e6c0, 128 bytes
 * UNKNOWN: add_itr_file @ 0x0041e740, 360 bytes
 */

int sort_method;

int get_sort_method(void) { return sort_method; }

void set_sort_method(int sm) { sort_method = sm; }

unsigned int hash(unsigned int a)
{
    a = (a ^ 0x3dU) ^ (a >> 16);
    a *= 9U;
    a ^= a >> 4;
    a *= 668265261U;
    a ^= a >> 15;
    return a;
}

typedef struct Treplay_post {
    char *full_path;
    char directory;
    char parent;
    char reserved[2];
    int version;
    int score;
    int floor;
    int combo;
} Treplay_post;

extern int stricmp(const char *a, const char *b);
extern int get_replay_property(const char *file_name, int property);
extern int for_each_file_ex(const char *pattern, int in_attrib, int out_attrib,
                            int (*callback)(const char *, int, void *), void *param);
extern int add_itr_file(const char *filename, int attrib, void *param);
extern void qsort(void *base, size_t count, size_t size,
                  int (*compare)(const void *, const void *));

Treplay_post itr_file_list[1024];
int num_itr_files;

typedef struct Treplay_data {
    unsigned char type;
    char reserved[3];
    int value;
} Treplay_data;

typedef struct Treplay {
    char header[6];
    int size;
    char name[32];
    char date[32];
    int checksum;
    int score;
    int floor;
    int combo;
    int no_combo_top_floor;
    int biggest_lost_combo;
    int ccc[5];
    int jc[5];
    int floor_shrink;
    int floor_size;
    int start_speed;
    int speed_increase;
    int gravity;
    int rejump;
    int random_seed;
    char comment[42];
    int tc_posts;
    float tc_c_data[100];
    float tc_q_data[100];
    float tc_t_data[100];
    float tc_s_data[100];
    float tc_f_data[100];
    Treplay_data *data;
} Treplay;

extern void free(void *ptr);

void destroy_replay(Treplay *r)
{
    if (r) {
        if (r->data) free(r->data);
        free(r);
    }
}

int calc_replay_checksum_131(Treplay *r)
{
    int i;
    int sum;

    sum = r->random_seed * 17;
    sum += r->rejump * 26;
    sum += (r->score + 1) * 7;
    sum += (r->floor + 1) * 13;
    sum += (r->combo + 1) * 23;
    for (i = 0; i < 32; i++)
        sum += (r->date[i] + i) * (r->name[i] + i) * (i + 1) * 117;
    for (i = 0; i < r->size; i++)
        sum += (r->data[i].type * 5 + r->data[i].value * 3) * i;
    return sum;
}

int my_strcmp(const void *c, const void *d)
{
    Treplay_post *a;
    Treplay_post *b;
    int av, bv;

    a = (Treplay_post *)c;
    b = (Treplay_post *)d;
    if (a->directory != b->directory) {
        if (a->directory)
            return -1;
        return 1;
    }
    if (!a->directory && sort_method >= 2 && sort_method <= 4) {
        av = get_replay_property(a->full_path, sort_method);
        bv = get_replay_property(b->full_path, sort_method);
        if (av > bv)
            return -1;
        return 1;
    }
    return stricmp(a->full_path, b->full_path);
}

void update_file_list(char *path)
{
    int i;
    char full_path[1024];

    for (i = 0; i < num_itr_files; i++) {
        free(itr_file_list[i].full_path);
        itr_file_list[i].parent = 0;
        itr_file_list[i].directory = 0;
    }
    num_itr_files = 0;
    sprintf(full_path, "%s/*", path);
    for_each_file_ex(full_path, 0, 0, add_itr_file, 0);
    qsort(itr_file_list, num_itr_files, sizeof(Treplay_post), my_strcmp);
}
