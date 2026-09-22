void show_instructions(void)
{
    int done;

    blit(data[126].dat,swap_screen,0,0,0,0,640,480);
    masked_blit(data[70].dat,swap_screen,0,0,0,0,640,480);
    while (is_any(&ctrl))
        poll_control(&ctrl,0);
    fadeIn(swap_screen,16);
    done=0;
    while (!closeButtonClicked && !done) {
        cycle_count=0;
        checkMenuFocus();
        poll_control(&ctrl,0);
        done=is_fire(&ctrl)!=0;
        if (key[KEY_ESC] || key[KEY_ENTER])
            done=1;
        while (!cycle_count)
            rest(2);
    }
    fadeOut(16);
}
