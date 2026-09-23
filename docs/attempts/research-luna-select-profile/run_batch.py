import json, subprocess, sys, hashlib
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'tools'))
from tu_context_probe import islands
from experiment import compare
from recovery_pipeline import OBJDUMP
from common import read_json, identity, write_json
ROOT=Path.cwd()
source_path=ROOT/'docs/attempts/research-luna-profile-interface/overlay/profile-typed-late-header.c'
full_base=source_path.read_text(encoding='cp1252')
body_path=ROOT/'docs/attempts/research-luna-select-profile/overlay/profile-typed-late-header-typed.c'
base=body_path.read_text(encoding='cp1252')

def require_replace(s, old, new, label):
    if old not in s: raise ValueError('missing pattern for '+label+': '+old[:100])
    return s.replace(old,new,1)

def add_paths(body, scoped=False):
    b=body
    if scoped:
        b=require_replace(b,'    char input[256];\n','', 'remove function-scope input')
        b=require_replace(b,'                char *name = profiles[profileIndex].handle;\n                if (stricmp(name, "guest")', '                char *name = profiles[profileIndex].handle;\n                char buff[256];\n                if (stricmp(name, "guest")','add delete buffer')
        s=b.index('                char *name = profiles[profileIndex].handle;\n                char buff[256];')
        e=b.index('            } else if (kp == 67)',s)
        b=b[:s]+b[s:e].replace('input','buff')+b[e:]
        b=require_replace(b,'                char *name = profiles[profileIndex].handle;\n                play_menu_select();','                char *name = profiles[profileIndex].handle;\n                char new_name[32];\n                play_menu_select();','add profile-name buffer')
        s=b.index('                char *name = profiles[profileIndex].handle;\n                char new_name[32];')
        e=b.index('            } else if (kp == 59)',s)
        b=b[:s]+b[s:e].replace('input','new_name')+b[e:]
    # Restore the historically evidenced create-profile prompt decorations.
    b=require_replace(b,'                    textprintf_ex(swap_screen, data[51].dat, 140, 140,\n                                  -1, -1, "Enter profile name:");\n',
      '                    textprintf_ex(swap_screen, data[51].dat, 140, 140,\n                                  -1, -1, "Enter profile name:");\n'
      '                    textout_right_ex(swap_screen, data[54].dat,\n'
      '                                     "...and press enter.", 480, 210, 0, -1);\n'
      '                    rect(swap_screen, 139, 191, 480, 210,\n'
      '                         makecol(255, 255, 255));\n'
      '                    rectfill(swap_screen, 139, 191, 480, 210,\n'
      '                             makecol(80, 80, 80));\n','add create prompt UI')
    # Historical post-loop selected-profile confirmation. Its buffer is block-scoped per DWARF.
    b=require_replace(b,'\n    targetY = 510;\n',
      '\n    if (selectedProfile) {\n'
      '        char buf[128];\n'
      '        sprintf(buf, "Now using profile \'%s\'", selectedProfile->handle);\n'
      '        my_alert("Profile Changed!", buf, 0, 1);\n'
      '    }\n'
      '\n    targetY = 510;\n','add selected profile alert')
    return b

