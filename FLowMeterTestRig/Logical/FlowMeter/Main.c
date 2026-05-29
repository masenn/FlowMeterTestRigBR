#include <bur/plc.h>
#include <bur/plctypes.h>
#include <drv_mbus.h>
#include <string.h>

unsigned long bur_heap_size = 0x2000;

//_LOCAL DUT_Slot_t duts[5];

_GLOBAL USINT	dut_registers[5][32];

typedef struct {
	USINT	VERSION;
	USINT	INFO_PN;
	REAL	INFO_FIRM_VER;
	USINT	MOD_ADDR;
	USINT	MOD_BAUD;
	USINT	MOD_TERM;
	
	REAL	DEBUG_UP;
	REAL	DEBUG_DOWN;
	REAL	DEBUG_AMB;
	
	
	USINT 	address;
	USINT 	registers[32];
} FlowMeter_t;

typedef struct {

	/* Modbus function blocks */
	MBMOpen_typ     MOpen;
	MBMClose_typ    MClose;
	MBMCmd_typ      MCmd;

	BOOL            fMOpen;
	BOOL            fMClose;
	BOOL            fMCmd;
	UINT            statusMOpen;
	UINT            statusMClose;
	UINT            statusMCmd;
	UINT           	timeout;
	UDINT           ident;
	STRING          device[32];
	STRING          mode[32];
	STRING          config[32];
	
	//DUT status
	BOOL            bConnected;
	BOOL            bError;
	UINT            errorCode;

	//Flow Meter Belonging to DUT
	FlowMeter_t flow_meter_dut;
} DUT_Slot_t;



_INIT void modbus_init(void)
{
	// init_DUT(&duts[0],"SL1.IF1.ST1.IF1.ST7.IF1",9);
	// init_DUT(&duts[1],"SL1.IF1.ST1.IF1.ST8.IF1",9);
	// init_DUT(&duts[2],"SL1.IF1.ST1.IF1.ST9.IF1",9);
	// init_DUT(&duts[3],"SL1.IF1.ST1.IF1.ST10.IF1",9);
	// init_DUT(&duts[4],"SL1.IF1.ST1.IF1.ST11.IF1",9);


}

_CYCLIC void modbus_cyclic(void)
{
	// int i;
	// for(i = 0; i < 5;i++) serve_DUT(&duts[i]);
}

_EXIT void modbus_exit(void)
{

}