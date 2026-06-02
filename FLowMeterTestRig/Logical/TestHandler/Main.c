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
#include "time.h"

_GLOBAL BOOL enable_isolation_valve;
_GLOBAL BOOL enable_pump;
_GLOBAL BOOL dut_solenoids[5];
_GLOBAL REAL flow_actual;
_GLOBAL INT	pump_output;

DUT_Slot_t duts[5];
_LOCAL UDINT time_val;

_LOCAL UDINT log_num;

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


_LOCAL UDINT test;
_LOCAL UDINT num_attempts;
_LOCAL STRING test_str[80];
unsigned long file_pointer_ul;

_INIT void init(void){
	init_data_logger("test_log.csv");
	modbus_init();
}

/***** Cyclic part *****/
_CYCLIC void Cyclic(void)
{
	modbus_cyclic();
	if(log_num < 1000)
	{
		num_attempts++;
		//temp null pointer to system info
		log_data_point(0,&(duts[1].flow_meter_dut));
		if(test == ERR_NONE) log_num++;
	}
}
