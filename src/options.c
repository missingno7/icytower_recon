/* Historical CU: F:\projects\icytower\trunk\source\options.c
 * Ownership: GAME
 * UNKNOWN: generate_options_checksum @ 0x004181cc, 254 bytes
 * UNKNOWN: reset_options @ 0x004182cc, 205 bytes
 * UNKNOWN: load_options @ 0x0041839c, 70 bytes
 * UNKNOWN: save_options @ 0x004183e4, 58 bytes
 */

unsigned int hash3(unsigned int a)
{
    a = (a ^ 0x3dU) ^ (a >> 16);
    a *= 9U;
    a ^= a >> 4;
    a *= 668265261U;
    a ^= a >> 15;
    return a;
}
