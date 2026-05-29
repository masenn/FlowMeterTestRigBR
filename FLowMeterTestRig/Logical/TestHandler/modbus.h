#pragma once 

#include <bur/plc.h>
#include <bur/plctypes.h>
#include <drv_mbus.h>
#include <string.h>
#include "flowmeter.h"

// Default config shared across all DUTs
#define DUT_DEFAULT_TIMEOUT  1000
#define DUT_DEFAULT_ASCII    0
#define DUT_DEFAULT_MODE     "PHY=RS485/BD=38400/PA=N/DB=8/SB=1"
#define DUT_DEFAULT_CONFIG   ""


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

void init_DUT(DUT_Slot_t* dut, char* device_str,int address);
void serve_DUT(DUT_Slot_t* dut);

