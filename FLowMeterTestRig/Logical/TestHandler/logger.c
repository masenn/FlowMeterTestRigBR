#include "logger.h"

static File_t log;
static bool ready = false;

void init_data_logger(char* file_name)
{
    delete_file(file_name);
    log.file_name = file_name;
    int result = create_file(&log);
    if(!log.is_open) return;
    
    ready = true;
    return;
}

/**
 * @breif checks if file is open and initialized
 * @note is redundant right now, possibility for more checking
 */
bool is_ready()
{
    return ready && log.is_open;
}


