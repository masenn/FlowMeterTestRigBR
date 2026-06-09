#include "logger.h"

#define BUFFER_MAX 1024

#define BUFFER_READY 0

static File_t log;
static bool ready = false;
static char buffer[BUFFER_MAX];
static uint16_t buffer_pos;

_LOCAL STRING temp_str[80];
_LOCAL INT error;

void init_data_logger(char* file_name)
{
    while(delete_file(file_name) == ERR_BUSY);
    log.file_name = file_name;
    int result = create_file(&log);
    if(!log.is_open) return;
    // #define HEADER "DUT1,UP1,DOWN1,AMB321,SYS1,DUT2,UP2,DOWN2,AMB322,SYS2,DUT3,UP3,DOWN3,AMB323,SYS3,DUT4,UP4,DOWN4,AMB324,SYS4,DUT5,UP5,DOWN5,AMB325,SYS5\n"
    #define HEADER "target,flow_actual,UP,DOWN,AMB32,SYS\n"
    write_file(&log,HEADER,sizeof(HEADER)-1);
    buffer_pos = 0;
    ready = true;
    return;
}

static void add_u32_to_buf(uint32_t val)
{
    int length = brsitoa(val,(UDINT)&buffer[buffer_pos]);
    buffer_pos += length;
    if(buffer_pos >= BUFFER_MAX) buffer_pos = BUFFER_MAX - 1;
    return;
}

static void add_float_to_buf(float val) 
{
    int length = ftoa(val,(UDINT)&buffer[buffer_pos]);
    buffer_pos += length;
    if(buffer_pos >= BUFFER_MAX) buffer_pos = BUFFER_MAX - 1;
    return;
}

static void add_string_to_buf(char* str)
{
    int i = 0;
    for(;str[i] && buffer_pos < BUFFER_MAX - 1; i++) 
    {
        buffer[buffer_pos++] = str[i];
    }
}

static void add_u32_to_csv(uint32_t val)
{
    int length = brsitoa(val,(UDINT)&buffer[buffer_pos]);
    buffer_pos += length;
    if(buffer_pos >= BUFFER_MAX) buffer_pos = BUFFER_MAX - 1;
    add_string_to_buf(",");
    return;
}

static void add_float_to_csv(float val) 
{
    int length = ftoa(val,(UDINT)&buffer[buffer_pos]);
    buffer_pos += length;
    if(buffer_pos >= BUFFER_MAX) buffer_pos = BUFFER_MAX - 1;
    add_string_to_buf(",");
    return;
}

static void add_string_to_csv(char* str)
{
    int i = 0;
    for(;str[i] && buffer_pos < BUFFER_MAX - 1; i++) 
    {
        buffer[buffer_pos++] = str[i];
    }
    add_string_to_buf(",");
}

/**
 * @brief removes comma on final entry (backspace) and then writes new line
 */
static void end_csv_line() {     buffer_pos--;add_string_to_buf("\n");    }

/**
 * @brief Writes the contents of the buffer out and returns busy until buffer has been written
 * 
 */
static int write_buffer()
{
    // if data buffer is fresh
    if(buffer_pos == 0) 
    {
        //ready to write buffer
        return BUFFER_READY;
    }
    int result = write_file(&log,buffer,buffer_pos);
    if(result == ERR_NONE) buffer_pos = 0;
    return result;
}


/**
 * @breif checks if file is open and initialized
 * @note is redundant right now, possibility for more checking
 */
bool is_ready()
{
    return ready && log.is_open;
}

_LOCAL UDINT x;

void log_data_point(System_Info_t* system_info, FlowMeter_t* meter)
{
    // if the buffer is not busy and ready
    if(write_buffer() == BUFFER_READY) 
    {
        add_u32_to_csv(system_info->target_flow);
        add_float_to_csv(system_info->flow_actual);
        add_float_to_csv(meter->DEBUG_UP);
        add_float_to_csv(meter->DEBUG_DOWN);
        add_u32_to_csv(get_ieee754(meter->DEBUG_AMB));
        add_u32_to_csv(meter->DEBUG_SYSTICK);
        end_csv_line();

    }

}

void log_all_meters(DUT_Slot_t* duts) 
{
    // if the buffer is not busy and ready
    if(write_buffer() == BUFFER_READY) 
    {
        int i;
        for(i = 0; i < 5; i++)
        {
            add_u32_to_csv(i);
            add_float_to_csv(duts[i].flow_meter_dut.DEBUG_UP);
            add_float_to_csv(duts[i].flow_meter_dut.DEBUG_DOWN);
            //prevents the loss of digits
            add_u32_to_csv(get_ieee754(duts[i].flow_meter_dut.DEBUG_AMB));
            add_u32_to_csv(duts[i].flow_meter_dut.DEBUG_SYSTICK);
        }
        end_csv_line();

    }
}