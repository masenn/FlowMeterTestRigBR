/* Automation Studio generated header file */
/* Do not edit ! */

#ifndef _BUR_1779371383_2_
#define _BUR_1779371383_2_

#include <bur/plctypes.h>

/* Constants */
#ifdef _REPLACE_CONST
#else
#endif


/* Variables */
_GLOBAL signed short FlowPumpFlowINT;
_GLOBAL unsigned short gDUT1_rxbuf[32];
_GLOBAL plcbit LiftPumpEN;
_GLOBAL plcbit cmdFlowPumpEN;
_GLOBAL float TargetFlow;
_GLOBAL signed short FluidTemp;
_GLOBAL float FluidTempFloat;
_GLOBAL signed short AirTemp;
_GLOBAL float AirTempFloat;
_GLOBAL float Cori_Measurement;
_GLOBAL float ActiveFlowMeterMeasurement;
_GLOBAL signed short PumpOut;





__asm__(".section \".plc\"");

/* Used IEC files */
__asm__(".ascii \"iecfile \\\"Logical/Global.var\\\" scope \\\"global\\\"\\n\"");

/* Exported library functions and function blocks */

__asm__(".previous");


#endif /* _BUR_1779371383_2_ */

