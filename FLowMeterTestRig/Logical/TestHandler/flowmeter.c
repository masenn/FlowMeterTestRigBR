#include "flowmeter.h"

static uint32_t get_u32t(uint16_t base_address, uint16_t* registers) 
{
    return ((uint32_t)registers[base_address+0] << 16) | (registers[base_address+1]);
}

static float get_float(uint16_t base_address, uint16_t* registers)
{
    uint32_t value = get_u32t(base_address,registers);
    return *(float*)(&value);
}

void registers_to_flowmeter(FlowMeter_t* dut)
{
    dut->VERSION = dut->registers[1-1];
    dut->INFO_PN = dut->registers[2-1];
    dut->INFO_FIRM_VER = get_float(0x04-1,dut->registers);
    dut->BATCH_SN = dut->registers[0x28-1];
    dut->BATCH = dut->registers[0x29-1];

    dut->DEBUG_UP = get_float(0x1C - 1,dut->registers);
    dut->DEBUG_DOWN = get_float(0x1E - 1,dut->registers);
    dut->DEBUG_AMB = get_float(0x24 - 1,dut->registers);

    dut->DEBUG_SYSTICK = get_u32t(0x26 - 1,dut->registers);
}
