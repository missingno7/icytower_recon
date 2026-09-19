#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* Partial historical replay.c recovery.
 * Ownership: GAME.
 *
 * The remaining functions below are still pending reconstruction:
 * PARTIAL: calc_replay_checksum_131 @ 0x0041ba10, 177 bytes
 * DIFFER: calc_replay_checksum @ 0x0041bac4, 676 bytes
 * EXACT: update_file_list @ 0x0041bda0, 184 bytes
 * UNKNOWN: draw_replay_selector @ 0x0041be58, 3726 bytes
 * DIFFER: create_replay @ 0x0041cce8, 254 bytes
 * UNKNOWN: load_replay @ 0x0041cde8, 1136 bytes
 * UNKNOWN: replay_selector @ 0x0041d258, 2845 bytes
 * UNKNOWN: save_replay @ 0x0041dd78, 1227 bytes
 * UNKNOWN: get_replay_property @ 0x0041e244, 1147 bytes
 * UNKNOWN: my_strcmp @ 0x0041e6c0, 128 bytes
 * DIFFER: add_itr_file @ 0x0041e740, 360 bytes
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
extern char *get_filename(const char *path);
extern char *get_extension(const char *path);
#ifndef FA_DIREC
#define FA_DIREC 0x10
#endif

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

int calc_replay_checksum(Treplay *r)
{
    int i;
    int sum;

    sum = (r->biggest_lost_combo * 17 + r->no_combo_top_floor * 127) * 2;
    sum += r->floor_shrink * 102 + r->floor_size * 17 + 3702;
    sum += r->start_speed * 163 + r->speed_increase * 23;
    sum += r->gravity * 88 + r->random_seed * 329;
    sum += r->tc_posts * 127 + r->rejump * 13;
    sum += r->score * 17 + 17;
    sum += (r->combo + 1) * 649;
    sum += (r->floor + 1) * 113;
    for (i = 0; i < 5; i++)
        sum += r->ccc[i] * (39 + i * 3) + r->jc[i] * (27 + i * 3);
    for (i = 0; i < 100; i++) {
        sum += r->tc_c_data[i] * ((i + 1) % 13);
        sum += r->tc_q_data[i] * ((i + 6) % 17);
        sum += r->tc_t_data[i] * ((i + 8) % 23);
    }
    for (i = 0; i < 32; i++)
        sum += (r->date[i] + i) * (r->name[i] + i) * (17 + i * 17);
    for (i = 0; i < 42; i++)
        sum += (r->comment[i] + i) * (r->comment[i] + i) * (-3 + i * 3);
    for (i = 0; i < r->size; i++)
        sum += r->data[i].type * 3 * (i % 193 + 1) +
               r->data[i].value * 7 * (i % 167 + 1);
    return hash(sum);
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

int add_itr_file(const char *filename, int attrib, void *param)
{
    int length;
    char *name;
    int res;

    length = strlen(filename) + 10;
    name = get_filename(filename);
    if (!stricmp(name, "."))
        goto done;
    if (!(attrib & FA_DIREC))
        goto replay_file;
    goto directory;
replay_file:
    if (stricmp(get_extension(filename), "itr"))
        goto done;
    itr_file_list[num_itr_files].full_path = malloc(length);
    res = get_replay_property(filename, 0);
    if (res < 0)
        goto bad_replay;
copy_replay:
    strcpy(itr_file_list[num_itr_files].full_path, filename);
    itr_file_list[num_itr_files].directory = 0;
    num_itr_files++;
done:
    return 0;
directory:
    itr_file_list[num_itr_files].full_path = malloc(length);
    strcpy(itr_file_list[num_itr_files].full_path, filename);
    itr_file_list[num_itr_files].directory = 1;
    if (!strncmp(name, "..", 3))
        itr_file_list[num_itr_files].parent = 1;
    num_itr_files++;
    goto done;
bad_replay:
    if (res == -1 || res == -1000)
        goto done;
    itr_file_list[num_itr_files].version = -1000 - res;
    goto copy_replay;
}

Treplay *create_replay(int size)
{
    Treplay *r;
    int i;

    r = malloc(sizeof(Treplay));
    if (!r)
        return 0;
    strncpy(r->header, "ITR140", 6);
    r->comment[0] = 0;
    r->size = size;
    r->combo = 0;
    r->floor = 0;
    r->score = 0;
    for (i = 0; i < 32; i++)
        r->name[i] = 0;
    for (i = 0; i < 32; i++)
        r->name[i] = 0;
    strcpy(r->name, "replay");
    strcpy(r->date, "no date");
    r->data = malloc(size * sizeof(Treplay_data) + 32);
    if (!r->data) {
        free(r);
        return 0;
    }
    for (i = 0; i < size; i++) {
        r->data[i].type = 0;
        r->data[i].value = 0;
    }
    return r;
}
