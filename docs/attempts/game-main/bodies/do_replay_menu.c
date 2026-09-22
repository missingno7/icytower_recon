/* Source recovery of main.c:5474, 0x410f98..0x4119fd.
 * Census gap ext_4b2a3c (offset 0, first instruction of the function) is
 * ___chkstk, the compiler-emitted Win32 stack probe automatically inserted
 * ahead of any large (>4KB) local frame -- historical frame here is 0x185c
 * (6236) bytes. It is not a call written in C source and cannot be added by
 * editing this body (no asm/pragma allowed); whether it is emitted depends
 * on the compiler's own stack-frame threshold, which is outside function-body
 * scope. Left unresolved.
 * buffer/fname/pname/fpath/status/action/lets_save/lastGameFile/thisChecksum
 * are DWARF-evidenced: stack slots decoded via CU base 0x406960 + function VA
 * 0x410f98 against docs/current/function-evidence/main/do_replay_menu.json's
 * location lists -- buffer=-0x1018(ebp) (fbreg -4128+8), fname=-0x218(ebp)
 * (fbreg -544+8), pname=-0x418(ebp) (fbreg -1056+8), fpath=-0x818(ebp)
 * (fbreg -2080+8), lastGameFile=-0x1818(ebp) (fbreg -6176+8, its other
 * DWARF entry reuses buffer's -0x1018 slot in a non-overlapping scope). */
int do_replay_menu(void)
{
    int ret = -1;
    int play_again = 0;
    int isGuest = !stricmp("guest",profile->handle);
    int status = !isGuest;
    char fname[512];
    char pname[512];
    char comment[512];
    char fpath[512];
    char buffer[1024];
    char lastGameFile[2048];
    int action;
    int thisChecksum;

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
            sprintf(lastGameFile,"%slast_game.itr",replay_directory);
            run_demo(lastGameFile);
        }
        else if (ret=='{') {
            log2file("  save replay selected");
            memset(fname,' ',511);
            fname[511]=0;
            if (isGuest)
                strcpy(pname," - ");
            else
                strcpy(pname,profile->handle);
            memset(comment,' ',511);
            comment[511]=0;
            status=!isGuest;
            while (!closeButtonClicked && status!='*') {
                stretch_sprite(swap_screen,data[86].dat,120,140,380,200);
                textout_ex(swap_screen,data[51].dat,"SAVE REPLAY",140,150,-1,-1);
                textout_ex(swap_screen,data[54].dat,"(enter to advance)",320,312,
                           makecol(80,80,80),-1);
                drawSlot(swap_screen,140,210,"Your name:",pname,
                         makecol(50,50,50));
                drawSlot(swap_screen,140,250,"Filename:",fname,
                         makecol(50,50,50));
                drawSlot(swap_screen,140,290,"Comment: (optional)",comment,
                         makecol(50,50,50));
                blit_to_screen(swap_screen);
                if (status==0) {
                    action=get_string(swap_screen,pname,340,512,data[54].dat,
                                     140,210,makecol(0,0,0),makecol(255,255,255));
                    replaceBadCharacters(pname,'_');
                    action++;
                    if (!action)
                        status='*';
                    else
                        status=1;
                    /* 5537 */
                    drawSlot(swap_screen,140,210,"Your name:",pname,
                             makecol(50,50,50));
                    /* 5538 */
                    drawSlot(swap_screen,140,250,"Filename:",fname,
                             makecol(50,50,50));
                    /* 5539 */
                    drawSlot(swap_screen,140,290,"Comment: (optional)",comment,
                             makecol(50,50,50));
                }
                else if (status==1) {
                    if (!fname[0] && pname[0]) {
                        sprintf(fname,"%s_%d_%d_%d",pname,demo->score,
                                demo->floor,demo->combo);
                        replaceBadCharacters(fname,'_');
                    }
                    action=get_string(swap_screen,fname,340,512,data[54].dat,
                                   140,250,makecol(0,0,0),makecol(255,255,255));
                    if (action == -1)
                        status='*';
                    else {
                        replaceBadCharacters(fname,'_');
                        status=2;
                    }
                    /* 5581 */
                    drawSlot(swap_screen,140,210,"Your name:",pname,
                             makecol(50,50,50));
                    /* 5582 */
                    drawSlot(swap_screen,140,250,"Filename:",fname,
                             makecol(50,50,50));
                    /* 5583 */
                    drawSlot(swap_screen,140,290,"Comment: (optional)",comment,
                             makecol(50,50,50));
                    /* 5584 */
                    blit_to_screen(swap_screen);
                }
                else if (status==2) {
                    action=get_string(swap_screen,comment,340,42,data[54].dat,
                                           140,290,makecol(0,0,0),makecol(255,255,255));
                    if (action == -1)
                        status='*';
                    else if (action == -2)
                        status=!isGuest;
                    else
                        status=3;
                    /* 5581 */
                    drawSlot(swap_screen,140,210,"Your name:",pname,
                             makecol(50,50,50));
                    /* 5582 */
                    drawSlot(swap_screen,140,250,"Filename:",fname,
                             makecol(50,50,50));
                    /* 5583 */
                    drawSlot(swap_screen,140,290,"Comment: (optional)",comment,
                             makecol(50,50,50));
                    /* 5584 */
                    blit_to_screen(swap_screen);
                }
                else if (status==3) {
                    sprintf(lastGameFile,"%slast_game.itr",replay_directory);
                    if (!pname[0]) {
                        status=0;
                        continue;
                    }
                    if (!fname[0]) {
                        status=1;
                        continue;
                    }
                    if (demo)
                        destroy_replay(demo);
                    demo=load_replay(lastGameFile);
                    if (!demo) {
                        my_alert("Failed to save replay.",
                                 "Temporary file not found.",0,1);
                        continue;
                    }
                    thisChecksum=calc_replay_checksum(demo);
                    if (thisChecksum!=uberChecksum) {
                        my_alert("Failed to save replay.",
                                 "Temporary file mismatch.",0,1);
                        continue;
                    }
                    strncpy(demo->name,pname,30);
                    strcpy(demo->comment,comment);
                    replace_extension(buffer,fname,"itr",512);
                    sprintf(fpath,"%s%s",replay_directory,buffer);
                    if (exists(fpath) &&
                        !my_alert("The file exists.","Do you want to overwrite it?",1,0)) {
                        status=1;
                        continue;
                    }
                    if (save_replay(replay_directory,buffer,demo,demo->size+2,1)<0) {
                        my_alert("Failed to save replay.",fpath,0,1);
                        status=1;
                    }
                    else {
                        my_alert("Replay saved.",0,0,1);
                        status='*';
                    }
                }
            }
        }
    }
    return play_again;
}
