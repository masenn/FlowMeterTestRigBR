

(*************init program**********************)
PROGRAM _INIT
	Receiver.Commands.open_receive := TRUE;												(*enable Receiver by default*)						
END_PROGRAM

(*************cyclic program********************)
PROGRAM _CYCLIC


	CASE Receiver.step OF
		FRM_WAIT:	(*--- wait for command*)
			
			IF Receiver.Commands.open_receive = TRUE THEN								(*command for Receiver activation*)
				Receiver.step := FRM_OPEN;
   			END_IF			
		
			(*close will be requested in step FRM_RBUF*)
		
		FRM_OPEN:	(*--- open serial interface*)
			
			(*Parameters for FRM_xopen()*)
			Receiver.FRM_xopen_0.enable := TRUE;
			Receiver.FRM_xopen_0.device := ADR('SL1.IF5');							(*Devicename --> see your serial interface properties*)
			Receiver.FRM_xopen_0.mode := ADR('/PHY=RS232 /BD=38400 /DB=8 /PA=N /SB=1'); (*Modestring --> specifies the seria operation mode*)
			Receiver.FRM_xopen_0.config := ADR(Receiver.xopenConfig) ;					(*Additional Parameters, optional*)
			
			(*Additional Parameters for FRM_xopen()*)
			Receiver.xopenConfig.idle := 10;											(*Idle time between two characters*)
			Receiver.xopenConfig.delimc := 0;											(*activate two delimeters*)
			Receiver.xopenConfig.delim[0] := 0; 										(*e.g. CR - carridge return -> dec 13*)
			Receiver.xopenConfig.delim[1] := 0; 										(*e.g. LF - line feed -> dec 10*)
			Receiver.xopenConfig.tx_cnt := 12;											(*number of transmit buffers*)
			Receiver.xopenConfig.rx_cnt := 14; 											(*number of receive buffers*)
			Receiver.xopenConfig.tx_len := 256; 										(*length of transmit buffers*)
			Receiver.xopenConfig.rx_len := 256; 										(*lenght of receive buffers*)
			Receiver.xopenConfig.argc := 0;												(*activate additional options*)
			Receiver.xopenConfig.argv := 0;												(*parameters for additional options (check help)*)
		
			Receiver.FRM_xopen_0();														(*call the FRM_xopen() function*)
			
			IF Receiver.FRM_xopen_0.status = 0 THEN
				Receiver.step := FRM_READ;												(*Interface opend successfully --> next step*)
			ELSIF Receiver.FRM_xopen_0.status = BUSY THEN
				Receiver.step := FRM_OPEN;												(*operation not finished yet --> call again*)
			ELSE
				Receiver.step := FRM_ERROR;												(*function returned errorcode --> check help*)
   			END_IF			
			
		FRM_READ:	(*--- read data from serial interface*)
			Receiver.FRM_read_0.enable := TRUE;
   			Receiver.FRM_read_0.ident := Receiver.FRM_xopen_0.ident;
			
			Receiver.FRM_read_0();														(*call the FRM_read() function*)
			
			IF Receiver.FRM_read_0.status = 0 THEN
				Receiver.step := FRM_COPY_RD_DATA;										(*system returned a valid data --> next step*)
			ELSIF Receiver.FRM_read_0.status = frmERR_NOINPUT THEN
				Receiver.step := FRM_READ;												(*no data available --> call again*)
			ELSIF Receiver.FRM_read_0.status = frmERR_INPUTERROR THEN
				Receiver.step := FRM_RBUF;												(*received Frame with defective characters, skip data*)
			ELSE
				Receiver.step := FRM_ERROR;												(*function returned errorcode --> check help*)
   			END_IF			
			
		
		FRM_COPY_RD_DATA: (*--- copy data out of the receive buffer*)
			memset(ADR(Receiver.receive_data),0,SIZEOF(Receiver.receive_data));			(*clear read_data buffer*)
			memcpy(ADR(Receiver.receive_data),Receiver.FRM_read_0.buffer,Receiver.FRM_read_0.buflng);     (*copy and evaluate read data*)
			Receiver.step := FRM_RBUF;													(*release read buffer*)
			
		FRM_RBUF:	(*--- release readbuffer*)
			SwappedMeasurement[0] := Receiver.receive_data[11];
			SwappedMeasurement[1] := Receiver.receive_data[10];
			SwappedMeasurement[2] := Receiver.receive_data[9];
			SwappedMeasurement[3] := Receiver.receive_data[8];
			memcpy(ADR(flow_actual),ADR(SwappedMeasurement[0]),4);
			(*Parameters for FRM_rbuf()*)
			Receiver.FRM_rbuf_0.enable := TRUE;
			Receiver.FRM_rbuf_0.ident := Receiver.FRM_xopen_0.ident;					(*ident from FRM_xopen()*)
			Receiver.FRM_rbuf_0.buffer := Receiver.FRM_read_0.buffer;					(*read buffer*)
			Receiver.FRM_rbuf_0.buflng := Receiver.FRM_read_0.buflng;					(*length of sendbuffer*)
   			
			Receiver.FRM_rbuf_0();														(*call the FRM_rbuf() function*)
			
			IF Receiver.FRM_rbuf_0.status = 0 THEN
				IF Receiver.Commands.close = TRUE THEN
					Receiver.Commands.open_receive := FALSE;								(*disable command open_send*)
					Receiver.step := FRM_CLOSE;											(*request to close serial port*)
				ELSE				
					Receiver.step := FRM_READ;											(*read again*)
				END_IF
			ELSIF Receiver.FRM_rbuf_0.status = BUSY THEN
				Receiver.step := FRM_RBUF;												(*operation not finished yet --> call again*)
			ELSIF Receiver.FRM_rbuf_0.status = frmERR_INVALIDBUFFER THEN					
				Receiver.step := FRM_READ;												(*buffer is invalid --> read again*)
			ELSE
				Receiver.step := FRM_ERROR;												(*function returned errorcode --> check help*)
   			END_IF			
		
		FRM_CLOSE:	(*--- close the interface*)
			Receiver.FRM_close_0.enable := TRUE;
   			Receiver.FRM_close_0.ident := Receiver.FRM_xopen_0.ident;					(*ident from FRM_xopen()*)			
			
			Receiver.FRM_close_0();														(*call the FRM_close() function*)
			
			IF Receiver.FRM_close_0.status = 0 THEN
				Receiver.Commands.close := FALSE;										(*disable close command*)
				Receiver.step := FRM_WAIT;												(*closed interface successfully --> wait step*)
			ELSIF Receiver.FRM_close_0.status = BUSY THEN
				Receiver.step := FRM_CLOSE;												(*operation not finished yet --> call again*)
			ELSE
				Receiver.step := FRM_ERROR;												(*function returned errorcode --> check help*)
			END_IF
			
		FRM_ERROR:	(*--- error handling*)
			; (*not implementet yet, check help for error codes*)
	END_CASE	
	

END_PROGRAM
