
#include <bur/plctypes.h>

#ifdef _DEFAULT_INCLUDES
	#include <AsDefault.h>
#endif

#define CYCLIC_PERIOD 100

_GLOBAL UDINT uw_tick;



void _INIT ProgramInit(void)
{
	uw_tick = 0; 
}

void _CYCLIC ProgramCyclic(void)
{
	uw_tick += CYCLIC_PERIOD;
}

void _EXIT ProgramExit(void)
{

}

