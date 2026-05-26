/***** Header files *****/
#include <bur/plctypes.h>
#include <brsystem.h>
//#include "Global.h"
#include <fileio.h>


/***** Variable declaration *****/
_LOCAL BOOL bOK;
_LOCAL USINT byStep, byErrorLevel;
_LOCAL USINT byReadData[100], byWriteData[100];
_LOCAL UINT wStatus, wError;
_LOCAL UDINT dwIdent;
_LOCAL FileOpen_typ FOpen;
_LOCAL FileClose_typ FClose;
_LOCAL FileCreate_typ FCreate;
_LOCAL FileRead_typ FRead;
_LOCAL FileWrite_typ FWrite;
_LOCAL FileDelete_typ FDelete;

typedef struct {
	USINT field;
}Data_Point_t; 

_GLOBAL Data_Point_t test;

/***** Init part *****/
_INIT void Init(void)
{
	int i;
	/* Initialize variables */
	bOK = 0;
	byStep = 1;
	byErrorLevel = 0;
	/* Initialize read and write data */
	for (i = 0; i < 100; i ++)
	{
		byWriteData[i]  = i + 1;
		byReadData[i]   = 0;
	}
}
 
/***** Cyclic part *****/
_CYCLIC void Cyclic(void)
{
	switch (byStep)
	{
		case 0: /**** Error step ****/
			bOK = 0;
			break;
		case 1: /**** Try to open existing file ****/
			/* Initialize file open structrue */
			FOpen.enable      = 1;
			FOpen.pDevice   = (UDINT) "USER";
			FOpen.pFile     = (UDINT) "TestFile.csv";
			FOpen.mode      = fiREAD_WRITE;                        /* Read and write access */

			/* Call FUB */
			FileOpen(&FOpen);

			/* Get FBK output information */
			dwIdent = FOpen.ident;
			wStatus = FOpen.status;
			/* Verify status (20708 -> File doesn't exist) */
			if (wStatus == 20708)
			{
				byStep = 2;
			}
			else if (wStatus == 0)
			{
				byStep = 3;
			}
			else if (wStatus != 65535)
			{
				byErrorLevel = 1;
				byStep = 0;
				if (wStatus == 20799)
				{
					wError = FileIoGetSysError();
				}
				else 
				{
					wError = 111;
				}
			}
			break;
		case 2: /**** Create file ****/
			/* Initialize file create structure */
			FCreate.enable    = 1;
			FCreate.pDevice = (UDINT) "USER";
			FCreate.pFile   = (UDINT) "TestFile.csv";
			/* Call FUB */
			FileCreate(&FCreate);
			/* Get output information of FBK */
			dwIdent = FCreate.ident;
			wStatus = FCreate.status;
			/* Verify status */
			if (wStatus == 0)
			{
				byStep = 3;
			}
			else if (wStatus != 65535)
			{
				byErrorLevel = 2;
				byStep = 0;
                                
				if (wStatus == 20799)
				{
					wError = FileIoGetSysError();
				}
			}
			else
			{
				wError = 222;
			}
			break;

		case 3: /**** Write data to file ****/
			/* Initialize file write structure */
			FWrite.enable     = 1;
			FWrite.ident    = dwIdent;
			FWrite.offset   = 0;
			FWrite.pSrc     = (UDINT) &byWriteData[0];
			FWrite.len      = sizeof (byWriteData);

			/* Call FBK */
			FileWrite(&FWrite);
			/* Get status */
			wStatus = FWrite.status;
			/* Verify status */
			if (wStatus == 0)
			{
				byStep = 4;
			}
			else if (wStatus != 65535)
			{
				byErrorLevel = 3;
				byStep = 0;

				if (wStatus == 20799)
				{
					wError = FileIoGetSysError();
				}
			}
			else
			{
				wError = 333;
			}
			break;
		case 4: /**** Read data from file ****/
			/* Initialize file read structure */
			FRead.enable      = 1;
			FRead.ident     = dwIdent;
			FRead.offset    = 0;
			FRead.pDest     = (UDINT) &byReadData[0];
			FRead.len       = sizeof (byReadData);
			/* Call FBK */
			FileRead(&FRead);
			/* Get status */
			wStatus = FRead.status;
			/* Verify status */
			if (wStatus == 0)
			{
				byStep = 5;
			}
			else if (wStatus != 65535)
			{
				byErrorLevel = 4;
				byStep = 0;
				if (wStatus == 20799)
				{
					wError = FileIoGetSysError();
				}
			}
                        
			break;
		case 5: /**** Close file ****/
			/* Initialize file close structure */
			FClose.enable     = 1;
			FClose.ident    = dwIdent;
                        
			/* Call FBK */
			FileClose(&FClose);

			/* Get status */
			wStatus = FClose.status;

			/* Verify status */
			if (wStatus == 0)
			{
				byStep = 1;
			}
			else if (wStatus != 65535)
			{
				byErrorLevel = 5;
				byStep = 0;
				if (wStatus == 20799)
				{
					wError = FileIoGetSysError();
				}
			}
                        
			break;
		case 6: /**** Delete file ****/
			/* Initialize file delete structure */
			FDelete.enable    = 1;
			FDelete.pDevice = (UDINT) "HARDDISK";
			FDelete.pName   = (UDINT) "TestFile.csv";
			/* Call FBK */
			FileDelete(&FDelete);
			/* Get status */
			wStatus = FDelete.status;
			/* Verify status */
			if (wStatus == 0)
			{
				bOK = 1;
				byStep = 7;
			}
			else if (wStatus != 65535)
			{
				byErrorLevel = 6;
				byStep = 0;
				if (wStatus == 20799)
				{
					wError = FileIoGetSysError();
				}
			}
			break;
	}

}