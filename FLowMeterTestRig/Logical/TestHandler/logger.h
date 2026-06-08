
#include <bur/plctypes.h>
#include <brsystem.h>
#include "modbus.h"
#include "time.h"
#include "file.h"
#include <stdint.h>
#include <stdbool.h>
#include <asstring.h>
// #include <stdio.h>

typedef struct {
    uint32_t date_time;
    uint16_t target_flow;
    float flow_actual;
    float air_temp;
    float fluid_temp;
} System_Info_t;

void init_data_logger(char* file_name);
bool is_ready();
int write_test_data(uint32_t time, float current_flow);
int write_time();
// main entry point
void log_data_point(System_Info_t* system_info, FlowMeter_t* flow_info);
void log_all_meters(DUT_Slot_t* duts);

