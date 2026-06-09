#include <bur/plctypes.h>
#include <brsystem.h>
#include <stdint.h>
#include <stdbool.h>

#include "modbustcp.h"
#include "modbus.h"

//SYSTEM REGS
_GLOBAL UINT target_flow;               // ADDRESS 0x01
_GLOBAL UINT modbus_flow_actual;        // ADDRESS 0x02
_GLOBAL UINT active_dut;                // ADDRESS 0x03

//DUT REGS
_GLOBAL UINT DUT_up_msb;                // ADDRESS 0x20
_GLOBAL UINT DUT_up_lsb;                // ADDRESS 0x21
_GLOBAL UINT DUT_down_msb;              // ADDRESS 0x22
_GLOBAL UINT DUT_down_lsb;              // ADDRESS 0x23
_GLOBAL UINT DUT_amb_msb;               // ADDRESS 0x24
_GLOBAL UINT DUT_amb_lsb;               // ADDRESS 0x25
_GLOBAL UINT DUT_sys_msb;               // ADDRESS 0x20
_GLOBAL UINT DUT_sys_lsb;               // ADDRESS 0x21

//SYSTEM COILS REGS
_GLOBAL BOOL modbus_enable_flow_controller;
_GLOBAL BOOL modbus_enable_isolation_valve;
_GLOBAL BOOL modbus_pump_enable;
_GLOBAL BOOL modbus_dut_solenoids[5];






void update_modbus_tcp_values()
{


}

void DUT_data_to_modbus_tcp(DUT_Slot_t* dut)
{
    
}