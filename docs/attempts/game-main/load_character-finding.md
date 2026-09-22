# load_character: identical instructions, one register permutation, and where it comes from

`load_character` (0x40fe78, 330 bytes) compiles to exactly the historical size, exactly 92
instructions, with every relocation resolving equal.  Thirteen bytes differ, at offsets 13, 16, 24,
41, 53, 59, 67, 138, 202, 206, 248, 254 and 258, and every one of them is a ModRM register field.

The original's own DWARF location lists say precisely what the permutation is:

    filename   offsets   0..31   (none)
               offsets  31..58   register esi
               offsets  58..330  MEMORY at ebp+8
    name       offsets  25..36   ebx      36..66  eax      66..87, 91..289, 293..330  ebx

So historically the incoming parameter is held in `esi` only long enough to pass it to `sprintf`,
and from offset 58 onwards every further use re-reads it from its own incoming stack slot at
`ebp+8`, which frees `esi` for the address of `buf`.  Our build instead keeps `filename` in a
callee-saved register across the whole body and gives `buf` a fresh register, and the choice
cascades through every later reference to `name` and `filename`.

Four source rewrites were tried and every one produced byte-identical output, so none of them
reaches the cause: swapping the declaration order of `count` and `name`; the
declaration-with-initialiser form `char *name = get_filename(filename);`; hoisting `char buf[1024]`
to function scope; and splitting `(attrib & FA_DIREC) && *name != '.'` into nested `if`s.  GCC's
front end normalises all four to the same GIMPLE.

Ruled out by evidence rather than by assumption: it is not a wrong symbol or index (all
relocations equal), not a `<`/`<=` or signedness error, and not a swapped `&&` order -- the
original evaluates `testb $0x10,0xc(%ebp)` before `cmpb $0x2e,(%eax)`, the same order as ours.
The DWARF local set also matches ours exactly: `static int count` at 0x4dd330, `char *name`, and
`char buf[1024]` at `fbreg -1056` inside one lexical block.

What remains is that the same compiler, from the same flags, chose to spill a parameter to its home
slot where we keep it in a register.  That is a register-pressure decision, so the source difference
being looked for is one that makes the original's body need one more register than ours across
offsets 58..330, not a difference in this statement sequence -- which is identical.  Anyone picking
this up should look for a value the original keeps live across that span that our source never
computes, rather than re-testing surface rewrites of the statements that are already right.
