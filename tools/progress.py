"""Publish reviewable experiment snapshots and explicitly scoped metrics."""
from pathlib import Path
from common import ROOT, identity, read_json, write_json

def main():
    units=read_json(ROOT/'src/units.json')
    reports={}
    for target in ['game-beta','game-control','game-csv','game-custom','game-directories','game-fld-adspot','game-game-data','game-hisc','game-main-partial','game-map','game-menu','game-options','game-particle','game-replay','game-profile','game-scroller','game-stars','game-timer','allegro-timer','allegro-color','allegro-blit','allegro-logg']:
        p=ROOT/'build/experiments/tdm-2'/target/'O2/comparison.json'
        r=read_json(p)
        for name,expected in r['build']['local_inputs'].items():
            if identity(ROOT/name)!=expected:
                raise ValueError('Stale experiment local input: '+name)
        if r['build']['toolchain_lock']!=identity(ROOT/'toolchain/lock.json'):
            raise ValueError('Stale experiment toolchain lock')
        if r['build']['candidate_toolchain_lock']!=identity(ROOT/'toolchain/tdm-2-lock.json'):
            raise ValueError('Stale candidate toolchain lock')
        reports[target]=r
        write_json(ROOT/'docs/experiments'/f'{target}-O2.json',r)
    write_json(ROOT/'docs/experiments/optimization-matrix.json',read_json(ROOT/'build/experiments/tdm-2/summary.json'))
    link=read_json(ROOT/'build/link-probe/tdm-2/report.json')
    write_json(ROOT/'docs/experiments/link-probe.json',link)
    timer=reports['game-timer']
    game_units=[u for u in units if u['classification']=='GAME']
    game_functions=[f for u in game_units for f in u['functions']]
    games=[reports['game-beta'],reports['game-control'],reports['game-custom'],reports['game-directories'],reports['game-fld-adspot'],reports['game-game-data'],reports['game-hisc'],reports['game-main-partial'],reports['game-map'],reports['game-menu'],reports['game-options'],reports['game-particle'],reports['game-replay'],reports['game-profile'],reports['game-scroller'],reports['game-stars'],timer]
    matched=[f for r in games for f in r['functions'] if f['status']=='FUNCTION_MATCH']
    library_matches=[r for key,r in reports.items() if key.startswith('allegro-') and r['whole_text_contribution_equal']]
    data_bytes=sum(s['logical_size'] for r in reports.values() for s in r['initialized_data_comparison'] if s['content_equal'])
    summary=read_json(ROOT/'evidence/census/dwarf-summary.json')
    recovery={}
    recovery_sources={'game-fld-adspot':'src/fld_adspot.c','game-game-data':'src/game_data.c'}
    for target in ['game-beta','game-control','game-csv','game-custom','game-directories','game-fld-adspot','game-game-data','game-hisc','game-main-partial','game-map','game-menu','game-options','game-particle','game-replay','game-profile','game-scroller','game-stars','game-timer']:
        report=reports[target]
        recovery[recovery_sources.get(target,'src/'+target[5:]+'.c')]={
            'state':'RECOVERED_EXACT_FUNCTIONS' if report['function_matches']==report['functions_total'] else 'PARTIALLY_MATCHED',
            'functions':{f['name']:f['status'] for f in report['functions']},
            'function_complete':report['function_matches']==report['functions_total'],
            'text_contribution_equal':report['whole_text_contribution_equal'],
            'object_match':False,'cu_match':False,'report':'docs/experiments/'+target+'-O2.json'}
    integration=read_json(ROOT/'build/integration/tdm-2/build.json')
    layout=read_json(ROOT/'docs/experiments/integration-layout.json')
    if layout['build_report']!=identity(ROOT/'build/integration/tdm-2/build.json'):
        raise ValueError('Stale integration layout report')
    write_json(ROOT/'docs/experiments/integration-link.json',integration)
    library=read_json(ROOT/'build/allegro/tdm-2/build.json')
    xiph=read_json(ROOT/'build/xiph/tdm-2/build.json')
    audio=read_json(ROOT/'build/audio/tdm-2/build.json')
    custom_audio=read_json(ROOT/'build/custom-audio/tdm-2/build.json')
    if xiph['plan']!=identity(ROOT/'third_party/xiph-build.json') or xiph['source_lock']!=identity(ROOT/'third_party/xiph-lock.json'):
        raise ValueError('Stale Xiph build report')
    if audio['xiph_report']!=identity(ROOT/'build/xiph/tdm-2/build.json'):
        raise ValueError('Stale audio link report')
    if custom_audio['xiph_report']!=identity(ROOT/'build/xiph/tdm-2/build.json'):
        raise ValueError('Stale custom audio link report')
    write_json(ROOT/'docs/experiments/xiph-build.json',xiph)
    write_json(ROOT/'docs/experiments/audio-link.json',audio)
    write_json(ROOT/'docs/experiments/custom-audio-link.json',custom_audio)
    write_json(ROOT/'docs/experiments/allegro-build.json',library)
    write_json(ROOT/'src/recovery.json',recovery)
    metrics={
        'schema':1,
        'scope':'Current independent reconstruction; inherited behavioral promotions are not counted as reconstructed functions.',
        'game_tree_cus_total':len(units),'game_tree_cus_skeletonized':len(units),
        'game_owned_cus_total':len(game_units),'ambiguous_cus_recovery_owned':2,
        'game_cus_partially_recovered':sum(0<r['function_matches']<r['functions_total'] for r in games),
        'game_cus_function_complete':sum(r['function_matches']==r['functions_total'] for r in games),'game_cus_object_exact':0,
        'game_cus_complete_text_equal':sum(r['whole_text_contribution_equal'] for r in games),
        'game_functions_total':len(game_functions),'game_functions_recovered':len(matched),
        'game_text_bytes_reconstructed':sum(f['original_size'] for f in matched),
        'game_complete_cu_text_bytes':sum(r['original_cu_span'] for r in games if r['whole_text_contribution_equal']),
        'unknown_game_text_bytes':sum(f['size'] for f in game_functions)-sum(f['original_size'] for f in matched),
        'ambiguous_functions_not_in_game_denominator':16,'ambiguous_text_bytes_not_in_game_denominator':2998,
        'ambiguous_cus_complete_text_equal':int(reports['game-csv']['whole_text_contribution_equal']),
        'ambiguous_functions_recovered':reports['game-csv']['function_matches'],
        'ambiguous_complete_cu_text_bytes':reports['game-csv']['original_cu_span'] if reports['game-csv']['whole_text_contribution_equal'] else 0,
        'known_upstream_game_tree_files_populated':3,
        'upstream_library_cus_identified':137,'upstream_library_cu_scope':'115 Allegro (including 9 data-only) plus 22 Xiph; excludes CRT', 'allegro_core_cus_built':len(library['units']),'upstream_library_cus_reproduced':0,
        'upstream_library_cus_complete_text_equal':len(library_matches),
        'upstream_library_text_bytes_reproduced':sum(r['original_cu_span'] for r in library_matches),
        'modified_vendor_cus_complete_text_equal':int(reports['allegro-logg']['whole_text_contribution_equal']),
        'modified_vendor_scope':'Included in library CU totals; logg memory extension reconstructed independently, not unmodified upstream.',
        'xiph_cus_built':len(xiph['units']),
        'audio_dependencies_linked':True,
        'audio_dependency_scope':'Synthetic logg/Xiph/Allegro PE, not executed; Xiph bytes and original compiler configuration unproven.',
        'custom_dependencies_linked':True,
        'custom_dependency_scope':'Synthetic custom/directories/main-helper/particle/logg/Xiph/Allegro/pthread PE, not executed; custom complete text and natural layout remain unproven.',
        'particle_dependencies_linked':True,
        'particle_dependency_scope':'Synthetic custom-audio PE resolves particle through the recovered exact new_rand body; it is outside the natural integration layout experiment.',
        'data_bytes_structured_and_content_verified':data_bytes,
        'game_bss_globals_typed':7,'game_bss_semantic_bytes':168,'game_common_allocation_bytes':240,
        'dwarf_type_dies_recovered':len(read_json(ROOT/'evidence/census/types.json')),
        'dwarf_type_count_scope':'Type DIE census including duplicate declarations; not a count of emitted canonical C types.',
        'dwarf_total_dies':summary['die_count'],'dwarf_unresolved_origins':len(summary['unresolved_origin_specification']),
        'linker_resolved_game_functions':sum(f['classification']=='GAME' for f in layout['functions']),
        'linker_resolved_game_bytes':sum(f['candidate_body_size'] for f in layout['functions'] if f['classification']=='GAME'),
        'linker_resolved_ambiguous_functions':sum(f['classification']=='AMBIGUOUS' for f in layout['functions']),
        'linker_resolution_scope':'Synthetic integration link only; bytes count candidate function bodies, not exact matches',
        'natural_game_layout_prefix_length':layout['natural_game_address_extent_prefix_bytes'],
        'natural_game_layout_prefix_scope':'Matching function addresses and body extents; excludes padding after last matching body; not linked byte equality',
        'probe_startup_addresses_matching':sum(r['address_equal'] for r in link['startup_functions']),
        'probe_startup_address_and_extent_prefix_length':link['natural_startup_address_prefix_bytes'],
        'probe_strict_text_byte_prefix':link['strict_text_byte_prefix'],
        'pe_sections_matching':0,'whole_executable_status':'GAME_NOT_LINKED: synthetic beta/control/csv/directories/timer/stars plus Allegro integration PE links',
        'first_current_blocker':'B007: custom.c load_character_bmp differs; custom link dependencies and remaining CUs/debug metadata unresolved',
        'proof_policy':'docs/proof-levels.md',
    }
    write_json(ROOT/'docs/progress.json',metrics)
    blockers=[
        {'id':'B001','target':'Historical startup/link prefix',
         'current_evidence':'The archived compiler reports TDM-1 4.4.1 SJLJ. Seven startup symbol addresses match; the first 704 bytes have matching function starts and spans.',
         'first_mismatch':{'function':'___gcc_register_frame','address':'0x4012c6','original_byte':'e8','candidate_byte':'8b',
                           'detail':'Original calls ___cmshared_create_or_grab; archived crtbegin.o starts a global load. Next function is 4 bytes early.'},
         'hypotheses':['Original cross-built TDM runtime differs from archived native mingw32 runtime despite the same version label','Code::Blocks carried a patched CRT/libgcc set'],
         'experiments_tried':['Real gcc -mwindows link with archived crt2.o/crtbegin.o/import archives','Compared original and linked startup disassembly','gcc -v confirms --enable-sjlj-exceptions; archived libgcc.a symbol search lacks cmshared'],
         'missing_artifact':'crtbegin.o and matching libgcc from the original c:/crossdev/b4.4.1-tdm-1/build-sjlj toolchain',
         'next_experiment':'Inspect archived Code::Blocks 10.05 MinGW runtime or exact TDM cross-build sources for cmshared; compare crtbegin.o before any broad relink.'},
        {'id':'B002','target':'Game timer.c full object/CU match',
         'current_evidence':'All 3 functions and complete 152-byte text contribution match at -O2/-O3; five volatile int commons inventoried.',
         'first_mismatch':{'section':'.debug_info','detail':'Historical source path/line/header layout not reproduced; no original .o available for direct record comparison.'},
         'hypotheses':['Reconstructed source/header layout accounts for debug differences','Common ordering must be established with all game objects'],
         'experiments_tried':['All five optimization levels','All text relocations resolved independently','All functions, symbols, section contributions and common allocations inventoried'],
         'missing_artifact':'Exact historical declarations/include/line configuration or original timer.o',
         'next_experiment':'Use CU source-file table and DIE graph to recover declarations and line placement, then compare debug contribution and common layout in a multi-CU link.'},
        {'id':'B003','target':'Allegro blit.c',
         'current_evidence':'5/7 exact function bodies at -O2. Full candidate text is 15894 bytes versus original 15890.',
         'first_mismatch':{'function':'masked_blit','address':'0x4561c8','detail':'Direct branch displacement differs because a later blit function is 4 bytes longer. blit first differing field at 0x456297; instruction-selection difference at original 0x4562ee (add versus lea).'},
         'hypotheses':['Compiler build/register allocation difference','Source/header expansion or compiler flags differ; simple length slicing was already corrected'],
         'experiments_tried':['-O0/-O1/-O2/-O3/-Os, all functions','DWARF body extents instead of next-symbol padding','Relocation targets and anonymous read-only data resolved independently'],
         'missing_artifact':'Exact compiler/header/flag combination for this CU',
         'next_experiment':'Compare -O2 assembly around add/lea selection with the original cross-built compiler; sweep scheduling and alignment flags separately.'},
        {'id':'B004','target':'Remaining game tree and library dependencies',
         'current_evidence':'25 historical CUs mapped; 3 loadpng files populated; libvorbis 1.2.0 and libogg 1.1.3 publisher-verified sources available.',
         'first_mismatch':None,
         'hypotheses':['libogg 1.1.3 source is the correct candidate','logg memory extension is local vendor code'],
         'experiments_tried':['Imported ownership/provenance and behavioral promotion evidence','Recovered complete timer.c before further isolated functions'],
         'missing_artifact':'GCC 4.2.1-sjlj for libogg; exact png/pthread headers/import libraries; logg extension; exact strptime/timecompat provenance; remaining game CUs',
         'next_experiment':'Assign existing recovered bodies to complete historical control.c and recover its missing entities; obtain old libogg compiler independently.'},
        {'id':'B005','target':'PE resources',
         'current_evidence':'Two leaves and complete directory metadata freshly parsed; payload hashes recorded.',
         'first_mismatch':None,'hypotheses':['ALLEGRO_ICON names a custom resource icon rather than the available shooter example'],
         'experiments_tried':['Compared source-tree ICO image hashes to RT_ICON payload; no match'],
         'missing_artifact':'Original icon source/resource script and historical resource timestamp rules',
         'next_experiment':'Supply/extract the icon as a local user-owned fixture, compile a structural .rc with locked windres and compare resource directory ordering and timestamps.'},
    ]
    blockers[0].update(status='RESOLVED_FOR_STARTUP_TEXT',
        current_evidence='TDM-2 crt2.o and crtbegin.o text including padding match after independently resolved relocations. Eight startup starts/spans match, 792 bytes.',
        missing_artifact=None,
        next_experiment='Validate remaining runtime contributions as the game link grows; exact compiler distribution identity remains unproven.')
    blockers[0]['historical_first_mismatch']=blockers[0].pop('first_mismatch')
    blockers[0]['experiments_tried'].append('Imported hash-pinned TDM-2; compared both startup COFF objects and a real synthetic link')
    blockers[3].update(current_evidence='Complete timer/control text (18 functions, 902 bytes); all 114 Allegro core CUs built and linked with both recovered CUs.',
        next_experiment='Recover complete beta.c next to extend the natural game prefix; resolve remaining vendor dependencies.')
    blockers[3]['current_evidence']='Complete beta/control/directories/particle/stars/timer and ambiguous csv text; all 114 Allegro core CUs build and link with six historical game-tree CUs. particle and its exact main.c new_rand dependency link in the separate custom-audio PE.'
    blockers[3]['next_experiment']='All 22 Xiph CUs build and link with exact-text logg; custom dependencies now resolve in a synthetic PE. Compare Xiph code and recover remaining main CUs before natural integration.'
    blockers[3]['missing_artifact']='GCC 4.2.1-sjlj for libogg; exact png/pthread headers/import libraries; exact strptime/timecompat provenance; remaining game CUs'
    custom=reports['game-custom']
    blockers.append({'id':'B007','target':'custom.c complete text',
        'current_evidence':str(custom['function_matches'])+'/10 exact function bodies; initialized data checked separately; dependencies resolve in the separate synthetic custom-audio PE. load_character_bmp is behaviorally reconstructed at 1993 bytes against 1992 original bytes. DWARF confirms its nested error buffers, color-conversion block, frame-cropping block, and datafile block; the remaining mismatch is a one-byte code-generation/layout delta.',
        'first_mismatch':next(({'function':f['name'], 'detail':f['first_difference']} for f in custom['functions'] if f['status']!='FUNCTION_MATCH'),None),
        'experiments_tried':['Original DWARF function order and lexical scopes','Explicit fgets prefetch control flow','Historical Allegro inline draw_sprite expansion','All five optimization levels','DWARF lexical-scope and error-path audit: all three failure buffers and both image/datafile recovery blocks match original ownership; no missing semantic branch found.','Declaration placement preserved the 1993-byte candidate; an equivalent outer if (fp) form grew it to 2009 bytes and lost an additional exact body. The remaining extra byte is an alignment NOP at the second text-parser loop head.','Keeping the main image path outside a guarded initial scan but moving the open error after the frames branch grew the candidate to 2000 bytes and lost an additional exact body.'],
        'next_experiment':'Recover the historical branch source shape around the first file-open error from line/DWARF control scope, then compare it with the datafile fallback without changing locked build flags.',
        'missing_artifact':None})
    scroller=reports['game-scroller']
    blockers.append({'id':'B008','target':'scroller.c complete text',
        'current_evidence':str(scroller['function_matches'])+'/4 exact function bodies; scroll_scroller, restart_scroller and init_scroller match at -O2.',
        'first_mismatch':next(({'function':f['name'], 'detail':f['first_difference']} for f in scroller['functions'] if f['status']!='FUNCTION_MATCH'),None),
        'experiments_tried':['DWARF structure and lexical scopes','Original control-flow and signed-shift disassembly','Historical Allegro inline call ordering'],
        'next_experiment':'Match draw_scroller register allocation for its first vertical set_clip_rect argument sequence without changing source semantics.',
        'missing_artifact':None})
    game_map=reports['game-map']
    blockers.append({'id':'B009','target':'map.c complete text',
        'current_evidence':str(game_map['function_matches'])+'/5 exact function bodies; reset_map, is_solid and get_level match at -O2.',
        'first_mismatch':next(({'function':f['name'], 'detail':f.get('first_difference')} for f in game_map['functions'] if f['status']!='FUNCTION_MATCH'),None),
        'experiments_tried':['DWARF Tmap and Tfloor layouts','Original signed tile-row arithmetic','Historical compiler instruction selection for output edges'],
        'next_experiment':'Recover add_floor source and match getFloorData right-edge instruction selection without source-level workarounds.',
        'missing_artifact':None})
    beta=reports['game-beta']
    blockers.append({'id':'B006','target':'beta.c complete text and natural game prefix',
        'status':'RESOLVED_FOR_COMPLETE_TEXT',
        'current_evidence':'All seven functions and full 1141-byte text equal at -O2. The source guard i < 8 produces the original allocator decisions.',
        'historical_mismatch_report':'docs/experiments/game-beta-before-loader-fix.json',
        'experiments_tried':['All five optimization levels','Original source function order from DWARF','Checksum operand order and chained node assignments','Iterative and recursive cleanup forms; original matches explicit first-node free followed by loop'],
        'next_experiment':'Recover historical source line/header layout for debug equality.',
        'missing_artifact':None})
    write_json(ROOT/'docs/blockers.json',blockers)
    print(metrics)

if __name__=='__main__': main()
