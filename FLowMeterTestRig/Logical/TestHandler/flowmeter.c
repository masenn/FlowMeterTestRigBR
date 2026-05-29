#include "flowmeter.h"

static float get_float(uint16_t base_address, uint16_t* registers)
{
    uint32_t value = (registers[base_address+1] << 16) | (registers[base_address]);
    return *(float*)(&value);
}

void registers_to_flowmeter(uint16_t* registers, FlowMeter_t* dut)
{
    dut->VERSION = registers[1-1];
    dut->INFO_PN = registers[2-1];
    dut->BATCH_SN = registers[0x28-1];
    dut->BATCH = registers[0x29-1];

    dut->DEBUG_UP = get_float(0x1C - 1,registers);
    dut->DEBUG_DOWN = get_float(0x1E - 1,registers);
    dut->DEBUG_AMB = get_float(0x24 - 1,registers);

    dut->DEBUG_SYSTICK = get_float(0x20 - 1,registers);
}
