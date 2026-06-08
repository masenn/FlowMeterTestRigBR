#pragma once

#include <bur/plctypes.h>
#include <brsystem.h>
#include <stdint.h>

void init_flow_controller(uint8_t active_dut, uint16_t min, uint16_t max, uint16_t inc, uint16_t n);
void flow_controller_cyclic();
void deinit_flow_controller();
void ping_flow_controller();
bool flow_controller_initialized();