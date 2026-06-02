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
    #define HEADER "VER,UP,DOWN,AMB,SYS\n"
    write_file(&log,"VER,UP,DOWN,AMB,SYS\n",sizeof(HEADER)-1);
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
 * Writes the contents of the buffer out and returns busy until buffer has been written
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

int write_test_data(uint32_t time, float current_flow)
{
    // if data buffer is fresh
    if(buffer_pos == 0) 
    {
        add_u32_to_buf(time);
        add_string_to_buf(",");
        add_float_to_buf(current_flow);
        add_string_to_buf("\n");
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
        add_float_to_csv(meter->INFO_FIRM_VER);
        add_float_to_csv(meter->DEBUG_UP);
        add_float_to_csv(meter->DEBUG_DOWN);
        add_float_to_csv(meter->DEBUG_AMB);
        add_u32_to_csv(meter->DEBUG_SYSTICK);
        add_string_to_buf("EOL\n");
    }

}
