#include <bur/plctypes.h>
#include <brsystem.h>
#include <stdint.h>
#include <stdbool.h>

#include "modbustcp.h"
#include "modbus.h"
#include "utils.h"
#include <AsMbTCPS.h>

//SYSTEM REGS
_GLOBAL UINT target_flow;
_GLOBAL REAL flow_actual;      
_GLOBAL UINT active_dut;

_GLOBAL UINT modbus_target_flow;
_GLOBAL UINT modbus_flow_actual;

//internal for triggering changes
static uint16_t regs_current_state[NUMBER_SYSTEM_REGS], regs_previous_states[NUMBER_SYSTEM_REGS];

//DUT REGS
_GLOBAL UINT modbus_DUT_up_msb;                // ADDRESS 0x20
_GLOBAL UINT modbus_DUT_up_lsb;                // ADDRESS 0x21
_GLOBAL UINT modbus_DUT_down_msb;              // ADDRESS 0x22
_GLOBAL UINT modbus_DUT_down_lsb;              // ADDRESS 0x23
_GLOBAL UINT modbus_DUT_amb_msb;               // ADDRESS 0x24
_GLOBAL UINT modbus_DUT_amb_lsb;               // ADDRESS 0x25
_GLOBAL UINT modbus_DUT_sys_msb;               // ADDRESS 0x20
_GLOBAL UINT modbus_DUT_sys_lsb;               // ADDRESS 0x21

//SYSTEM COILS REGS
_GLOBAL BOOL enable_isolation_valve;
_GLOBAL BOOL enable_pump;
_GLOBAL BOOL dut_solenoids[5];
_GLOBAL BOOL enable_flow_controller;

//MODBUS TCP COILS 
//triggers for system coil
_GLOBAL BOOL modbus_enable_flow_controller;
_GLOBAL BOOL modbus_enable_isolation_valve;
_GLOBAL BOOL modbus_pump_enable;
_GLOBAL BOOL modbus_dut_solenoids[5];

_LOCAL INT output_monitor;

_GLOBAL UINT tcp_please;

// allowing for trigger logic rather than exact control
// modbus TCP registers are only readable from B&Rs side
static bool coil_previous_states[NUMBER_COILS],coil_current_states[NUMBER_COILS];

void update_modbus_tcp_values(DUT_Slot_t* active_dut)
{
    //READ ONLY DATA
    DUT_data_to_modbus_tcp(active_dut);
    //TODO try scaled to enabled two dec places
//    modbus_flow_actual = flow_actual > 0 ? (uint16_t)(int)flow_actual:0;
	modbus_flow_actual = 0xBEEF;		
    tcp_please = 0xBEEF;
	memset(&tcp_please,0xBEEF,sizeof(tcp_please));
    // UINT data_buf[128] = {0};
    // data_buf[0] = 0xBEEF;
    
    // struct mbSlWordPut test = {
    //     .startAddress = 102,
    //     .nrOfItems = 1,
    //     .station = "IF4.MODBUSSLAVE_1",
    //     .data = &data_buf,
    //     .enable = 1,
        
    // };
    // mbSlWordPut(&test);
    // output_monitor = test.status;
    // // READ/WRITE DATA

    //first reading in current states 
    coil_current_states[COIL_ISOLATION_VALVE_ENABLE] = modbus_enable_isolation_valve;
    coil_current_states[COIL_PUMP_ENABLE] = modbus_pump_enable;

    regs_current_state[REG_TARGET_FLOW] = modbus_target_flow;
    int i;
    for(i = COIL_DUT1; i < COIL_DUT1+5;i++)
    {
        coil_current_states[i] = modbus_dut_solenoids[i-COIL_DUT1];

    }

    // detecting changes in all of the coils
    for(i = 0; i < NUMBER_COILS; i++)
    {
        if(coil_previous_states[i] != coil_current_states[i])
        {
            switch (i)
            {
                case COIL_FLOW_CONTROLLER_ENABLE:
                    enable_flow_controller = coil_current_states[i];
                    break;
                case COIL_ISOLATION_VALVE_ENABLE:
                    enable_isolation_valve = coil_current_states[i];
                    break;
                case COIL_PUMP_ENABLE:
                    enable_pump = coil_current_states[i];
                    break;
                // apply the same logic for all duts
                case COIL_DUT1:
                case COIL_DUT2:
                case COIL_DUT3:
                case COIL_DUT4:
                case COIL_DUT5:
                    dut_solenoids[i] = coil_current_states[i];
                    break;
                default:
                    break;
            }
        }
        coil_previous_states[i] = coil_current_states[i];
    }

    for (i = 0; i < NUMBER_SYSTEM_REGS; i++)
    {
        if(regs_current_state[i] != regs_previous_states[i])
        {
            switch (i)
            {
                case REG_TARGET_FLOW:
                    target_flow = modbus_target_flow;
                    break;
            }
        }
        regs_previous_states[i] = regs_current_state[i];
    }

    // detecting changes in writeable values
    

}

void DUT_data_to_modbus_tcp(DUT_Slot_t* dut)
{
    FlowMeter_t meter = dut->flow_meter_dut;
    uint32_t up_val = get_ieee754(meter.DEBUG_UP);
    uint32_t down_val = get_ieee754(meter.DEBUG_DOWN);
    uint32_t amb_val = get_ieee754(meter.DEBUG_AMB);
    uint32_t sys_val = meter.DEBUG_SYSTICK;
    modbus_DUT_up_msb = get_u32_msb(up_val);
    modbus_DUT_up_lsb = get_u32_lsb(up_val);
    modbus_DUT_down_msb = get_u32_msb(down_val);
    modbus_DUT_down_lsb = get_u32_lsb(down_val);
    modbus_DUT_amb_msb = get_u32_msb(amb_val);
    modbus_DUT_amb_lsb = get_u32_lsb(amb_val);
}
