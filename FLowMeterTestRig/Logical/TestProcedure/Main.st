
PROGRAM _INIT
	(* Insert code here *)
	 LiftPumpEN;
END_PROGRAM

PROGRAM _CYCLIC
	
	
//	
//(* ===================== SET 1-5 WHICH DUT IS ACTIVE ======================= *)
//	IF CmdChangeSample THEN
//		IF CurrentSample <5 THEN
//			CurrentSample := CurrentSample + 1;
//		ELSE
//			AllSamplesTested := TRUE;
//			CurrentSample := 1;
//		END_IF
//	END_IF
//	
//	
//(* ===================== SCALE INPUTS TO REAL ============================== *)
//	FluidTempScale(x := INT_TO_REAL(FluidTemp), x1 := 0, y1 := 0, x2 := 32767, y2 := 300);
//	AirTempScale(x := INT_TO_REAL(AirTemp), x1 := 0, y1 := 0, x2 := 32767, y2 := 300);
//	
//	FluidTempFloat := FluidTempScale.y;
//	AirTempFloat := AirTempScale.y;
//	
//	//Check if fluid temp is within range
//	IF (FluidTempFloat <= (TargetTempFloat * 0.1)) OR (FluidTempFloat >= (TargetTempFloat * 0.1)) THEN
//		TargetTempOK := TRUE;
//	ELSE
//		TargetTempOK := FALSE;
//	END_IF
//	
//	rDUT_FlowRate := DUTFlowRate[CurrentSample];
//(* =====================  MAIN CYCLIC BODY  ================================ *)
// 
//(* --- Detect state change for one-shot entry actions --- *)
//	bStateChanged := (eState <> ePrevState);
//	IF bStateChanged THEN
//		ePrevState := eState;
//	END_IF
// 
//(* =========================================================================
// *  GLOBAL ABORT – highest priority, reachable from ANY state
// * ========================================================================= *)
//	IF cmdAbort AND eState <> ABORTED AND eState <> ABORTING THEN
//		eState := ABORTING;
//		cmdAbort := FALSE;
//	END_IF
// 
//(* =========================================================================
// *  GLOBAL STOP – reachable from execute-branch states
// * ========================================================================= *)
//	IF cmdStop AND
//		(eState = EXECUTE     OR
//		eState = STARTING    OR
//		eState = COMPLETING  OR
//		eState = COMPLETE    OR
//		eState = HOLDING     OR
//		eState = HELD        OR
//		eState = UNHOLDING   OR
//		eState = SUSPENDING  OR
//		eState = SUSPENDED   OR
//		eState = UNSUSPENDING) THEN
//		eState := STOPPING;
//		cmdStop := FALSE;
//	END_IF
// 
//(* =========================================================================
// *  STATE MACHINE
// * ========================================================================= *)
//	CASE eState OF
// 
//		(* --------------------------------------------------------------------- *)
//		STOPPED:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg := 'STOPPED – Awaiting Reset command';
//				bIsolationValve := FALSE;
//				bPumpRunning    := FALSE;
//			END_IF
// 
//			IF cmdReset THEN
//				eState   := RESETTING;
//				cmdReset := FALSE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		RESETTING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg       := 'RESETTING – Zeroing counters, homing actuators';
//				bResettingDone   := FALSE;
//				nExecStep        := 0;
//				nStabilityCount  := 0;
//				nAcqSampleCount  := 0;
//				rDUT_Accumulator := 0.0;
//				rRef_Accumulator := 0.0;
//				rFlowError_Pct   := 0.0;
//				bTestPass        := FALSE;
//				bAcquisitionDone := FALSE;
//				bFlowStable      := FALSE;
//			END_IF
// 
//			(* -- Perform reset actions (home valves, zero totalizers) -- *)
//			bIsolationValve := FALSE;
//			bPumpRunning    := FALSE;
// 
//			(* In a real project, wait for confirmation from actuators here *)
//			bResettingDone := TRUE;
// 
//			IF bResettingDone THEN
//				eState := IDLE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		IDLE:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg := 'IDLE – Ready for test. Awaiting Start command';
//			END_IF
// 			ActualSolenoids := HMISolenoids;
//			IF cmdStart THEN
//				eState   := STARTING;
//				cmdStart := FALSE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		STARTING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg     := 'STARTING – Opening isolation valve, priming pump';
//				bStartingDone  := FALSE;
//				AllSamplesTested := FALSE;
//				tonStartDelay(IN := FALSE);     (* reset timer *)
//			END_IF
// 
//			(* Step 1: Open isolation valve *)
//			bIsolationValve := TRUE;
// 
//			(* Step 2: Allow settling time *)
//			tonStartDelay(IN := bIsolationValve, PT := T#2S);
// 
//			(* Step 3: Start reference pump once valve is confirmed open *)
//			IF tonStartDelay.Q THEN
//				bPumpRunning  := TRUE;
//				bStartingDone := TRUE;
//			END_IF
// 
//			IF bStartingDone THEN
//				eState := EXECUTE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		EXECUTE:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg    := 'EXECUTE – Running flow-meter test sequence';
//				bExecuteDone  := FALSE;
//				nExecStep     := 0;
//			END_IF
// 			
//			//Open solenoid to the correct DUT
//			ActualSolenoids[CurrentSample - 1] := TRUE;
//			
//			CASE nExecStep OF
//				(* ---------- Step 0: Ramp to target flow rate ---------- *)
//				0:
//					sStatusMsg := 'EXECUTE [Ramp] – Approaching target flow rate';
//					cmdFlowPumpEN := TRUE;
//            (* Controller ramps pump speed toward rTargetFlowRate.
//               Placeholder: assume external PID writes rActualFlowRate. *)
//					tonRampTimeout(IN := TRUE, PT := T#30S);
// 
//					IF ABS((Cori_Measurement - TargetFlow) < (TargetFlow * 0.02)) AND TargetTempOK THEN
//						(* Within 2 % of target – move to stabilise *)
//						tonRampTimeout(IN := FALSE);
//						nExecStep := 1;
//					ELSIF tonRampTimeout.Q THEN
//						(* Timeout – could not reach set point ? Hold *)
//						tonRampTimeout(IN := FALSE);
//						sStatusMsg := 'EXECUTE [Ramp] – TIMEOUT reaching target or temperature';
//						cmdHold := TRUE;    (* auto-hold on fault *)
//					END_IF
// 
//					(* ---------- Step 1: Stabilise flow ---------- *)
//				1:
//					sStatusMsg := 'EXECUTE [Stabilise] – Waiting for steady state';
//					IF ABS(Cori_Measurement - TargetFlow) < (TargetFlow * 0.01) THEN
//						nStabilityCount := nStabilityCount + 1;
//					ELSE
//						nStabilityCount := 0;
//					END_IF
// 
//					IF nStabilityCount >= nStabilityTarget THEN
//						bFlowStable := TRUE;
//						nExecStep   := 2;
//					END_IF
// 
//					(* ---------- Step 2: Acquire DUT readings ---------- *)
//				2:
//					sStatusMsg := 'EXECUTE [Acquire] – Sampling DUT and reference';
//					rDUT_Accumulator := rDUT_Accumulator + rDUT_FlowRate;
//					rRef_Accumulator := rRef_Accumulator + Cori_Measurement;
//					nAcqSampleCount  := nAcqSampleCount + 1;
// 
//					IF nAcqSampleCount >= nAcqSampleTarget THEN
//						bAcquisitionDone := TRUE;
//						nExecStep := 3;
//					END_IF
// 
//					(* ---------- Step 3: Compute error & pass/fail ---------- *)
//				3:
//					sStatusMsg := 'EXECUTE [Evaluate] – Computing error';
//					IF rRef_Accumulator <> 0.0 THEN
//						rFlowError_Pct := ((rDUT_Accumulator - rRef_Accumulator)
//						/ rRef_Accumulator) * 100.0;
//					ELSE
//						rFlowError_Pct := 99.99;   (* avoid divide-by-zero *)
//					END_IF
// 
//					bTestPass := (ABS(rFlowError_Pct) <= rAcceptableTol_Pct);
// 
//					IF bTestPass THEN
//						sStatusMsg := 'EXECUTE [PASS] – DUT within tolerance';
//					ELSE
//						sStatusMsg := 'EXECUTE [FAIL] – DUT outside tolerance';
//					END_IF
// 
//					nExecStep := 4;
// 
//					(* ---------- Step 4: Ramp down ---------- *)
//				4:
//					sStatusMsg := 'EXECUTE [RampDown] – Reducing flow to zero';
//					cmdFlowPumpEN := FALSE;
//					(* When rActualFlowRate ˜ 0 ? done *)
//					IF Cori_Measurement < 10 THEN
//						bPumpRunning := FALSE;
//						bExecuteDone := TRUE;
//					END_IF
//			END_CASE
// 
//			(* ---- Suspend on external signal (e.g. upstream supply issue) ---- *)
//			IF cmdSuspend THEN
//				eState     := SUSPENDING;
//				cmdSuspend := FALSE;
//			END_IF
// 
//			(* ---- Hold on operator or fault request ---- *)
//			IF cmdHold THEN
//				eState  := HOLDING;
//				cmdHold := FALSE;
//			END_IF
// 
//			IF bExecuteDone AND (NOT AllSamplesTested) THEN //Switch sample and continue testing if all DUT have not been tested
//				CmdChangeSample := TRUE;
//			ELSIF bExecuteDone AND AllSamplesTested THEN
//				eState := COMPLETING;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		COMPLETING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg      := 'COMPLETING – Closing valves, writing test log';
//				bCompletingDone := FALSE;
//			END_IF
// 
//			bIsolationValve := FALSE;
// 
//			(* Write test record to historian / database here *)
//			(* Placeholder: assume instant *)
//			bCompletingDone := TRUE;
// 
//			IF bCompletingDone THEN
//				eState := COMPLETE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		COMPLETE:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				IF bTestPass THEN
//					sStatusMsg := 'COMPLETE – Test PASSED. Reset to run again.';
//				ELSE
//					sStatusMsg := 'COMPLETE – Test FAILED. Reset to run again.';
//				END_IF
//			END_IF
// 
//			IF cmdStop THEN
//				eState  := STOPPING;
//				cmdStop := FALSE;
//			END_IF
// 
//			IF cmdReset THEN
//				eState   := RESETTING;
//				cmdReset := FALSE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		HOLDING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg    := 'HOLDING – Pausing pump, maintaining valve position';
//				bHoldingDone  := FALSE;
//			END_IF
// 
//			(* Safe-pause: reduce pump to idle, keep valve open *)
//			bPumpRunning := FALSE;
//			bHoldingDone := TRUE;
// 
//			IF bHoldingDone THEN
//				eState := HELD;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		HELD:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg := 'HELD – Pump paused. Issue Unhold to resume.';
//			END_IF
// 
//			IF cmdUnhold THEN
//				eState    := UNHOLDING;
//				cmdUnhold := FALSE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		UNHOLDING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg       := 'UNHOLDING – Restarting pump, restabilising flow';
//				bUnholdingDone   := FALSE;
//				nStabilityCount  := 0;
//			END_IF
// 
//			bPumpRunning   := TRUE;
//			bUnholdingDone := TRUE;     (* In practice, wait for pump-ready *)
// 
//			IF bUnholdingDone THEN
//				eState := EXECUTE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		SUSPENDING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg        := 'SUSPENDING – External condition; reducing to idle flow';
//				bSuspendingDone   := FALSE;
//			END_IF
// 
//			(* Reduce to safe idle flow but keep loop alive *)
//			bSuspendingDone := TRUE;
// 
//			IF bSuspendingDone THEN
//				eState := SUSPENDED;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		SUSPENDED:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg := 'SUSPENDED – Waiting for external condition to clear';
//			END_IF
// 
//			IF cmdUnsuspend THEN
//				eState       := UNSUSPENDING;
//				cmdUnsuspend := FALSE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		UNSUSPENDING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg         := 'UNSUSPENDING – Ramping back to target flow';
//				bUnsuspendingDone  := FALSE;
//				nStabilityCount    := 0;
//			END_IF
// 
//			bUnsuspendingDone := TRUE;
// 
//			IF bUnsuspendingDone THEN
//				eState := EXECUTE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		STOPPING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg     := 'STOPPING – Shutting down pump, closing valve';
//				bStoppingDone  := FALSE;
//				tonStopDelay(IN := FALSE);
//			END_IF
// 
//			bPumpRunning    := FALSE;
//			bIsolationValve := FALSE;
// 
//			tonStopDelay(IN := TRUE, PT := T#3S);   (* allow line to drain *)
// 
//			IF tonStopDelay.Q THEN
//				tonStopDelay(IN := FALSE);
//				bStoppingDone := TRUE;
//			END_IF
// 
//			IF bStoppingDone THEN
//				eState := STOPPED;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		ABORTING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg     := 'ABORTING – Emergency shutdown in progress';
//				bAbortingDone  := FALSE;
//			END_IF
// 
//			(* Immediate safe state *)
//			bPumpRunning    := FALSE;
//			bIsolationValve := FALSE;
//			bAbortingDone   := TRUE;
// 
//			IF bAbortingDone THEN
//				eState := ABORTED;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		ABORTED:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg := 'ABORTED – Rig safe. Issue Clear to proceed.';
//			END_IF
// 
//			IF cmdClear THEN
//				eState   := CLEARING;
//				cmdClear := FALSE;
//			END_IF
// 
//			(* --------------------------------------------------------------------- *)
//		CLEARING:
//			(* --------------------------------------------------------------------- *)
//			IF bStateChanged THEN
//				sStatusMsg     := 'CLEARING – Resetting fault flags';
//				bClearingDone  := FALSE;
//			END_IF
// 
//			(* Reset any latched alarms / fault flags here *)				
//			nExecStep        := 0;
//			nStabilityCount  := 0;
//			nAcqSampleCount  := 0;
//			rDUT_Accumulator := 0.0;
//			rRef_Accumulator := 0.0;
//			rFlowError_Pct   := 0.0;
//			bTestPass        := FALSE;
//			bAcquisitionDone := FALSE;
//			bFlowStable      := FALSE;
//			bClearingDone := TRUE;
// 
//			IF bClearingDone THEN
//				eState := STOPPED;
//			END_IF
// 
//	END_CASE
// 
//(* =========================================================================
// *  ONE-SHOT COMMAND CLEARING
// *  Ensure stale commands don't re-fire on the next scan.
// * ========================================================================= *)
//	cmdStart      := FALSE;
//	cmdStop       := FALSE;
//	cmdHold       := FALSE;
//	cmdUnhold     := FALSE;
//	cmdSuspend    := FALSE;
//	cmdUnsuspend  := FALSE;
//	cmdAbort      := FALSE;
//	cmdClear      := FALSE;
//	cmdReset      := FALSE;
//	
	HMISolenoids[0] := cmdFlowPumpEN;
	IF NOT bIsolationValve THEN
		cmdFlowPumpEN := FALSE;
	END_IF		
END_PROGRAM

PROGRAM _EXIT
	(* Insert code here *)
	 
END_PROGRAM

