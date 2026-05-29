
#include <bur/plctypes.h>
#include <brsystem.h>
#include "modbus.h"
#include "time.h"
#include "file.h"
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t date_time;
    uint16_t target_flow;
    float current_flow;
    float air_temp;
    float fluid_temp;
} System_Info_t;

void init_data_logger(char* file_name);
bool is_ready();
// main entry point
void log_data_point();

