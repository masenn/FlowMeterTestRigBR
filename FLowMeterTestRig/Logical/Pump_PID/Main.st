
PROGRAM _INIT
	enable_pump;
	flow_actual;
	target_flow;
	pump_output;
	dut_solenoids;

	(* Insert code here *)
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

	// shut off pid if no isolation valve opening
	IF NOT enable_isolation_valve THEN
		enable_pump := FALSE;
	END_IF
	
	//TODO ensuring that solenoids are open
	// IF (NOT dut_solenoids[0]) AND (NOT dut_solenoids[1]) AND (NOT dut_solenoids[2]) AND (NOT dut_solenoids[3]) AND (NOT dut_solenoids[4]) THEN
	
	// 	enable_pump := FALSE;
	// END_IF

	IF flow_actual < 350 AND pump_output > 13000 THEN 
		enable_pump := FALSE;
	END_IF

	Pump_PID.Enable := enable_pump;
	Pump_PID.SetValue := target_flow;
	Pump_PID.ActValue := flow_actual;
	pump_output := REAL_TO_INT(Pump_PID.Out);
	Pump_PID();

	 
END_PROGRAM

PROGRAM _EXIT
	(* Insert code here *)
	 
END_PROGRAM

