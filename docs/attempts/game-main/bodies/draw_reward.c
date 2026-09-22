void draw_reward(BITMAP *bmp)
{
    if (options.flash) {
        if (options.flash!=1)
            return;
        stretch_sprite(bmp,reward_bmp,
                       320-(int)(fixtof(reward_scale/2)*reward_bmp->w),
                       360-(int)(fixtof(reward_scale/2)*reward_bmp->h)-fixtoi(reward_scale*reward_bmp->h/2),
                       fixtoi(reward_scale*reward_bmp->w),
                       fixtoi(reward_scale*reward_bmp->h));
    }
    else {
        rotate_scaled_sprite(bmp,reward_bmp,
                             320-(int)(fixtof(reward_scale/2)*reward_bmp->w),
                             360-(int)(fixtof(reward_scale)*120-reward_bmp->h*fixtof(reward_scale/2)),
                             reward_scale<<8,reward_scale);
    }
}
