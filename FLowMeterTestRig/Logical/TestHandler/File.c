#include <bur/plctypes.h>
#include <brsystem.h>
//#include "Global.h"
#include <fileio.h>
#include <stdbool.h>
#include <stdint.h>

#include "File.h"


static int get_error_code(int wStatus)
{
	if (wStatus == ERR_FILE_MISSING)
	{
		return ERR_FILE_MISSING;
	}
	else if (wStatus == ERR_NONE)
	{
		return ERR_NONE;
	}
	else if (wStatus != ERR_BUSY)
	{
		if (wStatus == ERR_GENERAL)
		{
			return FileIoGetSysError();
		}
	}
	return wStatus;
}

//TODO implement
// static int get_file_length(File_t* file)
// {
//     if(!file->is_open) return -1;
//     FileRead_typ file_read = {0};
//     file_read.enable = 1;
//     file_read.ident    = file->fp;
// 	file_read.offset   = 0;
// 	file_read.pDest     = (UDINT) write_data;
// 	file_read.len      = write_len;
// }

bool file_exists(File_t* file) 
{
	FileOpen_typ file_open = {0};
	/* Initialize file open structrue */
	file_open.enable = 1;
	file_open.pDevice = (UDINT)FILE_SYSTEM_NAME;
	file_open.pFile = (UDINT)file->file_name;
	file_open.mode = fiREAD_ONLY;                        /* Read and write access */
	/* Call FUB */
	FileOpen(&file_open);
	bool ret = (file_open.status != ERR_FILE_MISSING && file_open.status == 0 );
	if(ret) close_file(&(file_open.ident));
	return ;
}

/**
 * @brief opens a file on the local file system
 * @param file_name: the file name to be read, path included
 * @param fp: the file pointer to used to open the file
 */
int open_file(File_t* file)
{

	FileOpen_typ file_open = {0};
	/* Initialize file open structrue */
	file_open.enable = 1;
	file_open.pDevice = (UDINT)FILE_SYSTEM_NAME;
	file_open.pFile = (UDINT)file->file_name;
	file_open.mode = fiREAD_WRITE;                        /* Read and write access */

	/* Call FUB */
	FileOpen(&file_open);

	/* Get FBK output information */
	file->file_name = file_open.ident;
    if (file_open.status == 0) file->is_open = true;
	return get_error_code(file_open.status);
	
}

int create_file(File_t* file)
{
	FileCreate_typ file_create = { 0 };
	/* Initialize file create structure */
	file_create.enable    = 1;
	file_create.pDevice = (UDINT) FILE_SYSTEM_NAME;
	file_create.pFile   = (UDINT) file->file_name;
	/* Call FUB */
	FileCreate(&file_create);
	/* Get output information of FBK */
	file->fp = file_create.ident;
    if (file_create.status == 0) file->is_open = true;
	return get_error_code(file_create.status);
}

int write_file(File_t* file, char* write_data,uint16_t write_len) 
{
	FileWrite_typ file_write = {0};
	file_write.enable     = 1;
	// dereference the pointer to the file
	file_write.ident    = file->fp;
	file_write.offset   = 0;
	file_write.pSrc     = (UDINT) write_data;
	file_write.len      = write_len;

	/* Call FBK */
	FileWrite(&file_write);
	return get_error_code(file_write.status);
}

int close_file(File_t* file)
{
    if(!file->is_open) return -1;
	/* Initialize file close structure */
	FileClose_typ file_close = {0};
	file_close.enable     = 1;
	file_close.ident    = file->fp;
    
	/* Call FBK */
	FileClose(&file_close);
    file->is_open = false;
    return get_error_code(file_close.status);
}

int delete_file(char* file_name)
{
	FileDelete_typ file_delete;
	/* Initialize file delete structure */
	file_delete.enable    = 1;
	file_delete.pDevice = (UDINT) FILE_SYSTEM_NAME;
	file_delete.pName   = (UDINT) file_name;
	/* Call FBK */
	FileDelete(&file_delete);
	return get_error_code(file_delete.status);
}