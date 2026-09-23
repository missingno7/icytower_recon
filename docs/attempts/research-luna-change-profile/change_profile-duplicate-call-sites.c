void change_profile(void)
{
    Tprofile *newProfile;

    if (profile) {
        syncProfileFromOptions();
        save_profile(profile);
        newProfile = select_profile(profile, profiles, numProfiles, &ctrl);
    } else {
        newProfile = select_profile(profile, profiles, numProfiles, &ctrl);
    }
    if (newProfile) {
        if (profile) free(profile);
        profile = newProfile;
        strcpy(options.lastProfile, profile->handle);
        syncOptionsFromProfile();
        save_config();
        rebuild_profile_list(0);
    }
}
