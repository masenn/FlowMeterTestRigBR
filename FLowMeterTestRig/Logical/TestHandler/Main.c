/***** Header files *****/
#include <bur/plctypes.h>
#include <brsystem.h>
//#include "Global.h"
#include <fileio.h>
#include <stdbool.h>
#include <stdint.h>

#include "file.h"
#include "modbus.h"

_GLOBAL BOOL enable_isolation_valve;
_GLOBAL BOOL enable_pump;
_GLOBAL BOOL dut_solenoids[5];
_GLOBAL REAL flow_actual;
_GLOBAL INT	pump_output;

DUT_Slot_t duts[5];
_LOCAL UDINT time_val;

void modbus_init(void)
{
	init_DUT(&duts[0],"SL1.IF1.ST1.IF1.ST7.IF1",9);
	init_DUT(&duts[1],"SL1.IF1.ST1.IF1.ST8.IF1",9);
	init_DUT(&duts[2],"SL1.IF1.ST1.IF1.ST9.IF1",9);
	init_DUT(&duts[3],"SL1.IF1.ST1.IF1.ST10.IF1",9);
	init_DUT(&duts[4],"SL1.IF1.ST1.IF1.ST11.IF1",9);
}

void modbus_cyclic(void)
{
	int i;
	for(i = 0; i < 1;i++) serve_DUT(&duts[i]);
}


_LOCAL INT test;
unsigned long file_pointer_ul;

_INIT void init(void){
	test = -67;
	char* file_name = "TestFile.csv";
	test = delete_file(file_name);
	File_t test_file = {
		.file_name = "TestFile.csv",
		.fp = 0,
		.is_open = false
	};
	test = create_file(&test_file);
	char* test_data = "col1,col2,col3\n1,2,3\n4,5,6\n";
	test = write_file(&test_file,test_data,27);
	test = close_file(&test_file);
	// test = close_file(&test_file);
	// test = create_file(file_name,file_pointer);
	modbus_init();
}

/***** Cyclic part *****/
_CYCLIC void Cyclic(void)
{
	modbus_cyclic();
	time_val = get_time();
}
