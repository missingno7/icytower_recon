void change_profile(void)
{
    Tprofile *newProfile;

    newProfile = profile;
    if (newProfile) {
        syncProfileFromOptions();
        save_profile(profile);
        newProfile = profile;
    }
    newProfile = select_profile(newProfile, profiles, numProfiles, &ctrl);
    if (newProfile) {
        if (profile) free(profile);
        profile = newProfile;
        strcpy(options.lastProfile, profile->handle);
        syncOptionsFromProfile();
        save_config();
        rebuild_profile_list(0);
    }
}