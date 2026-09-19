/* Partial historical replay.c recovery.
 * Ownership: GAME.
 *
 * The remaining functions below are still pending reconstruction:
 * UNKNOWN: hash @ 0x0041b9c8, 71 bytes
 * UNKNOWN: calc_replay_checksum_131 @ 0x0041ba10, 177 bytes
 * UNKNOWN: calc_replay_checksum @ 0x0041bac4, 676 bytes
 * UNKNOWN: destroy_replay @ 0x0041bd68, 54 bytes
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
