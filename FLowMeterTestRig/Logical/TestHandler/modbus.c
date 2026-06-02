#include "modbus.h"

// transmission to see if data has been read since last read
static uint32_t transmission_number;

static Modbus_Cmd_t* cmd;

static Modbus_Cmd_t default_cmd = {
	.function_code = CMD_READ_HOLDING_REGS,
	.register_address = 0x01,
	.number_regs = 0x1F,
	// NULL POINTER because write data isn't needed
	.write_data = 0
};

void init_DUT(DUT_Slot_t* dut, char* device_str,int address)
{
	memset(dut,0,sizeof(DUT_Slot_t));

	// Copy config strings
    strcpy(dut->device, device_str);
    strcpy(dut->mode,   DUT_DEFAULT_MODE);
    strcpy(dut->config, DUT_DEFAULT_CONFIG);

    // Timeouts and flags
    dut->timeout    = DUT_DEFAULT_TIMEOUT;
    dut->fMCmd      = 1;
    dut->bConnected = 0;
    dut->bError     = 0;

	dut->fMOpen      = 0;
	dut->fMCmd       = 0;
	dut->fMClose     = 0;

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
		dut->bConnected  = 1;
	}
	else
	{
		dut->bError      = 1;
		dut->errorCode   = statusMOpen;
	}

	cmd = &default_cmd;
}

int serve_DUT(DUT_Slot_t* dut)
{

	dut->MCmd.enable     = 1;
	dut->MCmd.ident      = dut->ident;
	dut->MCmd.node       = dut->flow_meter_dut.address;
	dut->MCmd.data       = (UDINT) &(dut->flow_meter_dut.registers);
	// if write data, take write data, otherwise, 
	dut->MCmd.data 		= 
		cmd->function_code == CMD_WRITE_SINGLE_REGISTER ? (UDINT)cmd->write_data:(UDINT) &(dut->flow_meter_dut.registers);
	dut->MCmd.mfc        = cmd->function_code;
	dut->MCmd.offset     = cmd->register_address;
	dut->MCmd.len        = cmd->number_regs;
	MBMCmd(&(dut->MCmd));
	int error_code = dut->MCmd.status;
	if (error_code == ERR_NONE)
	{
		//increment if transmission is successful
		dut->last_transmission = transmission_number;
		transmission_number++;
		debug_registers_to_flowmeter(&(dut->flow_meter_dut));
	}
	return error_code;
}

void set_modbus_cmd(Modbus_Cmd_t* new_cmd)
{
	cmd = new_cmd;
}

void set_modbus_default_cmd()
{
	cmd = &default_cmd;
}

/**
 * @brief checks if new data has been received since last read
 * @return true if no new tranmission occured (last_transmission == current_transmission
 */
bool data_is_stale(DUT_Slot_t* dut) {	return dut->last_transmission == transmission_number;	}

void mark_data_as_read(DUT_Slot_t* dut) { 	dut->last_transmission = transmission_number;	}
