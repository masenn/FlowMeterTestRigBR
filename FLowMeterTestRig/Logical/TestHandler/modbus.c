#include "modbus.h"

_LOCAL DUT_Slot_t duts[5];

_GLOBAL USINT	dut_registers[5][32];




void init_DUT(DUT_Slot_t* dut, const char* device_str,int address)
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

}

void serve_DUT(DUT_Slot_t* dut)
{
		
	/* Reopen if requested */
	if (dut->fMOpen)
	{
		dut->MOpen.enable    = 1;
		dut->MOpen.pDevice   = (UDINT) &(dut->device[0]);
		dut->MOpen.pMode     = (UDINT) &(dut->mode[0]);
		dut->MOpen.pConfig   = 0;
		dut->MOpen.timeout   = dut->timeout;
		dut->MOpen.ascii     = 0;
		MBMOpen(&(dut->MOpen));
		int statusMOpen = dut->MOpen.status;
		if (!statusMOpen)
		{
			dut->ident       = dut->MOpen.ident;
			dut->bConnected  = 1;
			dut->bError      = 0;
			dut->fMOpen      = 0;
			dut->fMCmd       = 0;
			dut->fMClose     = 0;
		}
		else
		{
			dut->ident       = 0;
			dut->bConnected  = 0;
			dut->fMOpen      = 0;
		}
	}

	else if (1)
	{
		dut->MCmd.enable     = 1;
		dut->MCmd.ident      = dut->ident;
		dut->MCmd.mfc        = 4;                    						/* Read Input Registers */
		dut->MCmd.node       = dut->flow_meter_dut.address;					/* Slave address */
		dut->MCmd.data       = (UDINT) &(dut->flow_meter_dut.registers);
		dut->MCmd.offset     = 1;
		dut->MCmd.len        = 31;
		MBMCmd(&(dut->MCmd));
		int statusMCmd = dut->MCmd.status;
		if (!statusMCmd)
		{
			dut->fMCmd   = 1;
			dut->bError  = 0;
		}
		else if (dut->statusMCmd == 65535)           /* ERR_FUB_BUSY */
		{
			dut->fMCmd   = 1;
		}
		else
		{
			dut->bError      = 1;
			dut->errorCode   = statusMCmd;
			dut->fMCmd       = 0;
		}
	}

	/* Close connection if requested */
	if (dut->fMClose)
	{
		dut->fMClose     = 0;
		dut->bConnected  = 0;
		dut->MClose.enable   = 1;
		dut->MClose.ident    = dut->ident;
		MBMClose(&(dut->MClose));
		int statusMClose = dut->MClose.status;
		if (!dut->statusMClose)
		{
			dut->ident   = 0;
			dut->fMOpen  = 0;
			dut->fMCmd   = 0;
		}
	}
}