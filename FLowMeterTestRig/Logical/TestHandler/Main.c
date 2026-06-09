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
#include "flowcontroller/flowcontroller.h"

#define STATE_WRITE_META_DATA
#define STATE_UPDATE_READINGS 1

_GLOBAL BOOL enable_isolation_valve;
_GLOBAL BOOL enable_pump;
_GLOBAL BOOL dut_solenoids[5];
_GLOBAL BOOL enable_flow_controller;

_GLOBAL REAL flow_actual;
_GLOBAL INT	pump_output;
_GLOBAL UINT target_flow; 

_GLOBAL BOOL send_heater_on;
_GLOBAL BOOL send_heater_off;
_GLOBAL BOOL reset_log;
_GLOBAL BOOL flow_meter_power_en;


_LOCAL INT active_dut;


DUT_Slot_t duts[5];
_GLOBAL INT dut_okay[5];

_LOCAL UDINT log_num;
_LOCAL UDINT test;
_LOCAL UDINT num_attempts;

System_Info_t sys_info = { 0 };

_LOCAL UINT current_state;

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
	for(i = 1; i < 2;i++)
	{
		int err = serve_DUT(&duts[i]);
		dut_okay[i] = !(err != 0 && err != 65535);
	} 
}

_INIT void init(void)
{
	flow_meter_power_en = 1;
	init_data_logger("test_log.csv");
	modbus_init();
	active_dut = 1;
}

/***** Cyclic part *****/
_CYCLIC void Cyclic(void)
{
	if (send_heater_off) set_modbus_cmd(MODBUS_CMD_HEATEROFF);
	else if (send_heater_on) set_modbus_cmd(MODBUS_CMD_HEATERON);
	else set_modbus_cmd(MODBUS_CMD_GETDEBUG);
	modbus_cyclic();
	if(enable_flow_controller) 
	{
		if (!flow_controller_initialized()) 
		{
			init_flow_controller(active_dut,300,2500,25,10);
		}
		flow_controller_cyclic();
	}

	if(log_num < 80000 && !send_heater_on && !send_heater_off && enable_flow_controller)
	{
		//if data is not stale, log to file
		if(!data_is_stale(&duts[active_dut])) 
		{
			//logs data to the log 
			sys_info.flow_actual = flow_actual;
			sys_info.target_flow = target_flow;
			sys_info.date_time = get_time();
			log_data_point(&sys_info,&(duts[active_dut].flow_meter_dut));
			mark_data_as_read(&duts[active_dut]);
			//pings the flow controller to incremenent and if # of reads is enough, continue to next flow
			ping_flow_controller();
			log_num++;
		}
		// // if(!data_is_stale(&duts[0]))
		// {
		// 	log_all_meters(duts);
		// 	mark_data_as_read(&duts[0]);
		// 	log_num++;
		// }
	}




}
