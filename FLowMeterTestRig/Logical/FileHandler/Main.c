/***** Header files *****/
#include <bur/plctypes.h>
#include <brsystem.h>
//#include "Global.h"
#include <fileio.h>
#include <stdbool.h>


#define ERR_FILE_MISSING	20708
#define ERR_NONE			0
#define ERR_BUSY			65535
#define ERR_GENERAL			20799
#define ERR_UNDEFINED		-1

#define FILE_SYSTEM_NAME "USER"

int test = 0;


int get_error_code(int wStatus)
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

bool file_exists(char* file_name) 
{
	FileOpen_typ file = {0};
	/* Initialize file open structrue */
	file.enable = 1;
	file.pDevice = (UDINT)FILE_SYSTEM_NAME;
	file.pFile = (UDINT)file_name;
	file.mode = fiREAD_ONLY;                        /* Read and write access */

	/* Call FUB */
	FileOpen(&file);
	return (file.status != ERR_FILE_MISSING && file.status == 0 );
}

/**
 * @brief opens a file on the local file system
 * @param file_name: the file name to be read, path included
 * @param fp: the file pointer to used to open the file
 */
int open_file(char* file_name, UDINT* fp)
{

	FileOpen_typ file = {0};
	/* Initialize file open structrue */
	file.enable = 1;
	file.pDevice = (UDINT)FILE_SYSTEM_NAME;
	file.pFile = (UDINT)file_name;
	file.mode = fiREAD_WRITE;                        /* Read and write access */

	/* Call FUB */
	FileOpen(&file);

	/* Get FBK output information */
	*fp = file.ident;
	return get_error_code(file.status);
	
}

int create_file(char* file_name,UDINT* fp)
{
	FileCreate_typ file_create = { 0 };
	/* Initialize file create structure */
	file_create.enable    = 1;
	file_create.pDevice = (UDINT) "USER";
	file_create.pFile   = (UDINT) "TestFile.csv";
	/* Call FUB */
	FileCreate(&file_create);
	/* Get output information of FBK */
	*fp = file_create.ident;
	return get_error_code(file_create.status);
}

int write_file(char* file_name,UDINT*fp, char* write_data,USINT write_len) 
{
	FileWrite_typ file_write = {0};
	file_write.enable     = 1;
	// dereference the pointer to the file
	file_write.ident    = *fp;
	file_write.offset   = 0;
	file_write.pSrc     = (UDINT) write_data;
	file_write.len      = write_len;

	/* Call FBK */
	FileWrite(&file_write);
	return get_error_code(file_write.status);
}

int close_file(UDINT* fp)
{
	/* Initialize file close structure */
	FileClose_typ file_close = {0};
	file_close.enable     = 1;
	file_close.ident    = *fp;
				
	/* Call FBK */
	FileClose(&file_close);
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
 
/***** Cyclic part *****/
_CYCLIC void Cyclic(void)
{
	char* file = "Test.csv";
	test = file_exists(file);
}