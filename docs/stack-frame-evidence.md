# Stack-frame diagnostics

A decoded constant SUB ESP in the straight-line entry prefix can identify an
allocation mismatch without attributing it to register selection. The classifier
uses STACK_FRAME_LAYOUT only when that instruction is the first mismatch. Calls,
branches and late adjustments end the bounded prologue scan.

The initial real examples include main_menu_callback (620 original versus 556
candidate bytes reserved), draw_profile_selector (188 versus 124), and
profile_data_page_general (428 versus 460). The latter has a separately evidenced
80-byte original buf versus a 100-byte candidate buf. This is not a complete frame
accounting identity: spills, outgoing arguments, alignment and lifetime reuse can
also contribute. Current values live in function cards, not this historical note.

The local declaration workflow corrected main_menu_callback's scroller_step to
const int and preserved emitted code. Its allocation mismatch remained. This
negative causal observation prevents a correct local-type fact from being mistaken
for a complete source fix. The accepted attempt is recorded in
`docs/attempts/interfaces/decl_main_main_menu_callback_scroller_step.jsonl`.

Do not tune registers, add padding, or alter compiler flags just to match allocation.
Use the attached local widths, original/candidate DWARF locations and called
interfaces to form a bounded source hypothesis. Exact promotion still requires all
function bytes, independently resolved relocations and decoded direct targets.
