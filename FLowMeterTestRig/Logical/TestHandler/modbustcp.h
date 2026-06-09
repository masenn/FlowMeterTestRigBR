#pragma once

#include <bur/plctypes.h>
#include <brsystem.h>
#include <stdint.h>
#include <stdbool.h>
#include "modbus.h"
#define NUMBER_COILS 8

#define COIL_FLOW_CONTROLLER_ENABLE     0
#define COIL_ISOLATION_VALVE_ENABLE     1
#define COIL_PUMP_ENABLE                2
#define COIL_DUT1                       3
#define COIL_DUT2                       4
#define COIL_DUT3                       5
#define COIL_DUT4                       6
#define COIL_DUT5                       7

#define NUMBER_SYSTEM_REGS 8

#define REG_TARGET_FLOW                 0x1
#define REG_FLOW_ACTUAL                 0x2
#define REG_ACTIVE_DUT                  0x3

void update_modbus_tcp_values(DUT_Slot_t* active_dut);
