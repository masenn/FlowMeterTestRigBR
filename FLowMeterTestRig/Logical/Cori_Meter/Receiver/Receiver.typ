(********************************************************************
 * COPYRIGHT -- Bernecker + Rainer
 ********************************************************************
 * Program: Receiver
 * File: Receiver.typ
 * Author: Bernecker & Rainer
 * Created: January 25, 2010
 ********************************************************************
 * Local data types of program Receiver
 ********************************************************************)
(*Enumeration for Statemachine*)

TYPE
	enRECV_STEPS : 
		(
		FRM_WAIT := 0, (*Defines the wait step*)
		FRM_OPEN, (*Defines Step for FRM_xopen() *)
		FRM_READ, (*Defines Step for FRM_read()*)
		FRM_COPY_RD_DATA, (*Defines Step for storing read data*)
		FRM_RBUF, (*Defines Step for FRM_rbuf()*)
		FRM_CLOSE, (*Defines Step for FRM_close()*)
		FRM_ERROR := 255 (*Defines Step for Errorhandling*)
		);
END_TYPE

(*Command data type*)

TYPE
	command_typ : 	STRUCT 
		open_receive : BOOL; (*Open serial port and receive data*)
		close : BOOL; (*Close serial port*)
	END_STRUCT;
END_TYPE

(*Receiver type*)

TYPE
	Receiver_typ : 	STRUCT 
		step : enRECV_STEPS; (*Step of the Statemachine*)
		Commands : command_typ; (*Commandinterface*)
		receive_data : ARRAY[0..13]OF USINT; (*receive data*)
		FRM_xopen_0 : FRM_xopen; (*Functionblock FRM_xopen()*)
		xopenConfig : XOPENCONFIG; (*Configuration Type for FRM_xopen()*)
		FRM_read_0 : FRM_read; (*Functionblock FRM_read()*)
		FRM_rbuf_0 : FRM_rbuf; (*Functionblock FRM_rbuf()*)
		FRM_close_0 : FRM_close; (*Functionblock FRM_close()*)
	END_STRUCT;
END_TYPE
