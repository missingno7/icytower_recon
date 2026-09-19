/* Historical CU: F:\projects\icytower\trunk\source\game_data.c
 * Ownership: GAME
 * Partial source recovery.
 * UNKNOWN: getGameDataXML @ 0x00404254, 1855 bytes
 */

typedef struct { int start, end, length; } Tgd_combo;
typedef struct { int start, dist, num; } Tgd_jump_sequence;

typedef struct {
    void *replay;
    int score, floor, combo, no_combo_top_floor, biggest_lost_combo;
    int ccc[5], jc[5];
    int comboPosts;
    Tgd_combo combos[5000];
    int jumpPosts;
    Tgd_jump_sequence jumps[5000];
    int left, right, jump;
} Tgame_data;

extern void free(void *ptr);
extern void *malloc(unsigned int size);

void add_jump_sequence(Tgame_data *gd,Tgd_jump_sequence *js)
{
    if (js->num && gd->jumpPosts<5000) {
        gd->jumps[gd->jumpPosts].num=js->num;
        gd->jumps[gd->jumpPosts].dist=js->dist;
        gd->jumps[gd->jumpPosts].start=js->start;
        gd->jumpPosts++;
    }
}

void add_combo(Tgame_data *gd,Tgd_combo *c)
{
    if (gd->comboPosts<5000) {
        gd->combos[gd->comboPosts].end=c->end;
        gd->combos[gd->comboPosts].start=c->start;
        gd->combos[gd->comboPosts].length=c->length;
        gd->comboPosts++;
    }
}

void destroy_game_data(void *gd) { free(gd); }

Tgame_data *create_game_data(void)
{
    int i;
    Tgame_data *gd;

    gd=malloc(sizeof(Tgame_data));
    if (gd) {
        gd->replay=0;
        gd->score=gd->floor=gd->combo=gd->no_combo_top_floor=gd->biggest_lost_combo=0;
        for (i=0;i<5;i++) gd->ccc[i]=gd->jc[i]=0;
        gd->comboPosts=0;
        gd->jumpPosts=0;
        gd->left=gd->right=gd->jump=0;
    }
    return gd;
}
