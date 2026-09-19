/* Synthetic program, never counted as recovered game code. Real recovered
 * control/timer CUs and genuine Allegro/Win32 libraries supply every callee.
 */
#include <allegro.h>
#include "control.h"
#include "timer.h"

int main(void)
{
    Tcontrol c;
    if (allegro_init() != 0) return 1;
    init_control(&c);
    if (install_timers() != -1) return 2;
    allegro_exit();
    return 0;
}
END_OF_MAIN()
