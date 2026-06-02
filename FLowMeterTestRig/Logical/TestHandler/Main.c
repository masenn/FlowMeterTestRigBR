/***** Header files *****/
#include <bur/plctypes.h>
#include <brsystem.h>
//#include "Global.h"
#include <fileio.h>
#include <stdbool.h>
#include <stdint.h>

#include "file.h"
#include "modbus.h"
#include "logger.h"
#include "timing.h"

#define STATE_GET_FIRM_VER 0
#define STATE_UPDATE_READINGS 1

_GLOBAL BOOL enable_isolation_valve;
_GLOBAL BOOL enable_pump;
_GLOBAL BOOL dut_solenoids[5];
_GLOBAL REAL flow_actual;
_GLOBAL INT	pump_output;
_GLOBAL UINT target_flow; 

DUT_Slot_t duts[5];
_LOCAL UDINT log_num;
_LOCAL UDINT test;
_LOCAL UDINT num_attempts;

Modbus_Cmd_t READ_DEBUG_REGS = {
	.function_code = CMD_READ_HOLDING_REGS,
	.number_regs = 0x10,
	.register_address = 0x1C,
	//NULL pointer for no write data
	.write_data = 0
};

System_Info_t sys_info = { 0 };

void modbus_init(void)
{
	init_DUT(&duts[0],"SL1.IF1.ST1.IF1.ST7.IF1",1);
	init_DUT(&duts[1],"SL1.IF1.ST1.IF1.ST8.IF1",1);
	init_DUT(&duts[2],"SL1.IF1.ST1.IF1.ST9.IF1",1);
	init_DUT(&duts[3],"SL1.IF1.ST1.IF1.ST10.IF1",1);
	init_DUT(&duts[4],"SL1.IF1.ST1.IF1.ST11.IF1",1);
}

void modbus_cyclic(void)
{
	int i;
	for(i = 0; i < 5;i++) serve_DUT(&duts[i]);
}

_INIT void init(void){
	init_data_logger("test_log.csv");
	modbus_init();
	set_modbus_cmd(&READ_DEBUG_REGS);
}

static uint16_t current_state;

/***** Cyclic part *****/
_CYCLIC void Cyclic(void)
{
	modbus_cyclic();

	if(log_num < 1000)
	{
		//if data is not stale, log to file
		if(!data_is_stale(&duts[2])) 
		{
			//logs data to the log 
			sys_info.flow_actual = flow_actual;
			sys_info.target_flow = target_flow;
			sys_info.date_time = get_time();
			log_data_point(&sys_info,&(duts[2].flow_meter_dut));
			mark_data_as_read(&duts[2]);
			log_num++;
		}
	}
}
