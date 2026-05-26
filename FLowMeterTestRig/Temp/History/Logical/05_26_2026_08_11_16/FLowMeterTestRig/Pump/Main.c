//#include <stdbool.h>
//#include <stdint.h>
//#include <bur/plc.h>
//#include <bur/plctypes.h>
//
//// -----------------------------------------------------------------------
//// Types
//// -----------------------------------------------------------------------
//
//typedef struct {
//	float Gain;             // Proportional gain (Kp)
//	float IntegrationTime;  // Ti in seconds (0 = integrator disabled)
//	float DerivativeTime;   // Td in seconds (0 = derivative disabled)
//	float FilterTime;       // Tf in seconds for derivative filter (0 = no filter)
//} MTPIDParametersType;
//
//typedef struct {
//	// Inputs
//	bool            Enable;
//	bool            Update;         // reload parameters on next cycle
//	bool            Invert;         // invert control error (ActValue - SetValue instead)
//	float           SetValue;
//	float           ActValue;
//	float           MinOut;
//	float           MaxOut;
//	MTPIDParametersType PIDParameters;
//
//	// Outputs
//	float           Out;
//	float           ControlError;
//	float           ProportionalPart;
//	float           IntegrationPart;
//	float           DerivativePart;
//
//	// Internal state
//	float           _integrator;
//	float           _prevError;
//	float           _filteredDerivative;
//	bool            _initialized;
//} MTBasicsPID;
//
//// -----------------------------------------------------------------------
//// PID execute — call once per cycle
//// -----------------------------------------------------------------------
//
//void MTBasicsPID_run(MTBasicsPID* pid, float dt)
//{
//	if (!pid->Enable)
//	{
//		pid->Out            = 0.0f;
//		pid->ControlError   = 0.0f;
//		pid->ProportionalPart  = 0.0f;
//		pid->IntegrationPart   = 0.0f;
//		pid->DerivativePart    = 0.0f;
//		pid->_integrator       = 0.0f;
//		pid->_prevError        = 0.0f;
//		pid->_filteredDerivative = 0.0f;
//		pid->_initialized      = false;
//		return;
//	}
//
//	// Reload parameters if requested
//	if (pid->Update)
//	{
//		pid->Update = false;
//		// Reset integrator on parameter update to avoid windup spike
//		pid->_integrator = 0.0f;
//		pid->_filteredDerivative = 0.0f;
//		pid->_initialized = false;
//	}
//
//	// Control error
//	float error = pid->Invert
//		? (pid->ActValue - pid->SetValue)
//		: (pid->SetValue - pid->ActValue);
//
//	pid->ControlError = error;
//
//	// Proportional
//	float P = pid->PIDParameters.Gain * error;
//	pid->ProportionalPart = P;
//
//	// Integral
//	float I = 0.0f;
//	if (pid->PIDParameters.IntegrationTime > 0.0f)
//	{
//		pid->_integrator += (pid->PIDParameters.Gain / pid->PIDParameters.IntegrationTime)
//			* error * dt;
//		I = pid->_integrator;
//	}
//	pid->IntegrationPart = I;
//
//	// Derivative with optional first-order filter
//	float D = 0.0f;
//	if (pid->PIDParameters.DerivativeTime > 0.0f && pid->_initialized)
//	{
//		float rawDerivative = pid->PIDParameters.Gain
//			* pid->PIDParameters.DerivativeTime
//			* (error - pid->_prevError) / dt;
//
//		if (pid->PIDParameters.FilterTime > 0.0f)
//		{
//			float alpha = dt / (pid->PIDParameters.FilterTime + dt);
//			pid->_filteredDerivative += alpha * (rawDerivative - pid->_filteredDerivative);
//			D = pid->_filteredDerivative;
//		}
//		else
//		{
//			D = rawDerivative;
//		}
//	}
//	pid->DerivativePart = D;
//	pid->_prevError     = error;
//	pid->_initialized   = true;
//
//	// Sum and clamp
//	float output = P + I + D;
//	if      (output > pid->MaxOut) output = pid->MaxOut;
//	else if (output < pid->MinOut) output = pid->MinOut;
//
//	// Anti-windup — clamp integrator if output is saturated
//	if (pid->PIDParameters.IntegrationTime > 0.0f)
//	{
//		if ((output >= pid->MaxOut && error > 0.0f) ||
//			(output <= pid->MinOut && error < 0.0f))
//		{
//			pid->_integrator -= (pid->PIDParameters.Gain / pid->PIDParameters.IntegrationTime)
//				* error * dt;
//		}
//	}
//
//	pid->Out = output;
//}
//
//// -----------------------------------------------------------------------
//// Your program
//// -----------------------------------------------------------------------
//
//#define PUMP_MIN        0.0f
//#define PUMP_MAX_OUTPUT 16383.0f
//
//MTBasicsPID        	Pump_PID     = {0};
//MTPIDParametersType Pump_PID_Pars = {0};
//bool               	Config_Update = false;
//_GLOBAL REAL 		TargetFlow;
//_GLOBAL REAL		Cori_Measurement;
//_GLOBAL BOOL 		cmdFlowPumpEN;
//_GLOBAL INT			FlowPumpFlowINT;
//
//_INIT void program_init(void)
//{
//	Pump_PID_Pars.DerivativeTime   = 0.5f;
//	Pump_PID_Pars.FilterTime       = 0.0f;
//	Pump_PID_Pars.Gain             = 2.35f;
//	Pump_PID_Pars.IntegrationTime  = 0.6f;
//
//	Pump_PID.PIDParameters = Pump_PID_Pars;
//	Pump_PID.MinOut        = PUMP_MIN;
//	Pump_PID.MaxOut        = PUMP_MAX_OUTPUT;
//	Pump_PID.Invert        = false;
//	Pump_PID.Update        = true;
//}
//
//void program_cyclic(float dt)
//{
//	if (Config_Update)
//	{
//		Pump_PID_Pars.DerivativeTime  = 0.0f;
//		Pump_PID_Pars.FilterTime      = 0.0f;
//		Pump_PID_Pars.Gain            = 0.3f;
//		Pump_PID_Pars.IntegrationTime = 0.0f;
//
//		Pump_PID.PIDParameters = Pump_PID_Pars;
//		Pump_PID.MinOut        = PUMP_MIN;
//		Pump_PID.MaxOut        = PUMP_MAX_OUTPUT;
//		Pump_PID.Invert        = false;
//		Pump_PID.Update        = true;
//
//		Config_Update = false;
//	}
//
//	Pump_PID.Enable   = cmdFlowPumpEN;
//	Pump_PID.SetValue = TargetFlow;
//	Pump_PID.ActValue = Cori_Measurement;
//
//	MTBasicsPID_run(&Pump_PID, dt);
////	FlowPumpFlowINT = Pump_PID.Out;
//	// Pump_PID.Out now holds the output — equivalent to FlowPumpFlowINT
//}