#pragma once

#include <stdbool.h>

#define FILE_SYSTEM_NAME "USER"

#define ERR_FILE_MISSING	20708
#define ERR_NONE			0
#define ERR_BUSY			65535
#define ERR_GENERAL			20799
#define ERR_UNDEFINED		-1



typedef struct {
    char* file_name;
    unsigned long fp;
    bool is_open;
    unsigned long file_length;
    unsigned long write_offset;
} File_t;



bool file_exists(File_t* file);
/**
 * @brief opens a file on the local file system
 * @param file_name: the file name to be read, path included
 * @param fp: the file pointer to used to open the file
 */
int open_file(File_t* file);
int create_file(File_t* file);
int write_file(File_t* file,char* write_data,uint16_t write_len);
int close_file(File_t* file);
int delete_file(char* file_name);