def switch_dispatch(body):
    b=body
    old='''            if (kp == 85) {
                if (profileIndex < numProfiles - 1) {
                    profileIndex++;
                    if (profileIndex >= offset + page_size)
                        offset++;
                    play_menu_move();
                } else {
                    profileIndex = numProfiles - 1;
                    offset = numProfiles - page_size;
                    if (offset < 0)
                        offset = 0;
                }
            } else if (kp == 84) {
                if (profileIndex > 0) {
                    profileIndex--;
                    if (offset > profileIndex)
                        offset--;
                    play_menu_move();
                } else {
                    profileIndex = 0;
                    offset = 0;
                }
            } else if (kp == 83) {
                char *name = profiles[profileIndex].handle;
                if (stricmp(name, "guest") &&
                    stricmp(name, current_profile->handle)) {
                    sprintf(input, "Really delete '%s'?", name);
                    if (my_alert(input, "WARNING: It will be gone forever.",
                                 1, 0)) {
                        delete_profile(name);
                        numProfiles = rebuild_profile_list(&profiles);
                        if (profileIndex >= numProfiles)
                            profileIndex = numProfiles - 1;
                    }
                }
            } else if (kp == 67) {
                char *name = profiles[profileIndex].handle;
                play_menu_select();
                if (!stricmp(name, "CREATE NEW PROFILE")) {
                    set_trans_blender(0, 0, 0, 158);
                    drawing_mode(5, 0, 0, 0);
                    rectfill(swap_screen, 0, 0,
                             SCREEN_W,
                             SCREEN_H,
                             makecol(0, 0, 0));
                    solid_mode();
                    input[0] = 0;
                    draw_sprite(swap_screen, data[88].dat, 100, 140);
                    textprintf_ex(swap_screen, data[51].dat, 140, 140,
                                  -1, -1, "Enter profile name:");
                    if (get_string(swap_screen, input, 340, 32, data[54].dat,
                                   140, 191, makecol(0, 0, 0), -1) >= 0 &&
                        input[0]) {
                        replaceBadCharacters(input, '_');
                        selectedProfile = create_profile(input, 0);
                        if (selectedProfile) {
                            my_alert("CREATE PROFILE", "Profile created!", 0, 1);
                            done = -1;
                        } else {
                            my_alert("CREATE PROFILE", "Failed to create profile.", 0, 1);
                        }
                    }
                } else {
                    selectedProfile = load_profile(name);
                    if (selectedProfile)
                        done = -1;
                    else
                        my_alert("SELECT PROFILE",
                                 "The profile you selected is broken.", 0, 1);
                }
            } else if (kp == 59) {
                play_menu_select();
                clear_keybuf();
                done = -1;
            }'''
    new='''            switch (kp) {
            case 85:
                if (profileIndex < numProfiles - 1) {
                    profileIndex++;
                    if (profileIndex >= offset + page_size)
                        offset++;
                    play_menu_move();
                } else {
                    profileIndex = numProfiles - 1;
                    offset = numProfiles - page_size;
                    if (offset < 0)
                        offset = 0;
                }
                break;
            case 84:
                if (profileIndex > 0) {
                    profileIndex--;
                    if (offset > profileIndex)
                        offset--;
                    play_menu_move();
                } else {
                    profileIndex = 0;
                    offset = 0;
                }
                break;
            case 83: {
                char *name = profiles[profileIndex].handle;
                if (stricmp(name, "guest") &&
                    stricmp(name, current_profile->handle)) {
                    sprintf(input, "Really delete '%s'?", name);
                    if (my_alert(input, "WARNING: It will be gone forever.",
                                 1, 0)) {
                        delete_profile(name);
                        numProfiles = rebuild_profile_list(&profiles);
                        if (profileIndex >= numProfiles)
                            profileIndex = numProfiles - 1;
                    }
                }
                break;
            }
            case 67: {
                char *name = profiles[profileIndex].handle;
                play_menu_select();
                if (!stricmp(name, "CREATE NEW PROFILE")) {
                    set_trans_blender(0, 0, 0, 158);
                    drawing_mode(5, 0, 0, 0);
                    rectfill(swap_screen, 0, 0,
                             SCREEN_W,
                             SCREEN_H,
                             makecol(0, 0, 0));
                    solid_mode();
                    input[0] = 0;
                    draw_sprite(swap_screen, data[88].dat, 100, 140);
                    textprintf_ex(swap_screen, data[51].dat, 140, 140,
                                  -1, -1, "Enter profile name:");
                    if (get_string(swap_screen, input, 340, 32, data[54].dat,
                                   140, 191, makecol(0, 0, 0), -1) >= 0 &&
                        input[0]) {
                        replaceBadCharacters(input, '_');
                        selectedProfile = create_profile(input, 0);
                        if (selectedProfile) {
                            my_alert("CREATE PROFILE", "Profile created!", 0, 1);
                            done = -1;
                        } else {
                            my_alert("CREATE PROFILE", "Failed to create profile.", 0, 1);
                        }
                    }
                } else {
                    selectedProfile = load_profile(name);
                    if (selectedProfile)
                        done = -1;
                    else
                        my_alert("SELECT PROFILE",
                                 "The profile you selected is broken.", 0, 1);
                }
                break;
            }
            case 59:
                play_menu_select();
                clear_keybuf();
                done = -1;
                break;
            }'''
    if old not in b: raise ValueError('dispatch block not found for switch conversion')
    return b.replace(old,new,1)

