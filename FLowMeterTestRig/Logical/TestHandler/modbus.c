#include "modbus.h"

// transmission to see if data has been read since last read
static uint32_t transmission_number;

static Modbus_Cmd_t cmd;

_LOCAL UINT selected_cmd_id;
static uint16_t DUMMY = 0;

void set_modbus_cmd(uint16_t new_cmd)
{
	selected_cmd_id = new_cmd;
	switch (selected_cmd_id) 
	{
		case MODBUS_CMD_DEFAULT:
			cmd.function_code    = CMD_READ_HOLDING_REGS;
			cmd.register_address = 0x01;
			cmd.number_regs      = 0x1F;
			cmd.write_data       = NULL;
			break;

		case MODBUS_CMD_GETDEBUG:
			cmd.function_code    = CMD_READ_HOLDING_REGS;
			cmd.register_address = 0x1C;
			cmd.number_regs      = 0x10;
			cmd.write_data       = NULL;
			break;

		case MODBUS_CMD_HEATERON:
			cmd.function_code    = CMD_WRITE_SINGLE_REGISTER;
			cmd.register_address = 0x101;
			cmd.number_regs      = 0x1;
			cmd.write_data       = &DUMMY;
			break;

		case MODBUS_CMD_HEATEROFF:
			cmd.function_code    = CMD_WRITE_SINGLE_REGISTER;
			cmd.register_address = 0x102;
			cmd.number_regs      = 0x1;
			cmd.write_data       = &DUMMY;
			break;
		default:
			/* unknown command - leave current_cmd unchanged or handle error */
			break;
	}
	return;

}

void init_DUT(DUT_Slot_t* dut, char* device_str,int address)
{
	memset(dut,0,sizeof(DUT_Slot_t));

	// Copy config strings
    strcpy(dut->device, device_str);
    strcpy(dut->mode,   DUT_DEFAULT_MODE);
    strcpy(dut->config, DUT_DEFAULT_CONFIG);

    // Timeouts and flags
    dut->timeout    = DUT_DEFAULT_TIMEOUT;

	/* Open Modbus connection */
	dut->MOpen.enable    = 1;
	dut->MOpen.pDevice   = (UDINT) &(dut->device[0]);
	dut->MOpen.pMode     = (UDINT) &(dut->mode[0]);
	dut->MOpen.pConfig   = 0;
	dut->MOpen.timeout   = dut->timeout;
	dut->MOpen.ascii     = 0;
	MBMOpen(&(dut->MOpen));
	
	dut->flow_meter_dut.address = address;
	int statusMOpen = dut->MOpen.status;
	if (!statusMOpen)
	{
		dut->ident       = dut->MOpen.ident;
	}
	else
	{
		dut->errorCode   = statusMOpen;
	}

	set_modbus_cmd(MODBUS_CMD_DEFAULT);
}

int serve_DUT(DUT_Slot_t* dut)
{

	dut->MCmd.enable     = 1;
	dut->MCmd.ident      = dut->ident;
	dut->MCmd.node       = dut->flow_meter_dut.address;
	dut->MCmd.data       = (UDINT) &(dut->flow_meter_dut.registers);
	// if write data, take write data, otherwise, place registers as the destination address
	dut->MCmd.data 		= 
		cmd.function_code == CMD_WRITE_SINGLE_REGISTER ? (UDINT)cmd.write_data:(UDINT) &(dut->flow_meter_dut.registers);
	dut->MCmd.mfc        = cmd.function_code;
	dut->MCmd.offset     = cmd.register_address;
	dut->MCmd.len        = cmd.number_regs;
	MBMCmd(&(dut->MCmd));
	int error_code = dut->MCmd.status;
	if (error_code == ERR_NONE)
	{
		//increment if transmission is successful
		dut->last_transmission = transmission_number;
		transmission_number++;
		switch (selected_cmd_id)
		{
			case MODBUS_CMD_GETDEBUG:
				debug_registers_to_flowmeter(&(dut->flow_meter_dut));
				break;
			case MODBUS_CMD_DEFAULT:
				registers_to_flowmeter(&(dut->flow_meter_dut));
				break;
			default:
				break;
		}
	}
	return error_code;
}

uint16_t get_current_modbus_cmd() 
{
	return selected_cmd_id;
}


/**
 * @brief checks if new data has been received since last read
 * @return true if no new tranmission occured (last_transmission == current_transmission
 */
bool data_is_stale(DUT_Slot_t* dut) {	return dut->last_transmission == transmission_number;	}

void mark_data_as_read(DUT_Slot_t* dut) { 	dut->last_transmission = transmission_number;	}
