/***** Header files *****/
#include <bur/plctypes.h>
#include <brsystem.h>
//#include "Global.h"
#include <fileio.h>
#include <stdbool.h>
#include <stdint.h>

#include "File.h"
#include "modbus.h"


_LOCAL DUT_Slot_t duts[5];

_GLOBAL USINT	dut_registers[5][32];

static void modbus_init(void)
{
	init_DUT(&duts[0],"SL1.IF1.ST1.IF1.ST7.IF1",9);
	init_DUT(&duts[1],"SL1.IF1.ST1.IF1.ST8.IF1",9);
	init_DUT(&duts[2],"SL1.IF1.ST1.IF1.ST9.IF1",9);
	init_DUT(&duts[3],"SL1.IF1.ST1.IF1.ST10.IF1",9);
	init_DUT(&duts[4],"SL1.IF1.ST1.IF1.ST11.IF1",9);
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
}

/***** Cyclic part *****/
_CYCLIC void Cyclic(void)
{
	
//	
}