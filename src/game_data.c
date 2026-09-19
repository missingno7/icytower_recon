/* Historical CU: F:\projects\icytower\trunk\source\game_data.c
 * Ownership: GAME
 * Partial source recovery.
 * UNKNOWN: add_jump_sequence @ 0x004040f4, 87 bytes
 * UNKNOWN: add_combo @ 0x0040414c, 62 bytes
 * UNKNOWN: create_game_data @ 0x00404198, 186 bytes
 * UNKNOWN: getGameDataXML @ 0x00404254, 1855 bytes
 */

extern void free(void *ptr);

void destroy_game_data(void *gd) { free(gd); }
