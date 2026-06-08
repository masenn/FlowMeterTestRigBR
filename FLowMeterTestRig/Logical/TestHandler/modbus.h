#pragma once 

#include <bur/plc.h>
#include <bur/plctypes.h>
#include <drv_mbus.h>
#include <string.h>
#include <stdbool.h>
#include "flowmeter.h"

// Default config shared across all DUTs
#define DUT_DEFAULT_TIMEOUT  1000
#define DUT_DEFAULT_ASCII    0
#define DUT_DEFAULT_MODE     "PHY=RS485/BD=38400/PA=N/DB=8/SB=1"
#define DUT_DEFAULT_CONFIG   ""

#define ERR_NONE			0
#define ERR_BUSY			65535


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

	uint32_t last_transmission;

	//Flow Meter Belonging to DUT
	FlowMeter_t flow_meter_dut;
} DUT_Slot_t;

typedef struct {
	uint16_t register_address;
	uint16_t number_regs;
	uint8_t function_code;
	uint16_t* write_data;
	uint16_t internal_cmd_id;
} Modbus_Cmd_t;

#define CMD_READ_HOLDING_REGS 		0x03
#define CMD_READ_INPUT_REGS 		0x04
#define CMD_WRITE_SINGLE_REGISTER	0x06

#define MODBUS_CMD_DEFAULT 		0x00
#define MODBUS_CMD_GETDEBUG 	0x01
#define MODBUS_CMD_HEATERON 	0x02
#define MODBUS_CMD_HEATEROFF	0x03
#define MODBUS_CMD_GETMETADATA	0x04

void init_DUT(DUT_Slot_t* dut, char* device_str,int address);
int serve_DUT(DUT_Slot_t* dut);
void set_modbus_cmd(uint16_t new_cmd);
bool data_is_stale(DUT_Slot_t* dut);
void mark_data_as_read(DUT_Slot_t* dut);