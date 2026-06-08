#include <bur/plctypes.h>
#include <brsystem.h>
#include <stdint.h>
#include <stdbool.h>

_GLOBAL BOOL enable_isolation_valve;
_GLOBAL BOOL enable_pump;
_GLOBAL BOOL dut_solenoids[5];
_GLOBAL REAL flow_actual;
_GLOBAL INT	pump_output;
_GLOBAL UINT target_flow; 
_GLOBAL BOOL enable_flow_controller;

_LOCAL INT active_dut;

//params
static uint16_t min_flow,max_flow,increment,n_points;

//current state information
static uint16_t n_read = 0;
static bool is_initialized = 0;

void init_flow_controller(uint8_t active_dut, uint16_t min, uint16_t max, uint16_t inc, uint16_t n)
{
    dut_solenoids[4-active_dut] = 1;
    enable_isolation_valve = 1;

    min_flow = min;
    max_flow = max;
    increment = inc;
    n_points = n;
    n_read = 0;
    is_initialized = 1;
    enable_pump = 1;

}

void flow_controller_cyclic()
{
    //TODO implement harder interrupt
    // if(!enable_flow_controller) 
    // {
    //     enable_pump = 0;
    //     enable_flow_controller = 0;
    //     return;
    // }
    if(n_read > n_points - 1) 
    {
        //updating flow rate and resetting state
        n_read = 0;
        //if next point is out of range, move to minimum flow
        target_flow = (target_flow+increment) > max_flow ? min_flow : target_flow+increment;
    }

}

void deinit_flow_controller()
{
    dut_solenoids[active_dut] = 0;
    enable_isolation_valve = 0;
    enable_pump = 0;
    is_initialized = 0;
}

// 
void ping_flow_controller() {   if(is_initialized) n_read ++;   }

bool flow_controller_initialized() {    return is_initialized;  }