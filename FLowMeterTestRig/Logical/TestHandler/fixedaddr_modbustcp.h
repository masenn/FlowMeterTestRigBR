#include <bur/plctypes.h>
#include <brsystem.h>
#include <stdint.h>
#include <stdbool.h>

#include "modbus.h"
#include "utils.h"
#include <AsMbTCPS.h>

#define HOLDING_ADDRESS_BASE 24576
#define COIL_ADDRESS_BASE 16384

#define REG_FLOW_ACTUAL 0x00
#define REG_FLOW_TARGET 0x01
#define REG_ACTIVE_DUT 0x02


#define REG_DUT_UP 0x10
#define REG_DUT_DOWN 0x12
#define REG_DUT_AMB 0x14
#define REG_DUT_SYS 0x16
#define REG_DUT_BATCH 0x18
#define REG_DUT_BATCHSN 0x19


#define COIL_BUFFER_SIZE 10

#define COIL_FLOW_CONTROLLER_ENABLE     0
#define COIL_ISOLATION_VALVE_ENABLE     1
#define COIL_PUMP_ENABLE                2
#define COIL_DUT1                       3
#define COIL_DUT2                       4
#define COIL_DUT3                       5
#define COIL_DUT4                       6
#define COIL_DUT5                       7
#define COIL_HEATER_ON                  8
#define COIL_HEATER_OFF                 9

void modbus_tcp_load_initial_states();
void update_modbus_tcp_fixed(DUT_Slot_t* dut);