#include <bur/plc.h>
#include <bur/plctypes.h>
#include <stdint.h>

typedef struct {
	uint16_t	VERSION;
	uint16_t	INFO_PN;
	float	    INFO_FIRM_VER;
	uint16_t	MOD_ADDR;
	uint16_t	MOD_BAUD;
	uint16_t	MOD_TERM;
    uint16_t    BATCH;
    uint16_t    BATCH_SN;

	float	    DEBUG_UP;
	float	    DEBUG_DOWN;
	float	    DEBUG_AMB;
	
    uint32_t    DEBUG_SYSTICK;
	
	uint16_t 	address;
	uint16_t 	registers[32];
} FlowMeter_t;

void registers_to_flowmeter(uint16_t* registers, FlowMeter_t* flowmeter);
