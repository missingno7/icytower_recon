## Next discriminator

The requested pointer-versus-index and exit-store discriminators are complete. The pointer form remains closer (922/923, first difference 14, 9 exact CU functions); both explicit-index forms are smaller and first differ at offset 8. Three store-placement variants and two `i = 0` placement variants collapse to the pointer control. See “Cursor and exit-store follow-up” below.

The next evidence-backed discriminator is to make outer `i` the input index, as the historical code does in ESI and commits to EBP-0x824, while retaining the original output-pointer/capacity loop shape. The old source spelling used `i` for input, but its saved effective result should be compared before a fresh compiler invocation. Stop if the candidate collapses to that saved output without bringing the historical spill ownership closer.
