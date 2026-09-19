/* Historical CU: F:\projects\icytower\trunk\source\profile.c
 * Ownership: GAME
 * Source recovery pending. This file intentionally defines no fallback code.
 * EXACT: hash2 @ 0x004189cc, 71 bytes
 * UNKNOWN: generate_profile_checksum @ 0x00418a14, 112 bytes
 * DIFFER: get_rank_id @ 0x00418a84, 75 bytes
 * DIFFER: get_rank @ 0x00418ad0, 82 bytes
 * UNKNOWN: set_next_rank_message @ 0x00418b24, 431 bytes
 * UNKNOWN: draw_profile_selector @ 0x00418cd4, 1268 bytes
 * UNKNOWN: draw_buffer @ 0x004191c8, 185 bytes
 * UNKNOWN: profile_data_page_advanced @ 0x00419284, 332 bytes
 * UNKNOWN: profile_data_page_basic @ 0x004193d0, 637 bytes
 * UNKNOWN: profile_data_page_extra @ 0x00419650, 85 bytes
 * UNKNOWN: profile_data_page_general @ 0x004196a8, 1091 bytes
 * UNKNOWN: view_profile @ 0x00419aec, 2249 bytes
 * UNKNOWN: save_profile @ 0x0041a3b8, 1073 bytes
 * UNKNOWN: load_profile @ 0x0041a7ec, 188 bytes
 * UNKNOWN: delete_profile @ 0x0041a8a8, 222 bytes
 * UNKNOWN: create_profile @ 0x0041a988, 823 bytes
 * UNKNOWN: select_profile @ 0x0041acc0, 3070 bytes
 */

unsigned int hash2(unsigned int a)
{
    a = (a ^ 0x3dU) ^ (a >> 16);
    a *= 9U;
    a ^= a >> 4;
    a *= 668265261U;
    a ^= a >> 15;
    return a;
}
typedef struct Tprofile_rank {
    unsigned char before_score[0x4c];
    int score;
    int combo;
    unsigned char before_ccc[4];
    int ccc;
    unsigned char before_nml[0x2c];
    int no_combo_lost;
} Tprofile_rank;

extern int rankFloors[16];
extern int rankCombos[16];
extern int rankCCCs[16];
extern int rankNMLs[16];
extern char *rankLables[16];

inline int get_rank_id(Tprofile_rank *profile)
{
    int i;

    for (i = 11; i >= 0; i--) {
        if (profile->score < rankFloors[i]) continue;
        if (profile->combo < rankCombos[i]) continue;
        if (profile->ccc < rankCCCs[i]) continue;
        if (profile->no_combo_lost < rankNMLs[i]) continue;
        return i;
    }
    return 0;
}
inline char *get_rank(Tprofile_rank *profile)
{
    return rankLables[get_rank_id(profile)];
}