variants=[
 ('switch_dispatch',switch_dispatch(base)),
 ('missing_ui_paths',add_paths(base,False)),
 ('scoped_buffers_ui_paths',add_paths(base,True)),

]
refbuild=json.loads((ROOT/'docs/attempts/research-luna-profile-interface/build/profile-selector-typed-late-header-v1/build.json').read_text(encoding='utf-8'))
summary={'hypotheses':[
 'Original bytes have a bounded keyboard dispatch: subtract scan code 0x3b, range-check 0x1a, and jump through a table. The retained typed candidate uses an if/else chain.',
 'Original create-profile branch contains textout_right_ex and two bitmap rectangle draws missing from the typed candidate; DWARF has a branch-scoped 32-byte name buffer.',
 'Original post-loop selected-profile notice calls sprintf and my_alert; DWARF places its 128-byte buffer in a separate lexical block that aliases the other buffers at frame offset -288.',
 'Original delete confirmation owns a distinct branch-scoped 256-byte buffer; its DWARF location aliases the other disjoint-scope buffers at -288.'
 ],'baseline':{'label':'profile-selector-typed-late-header-v1','candidate_select_size':2698,'historical_select_size':3070,'first_mismatch':12},'compiler':refbuild['compiler'],'flags':refbuild['flags'],'variants':[]}
for label,body in variants:
    (ROOT/'docs/attempts/research-luna-select-profile/overlay').mkdir(parents=True,exist_ok=True)
    bodyfile=ROOT/'docs/attempts/research-luna-select-profile/overlay'/(label+'.body.c')
    bodyfile.write_bytes(body.encode('cp1252'))
    # replace only select_profile function body in full typed-late-header TU
    spans=[i for i in islands(full_base) if i['name']=='select_profile']
    if len(spans)!=1: raise ValueError('full TU select_profile island mismatch')
    s=spans[0]; full=full_base[:s['def_start']]+body+full_base[s['end']:]
    fullfile=ROOT/'docs/attempts/research-luna-select-profile/overlay'/(label+'.c')
    fullfile.write_bytes(full.encode('cp1252'))
    out=ROOT/'docs/attempts/research-luna-select-profile/build'/label; out.mkdir(parents=True,exist_ok=True)
    cmd=refbuild['command'][:]
    for flag,value in [('-MF',out/'unit.d'),('-aux-info',out/'interfaces.aux'),('-c',fullfile),('-o',out/'unit.o')]: cmd[cmd.index(flag)+1]=str(value)
    proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    (out/'compiler.stdout.txt').write_text(proc.stdout,encoding='utf-8'); (out/'compiler.stderr.txt').write_text(proc.stderr,encoding='utf-8')
    row={'label':label,'body_identity':identity(bodyfile),'full_tu_identity':identity(fullfile),'compile_returncode':proc.returncode}
    if proc.returncode:
        row['compile']='FAILED'; row['errors']=proc.stderr[-3000:]; summary['variants'].append(row); continue
    report=compare(out/'unit.o',refbuild['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
    write_json(out/'comparison.json',report)
    funcs={f['name']:f for f in report['functions']}
    from effective_outcomes import effective_identity
    exact=sorted(n for n,f in funcs.items() if f['status']=='FUNCTION_MATCH')
    row.update({'compile':'OK','object_identity':identity(out/'unit.o'),'select_profile':{'status':funcs['select_profile']['status'],'candidate_size':funcs['select_profile']['candidate_size'],'original_size':funcs['select_profile']['original_size'],'first_difference':funcs['select_profile'].get('first_difference'),'effective_identity':effective_identity(funcs['select_profile'])},'draw_profile_selector':{'status':funcs['draw_profile_selector']['status'],'candidate_size':funcs['draw_profile_selector']['candidate_size'],'original_size':funcs['draw_profile_selector']['original_size'],'first_difference':funcs['draw_profile_selector'].get('first_difference'),'effective_identity':effective_identity(funcs['draw_profile_selector'])},'exact_functions':exact,'exact_count':len(exact),'matches_after':report.get('function_matches'),'object_match':report.get('object_match'),'cu_match':report.get('cu_match'),'whole_text_contribution_equal':report.get('whole_text_contribution_equal'),'relative_layout_equal':report.get('relative_layout_equal'),'function_count':len(report.get('functions',[])),'object_relocations':len(report.get('object_relocations',[])),'common_allocations':report.get('common_allocations'),'initialized_data_comparison':report.get('initialized_data_comparison')})
    prov={'compiler':refbuild['compiler'],'flags':refbuild['flags'],'command':[str(a) for a in cmd],'cwd':str(ROOT),'historical_cu':refbuild['historical_cu'],'full_tu_overlay':str(fullfile),'object_identity':row['object_identity'],'strict_report':'comparison.json','function_count':row['function_count'],'all_17_profile_functions_reported':row['function_count']==17,'relocations_reported':row['object_relocations'] is not None,'initialized_data_reported':bool(row['initialized_data_comparison']),'common_allocations_reported':row['common_allocations'] is not None}
    write_json(out/'build-provenance.json',prov)
    summary['variants'].append(row)
write_json(ROOT/'docs/attempts/research-luna-select-profile/batch-summary.json',summary)
print(json.dumps(summary,indent=2))



