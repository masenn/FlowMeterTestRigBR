/* Automation Studio generated header file */
/* Do not edit ! */

#ifndef _BUR_1779814470_1_
#define _BUR_1779814470_1_

#include <bur/plctypes.h>

/* Datatypes and datatypes of function blocks */
typedef struct Data_Point_t
{	float up_voltage;
	float down_voltage;
	float amb_voltage;
	unsigned short systick;
	unsigned char batch;
	unsigned char batch_sn;
} Data_Point_t;






__asm__(".section \".plc\"");

/* Used IEC files */
__asm__(".ascii \"iecfile \\\"Logical/Global.typ\\\" scope \\\"global\\\"\\n\"");

/* Exported library functions and function blocks */

__asm__(".previous");


#endif /* _BUR_1779814470_1_ */

