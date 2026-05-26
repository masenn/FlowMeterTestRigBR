
PROGRAM _INIT
	(* Insert code here *)
	FlowPumpFlowINT;
	Pump_PID_Pars.DerivativeTime := 0.5;
	Pump_PID_Pars.FilterTime := 0.0;
	Pump_PID_Pars.Gain := 2.35;
	Pump_PID_Pars.IntegrationTime := 0.6;
		
	Pump_PID.PIDParameters := Pump_PID_Pars; 
	Pump_PID.MinOut := PUMP_MIN; 
	Pump_PID.MaxOut := PUMP_MAX_OUTPUT; 
	Pump_PID.Invert := FALSE; 
	Pump_PID.Update := TRUE; 
END_PROGRAM

PROGRAM _CYCLIC
	IF Config_Update THEN
		Pump_PID_Pars.DerivativeTime := 0.50;
		Pump_PID_Pars.FilterTime := 0.0;
		Pump_PID_Pars.Gain := 2.35;
		Pump_PID_Pars.IntegrationTime := 0.6;
		
		Pump_PID.PIDParameters := Pump_PID_Pars; 
		Pump_PID.MinOut := PUMP_MIN; 
		Pump_PID.MaxOut := PUMP_MAX_OUTPUT; 
		Pump_PID.Invert := FALSE; 
		Pump_PID.Update := TRUE; 
		 
	END_IF
	
	Pump_PID.Enable := cmdFlowPumpEN;
	Pump_PID.SetValue := TargetFlow;
	Pump_PID.ActValue := Cori_Measurement;
	FlowPumpFlowINT := REAL_TO_INT(Pump_PID.Out);
	
	Pump_PID();

	 
END_PROGRAM

PROGRAM _EXIT
	(* Insert code here *)
	 
END_PROGRAM

