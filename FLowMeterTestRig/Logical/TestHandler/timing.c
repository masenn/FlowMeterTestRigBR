#include "timing.h"

_LOCAL DTGetTime_typ time;


uint32_t get_time()
{
    time.enable = 1;
    DTGetTime(&time);
    return time.DT1;
}