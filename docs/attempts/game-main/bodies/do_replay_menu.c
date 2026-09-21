/* Source recovery of main.c:5474, 0x410f98..0x4119fd.
 * Census gap ext_4b2a3c (offset 0, first instruction of the function) is
 * ___chkstk, the compiler-emitted Win32 stack probe automatically inserted
 * ahead of any large (>4KB) local frame -- historical frame here is 0x185c
 * (6236) bytes, matching this function's six char buffers (filename[512],
 * player_name[512], comment[512], full_filename[512], replay_filename[2048],
 * temporary_filename[2048] = 6144 bytes + locals). It is not a call written
 * in C source and cannot be added by editing this body (no asm/pragma
 * allowed); whether it is emitted depends on the compiler's own stack-frame
 * threshold, which is outside function-body scope. Left unresolved. */
int do_replay_menu(void)
{
    int ret = -1;
    int play_again = 0;
    int isGuest = !stricmp("guest",profile->handle);
    int state = !isGuest;
    char filename[512];
    char player_name[512];
    char comment[512];
    char full_filename[512];
    char replay_filename[2048];
    char temporary_filename[2048];

    log2file(" replay_menu launched");
    while (!closeButtonClicked && ret!='l') {
        ret=handle_menu(replay_menu,&menu_params,&ctrl,swap_screen,
                        replay_menu_callback,180,160,0);
        if (ret=='e') {
            log2file("  play again selected");
            play_again=1;
        }
        else if (ret=='|') {
            log2file("  view replay selected");
            fadeOut(16);
            sprintf(temporary_filename,"%slast_game.itr",replay_directory);
            run_demo(temporary_filename);
        }
        else if (ret=='{') {
            log2file("  save replay selected");
            memset(filename,' ',511);
            filename[511]=0;
            memset(player_name,' ',511);
            player_name[511]=0;
            memset(comment,' ',511);
            comment[511]=0;
            if (isGuest)
                strcpy(player_name," - ");
            else
                strcpy(player_name,profile->handle);
            state=!isGuest;
            while (!closeButtonClicked && state!='*') {
                stretch_sprite(swap_screen,data[86].dat,120,140,380,200);
                textout_ex(swap_screen,data[51].dat,"SAVE REPLAY",140,150,-1,-1);
                textout_ex(swap_screen,data[54].dat,"(enter to advance)",320,312,
                           makecol(80,80,80),-1);
                drawSlot(swap_screen,140,210,"Your name:",player_name,
                         makecol(50,50,50));
                drawSlot(swap_screen,140,250,"Filename:",filename,
                         makecol(50,50,50));
                drawSlot(swap_screen,140,290,"Comment: (optional)",comment,
                         makecol(50,50,50));
                blit_to_screen(swap_screen);
                if (state==0) {
                    state=get_string(swap_screen,player_name,340,512,data[54].dat,
                                     140,210,makecol(0,0,0),makecol(255,255,255));
                    replaceBadCharacters(player_name,'_');
                    state++;
                    if (!state)
                        state='*';
                }
                else if (state==1) {
                    if (!filename[0] && player_name[0]) {
                        sprintf(filename,"%s_%d_%d_%d",player_name,demo->score,
                                demo->floor,demo->combo);
                        replaceBadCharacters(filename,'_');
                    }
                    if (get_string(swap_screen,filename,340,512,data[54].dat,
                                   140,250,makecol(0,0,0),makecol(255,255,255)) == -1)
                        state='*';
                    else {
                        replaceBadCharacters(filename,'_');
                        state=2;
                    }
                }
                else if (state==2) {
                    int edit_result;

                    edit_result=get_string(swap_screen,comment,340,42,data[54].dat,
                                           140,290,makecol(0,0,0),makecol(255,255,255));
                    if (edit_result == -1)
                        state='*';
                    else if (edit_result == -2)
                        state=!isGuest;
                    else
                        state=3;
                }
                else if (state==3) {
                    sprintf(temporary_filename,"%slast_game.itr",replay_directory);
                    if (!player_name[0]) {
                        state=0;
                        continue;
                    }
                    if (!filename[0]) {
                        state=1;
                        continue;
                    }
                    if (demo)
                        destroy_replay(demo);
                    demo=load_replay(temporary_filename);
                    if (!demo) {
                        my_alert("Failed to save replay.",
                                 "Temporary file not found.",0,1);
                        continue;
                    }
                    if (calc_replay_checksum(demo)!=uberChecksum) {
                        my_alert("Failed to save replay.",
                                 "Temporary file mismatch.",0,1);
                        continue;
                    }
                    strncpy(demo->name,player_name,30);
                    strcpy(demo->comment,comment);
                    replace_extension(replay_filename,filename,"itr",512);
                    sprintf(full_filename,"%s%s",replay_directory,replay_filename);
                    if (exists(full_filename) &&
                        !my_alert("The file exists.","Do you want to overwrite it?",1,0)) {
                        state=1;
                        continue;
                    }
                    if (save_replay(replay_directory,replay_filename,demo,demo->size+2,1)<0) {
                        my_alert("Failed to save replay.",full_filename,0,1);
                        state=1;
                    }
                    else {
                        my_alert("Replay saved.",0,0,1);
                        state='*';
                    }
                }
            }
        }
    }
    return play_again;
}
