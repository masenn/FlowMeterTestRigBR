import tkinter as tk
from tkinter import ttk
import threading
import random
import struct
from collections import deque
import time
from pyModbusTCP.client import ModbusClient
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import test_analyzer as ta

# Modbus client
c = ModbusClient(host='172.16.100.50', port=502, unit_id=1, auto_open=True, auto_close=True)

POLL_INTERVAL_MS = 250
MAX_HISTORY = 1000

COILS = [
    ("Flow Controller",     1),
    ("Isolation Valve",     2),
    ("Pump Enable (PID)",   3),
    ("DUT 1 Solenoid",      4),
    ("DUT 2 Solenoid",      5),
    ("DUT 3 Solenoid",      6),
    ("DUT 4 Solenoid",      7),
    ("DUT 5 Solenoid",      8),
]

HOLDING_ADDRESS_BASE = 24576
COIL_ADDRESS_BASE    = 16384

REG_FLOW_ACTUAL  = HOLDING_ADDRESS_BASE 
REG_TARGET_FLOW  = HOLDING_ADDRESS_BASE + 1
REG_ACTIVE_DUT   = HOLDING_ADDRESS_BASE + 0x02
REG_DUT_UP_MSB   = HOLDING_ADDRESS_BASE + 0x10
REG_DUT_UP_LSB   = HOLDING_ADDRESS_BASE + 0x11
REG_DUT_DOWN_MSB = HOLDING_ADDRESS_BASE + 0x12
REG_DUT_DOWN_LSB = HOLDING_ADDRESS_BASE + 0x13
REG_DUT_AMB_MSB  = HOLDING_ADDRESS_BASE + 0x14
REG_DUT_AMB_LSB  = HOLDING_ADDRESS_BASE + 0x15
REG_DUT_SYS_MSB  = HOLDING_ADDRESS_BASE + 0x16
REG_DUT_SYS_LSB  = HOLDING_ADDRESS_BASE + 0x17
REG_DUT_BATCH = HOLDING_ADDRESS_BASE + 0x18
REG_DUT_BATCHSN = HOLDING_ADDRESS_BASE + 0x19

COIL_DUT_BASE_ADDR = 3
COIL_NO_PID_ENABLE = 2
COIL_NO_ISOLATION_ENABLE = 1
COIL_HEATER_ON = 8
COIL_HEATER_OFF = 9

# Palette
BG        = "#1a1e2e"
PANEL     = "#232842"
ACCENT    = "#4f8ef7"
ON_COLOR  = "#2ecc71"
OFF_COLOR = "#e74c3c"
TEXT      = "#e8eaf0"
SUBTEXT   = "#7a80a0"
BORDER    = "#2e3450"
ENTRY_BG  = "#2e3450"
WARN      = "#f39c12"

C_UP   = "#4f8ef7"
C_DOWN = "#2ecc71"
C_AMB  = "#f39c12"
C_FLOW = "#e74c3c"

# History buffers
history_up   = deque(maxlen=MAX_HISTORY)
history_down = deque(maxlen=MAX_HISTORY)
history_amb  = deque(maxlen=MAX_HISTORY)
history_flow = deque(maxlen=MAX_HISTORY)




def msb_lsb_to_float(msb: int, lsb: int) -> float:
    raw = ((msb & 0xFFFF) << 16) | (lsb & 0xFFFF)
    return struct.unpack('>f', struct.pack('>I', raw))[0]

def ieee754_to_float(base_addr, regs):
    raw = ((regs[base_addr] & 0xFFFF) << 16) | (regs[base_addr+1] & 0xFFFF)
    return struct.unpack('>f', struct.pack('>I', raw))[0]


def read_initial_state() -> dict:
    state = {'coils': None, 'target_flow': None, 'flow_actual': None, 'dut_regs': None, 'active_dut': None}
    try:
        coils = c.read_coils(COIL_ADDRESS_BASE, 8)
        if coils and len(coils) == 8:
            state['coils'] = coils
        target = c.read_holding_registers(REG_TARGET_FLOW, 1)
        if target:
            state['target_flow'] = target[0]
        active_dut = c.read_holding_registers(REG_ACTIVE_DUT, 1)
        if active_dut:
            state['active_dut'] = active_dut[0]
        flow = c.read_holding_registers(REG_FLOW_ACTUAL, 1)
        if flow:
            state['flow_actual'] = float(flow[0])
        dut = c.read_holding_registers(REG_DUT_UP_MSB, 8)
        if dut and len(dut) == 8:
            state['dut_regs'] = dut
    except Exception:
        pass
    return state


# ─────────────────────────────────────────────────────────────────────────────
#  TEST INFRASTRUCTURE
# ─────────────────────────────────────────────────────────────────────────────

class TestContext:



    """
    Passed into every test function.
    Provides hardware access, stop signalling, and UI logging.
    """
    def __init__(self, log_fn, stop_event: threading.Event):
        self._log   = log_fn
        self._stop  = stop_event


    

    # Logging
    def log(self, msg: str):
        """Append a timestamped line to the test log panel."""
        ts = time.strftime("%H:%M:%S")
        self._log(f"[{ts}]  {msg}")

    # Stop signal
    @property
    def stopped(self) -> bool:
        """True if the user pressed STOP. Poll inside loops."""
        return self._stop.is_set()

    def sleep(self, seconds: float):
        """Interruptible sleep — returns early if stopped."""
        deadline = time.time() + seconds
        while time.time() < deadline:
            if self.stopped:
                return
            time.sleep(0.05)

    # Modbus helpers
    def set_target_flow(self, value: int):
        c.write_single_register(REG_TARGET_FLOW, value)

    def read_target_flow(self):
        regs = c.read_holding_registers(REG_TARGET_FLOW, 1)
        if not regs: return 0
        return regs[0]

    def read_active_dut(self):
        regs = c.read_holding_registers(REG_ACTIVE_DUT, 1)
        if not regs: return 0
        return regs[0]

    def read_flow_actual(self) -> float:
        reg = c.read_holding_registers(REG_FLOW_ACTUAL, 1)
        if reg and reg[0] < 40000:
            return reg[0] / 10.0
        return 0.0

    def set_coil(self, coil_index: int, state: bool):
        """Set coil by 0-based index."""
        c.write_single_coil(coil_index + COIL_ADDRESS_BASE - 1, state)

    def read_coils_all(self):
        return c.read_coils(COIL_ADDRESS_BASE, 8)

    def read_dut_regs(self):
        return c.read_holding_registers(REG_DUT_UP_MSB, 10)
    
    def select_dut(self,dut_no: int):
        # if DUT1 is selected: dut_idx = COIL_DUT_BASE_ADDR
        # if DUT5 is selceted: dut_idx = COIL_DUT_BASE_ADDR+4
        coil_values = [False, False, False, False, False]
        coil_values[dut_no] = True
        c.write_multiple_coils(COIL_ADDRESS_BASE+COIL_DUT_BASE_ADDR,coil_values)
    
    def set_active_dut(self,dut):
        c.write_single_register(REG_ACTIVE_DUT,dut)
        self.select_dut(dut)
        print(f'Trying to set ({dut}) the pinche active dut {c.read_holding_registers(REG_ACTIVE_DUT,1)}')


    def set_heater(self):
        c.write_single_coil(COIL_ADDRESS_BASE + COIL_HEATER_ON,True)
    
    def clear_heater(self):
        c.write_single_coil(COIL_ADDRESS_BASE + COIL_HEATER_OFF,True)

    def set_isolation_valve(self,value):
        c.write_single_coil(COIL_ADDRESS_BASE + COIL_NO_ISOLATION_ENABLE,value)

    def set_pid_enable(self,value):
        c.write_single_coil(COIL_ADDRESS_BASE + COIL_NO_PID_ENABLE,value)

    def get_batch_and_sn(self):
        """
            @return batch and sn in an array
        """
        regs = self.read_dut_regs()
        if not regs: return [0,0]
        return [regs[8],regs[9]]
    
    def clear_duts(self):
        coil_values = [False, False, False, False, False]
        c.write_multiple_coils(COIL_ADDRESS_BASE+COIL_DUT_BASE_ADDR,coil_values)

    # 1-indexed dut_no to match cable notation
    def flush_active_line(self,duration=10):
        self.set_isolation_valve(True)
        active_line = self.read_active_dut()
        print(f'DEBUG{active_line}')
        self.select_dut(active_line)
        # self.log(f'Flushing out dut {active_line}')
        self.sleep(2)
        prev_target = self.read_target_flow()
        self.set_target_flow(1500)
        self.set_pid_enable(True)

        self.sleep(duration)
        self.set_target_flow(prev_target)

        
        


# ─────────────────────────────────────────────────────────────────────────────
#  TEST DEFINITIONS  —  add your tests here
#  Signature: (ctx: TestContext) -> None
# ─────────────────────────────────────────────────────────────────────────────

def _test_flow_ramp(ctx: TestContext,dut=0,heater_tries=1):
    conn = sqlite3.connect(f'python/contdut.db')
    cur = conn.cursor()
    ctx.log("Flow ramp - Starting up!")
    #remember, this is 1 indexed to align with physical cables 
    ctx.set_isolation_valve(True)
    ctx.set_pid_enable(True)
    ctx.sleep(3)
    ctx.flush_active_line(duration=25)
    ctx.set_heater()
    ctx.set_heater()
    steps = range(300, 2500, 100)
    df = pd.DataFrame(columns=['TARGET','FLOW','UP', 'DOWN', 'AMB', 'SYS'])
    meta_data = ctx.get_batch_and_sn()
    batch_sn = 0
    if(len(meta_data) > 1):
        batch_sn = meta_data[0]
        ctx.log(f'Found board SN:{batch_sn}')
    ctx.log(f'Starting tests with meter: {batch_sn} at dut pos:{dut}')
    for flow in steps:
        # number of sub readings 
        ctx.set_target_flow(flow)
        ctx.sleep(3)
        # ctx.log(f'Setting flow to {flow}')
        #obtain 5 readings per flow
        for n in range(0,3):
            if ctx.stopped:
                return
            ctx.sleep(2)
            #get data points
            flow_actual = ctx.read_flow_actual()
            dut_regs = ctx.read_dut_regs()

            #concurrent access from this thread and UI thread periodically cause Nones to occur
            # TODO fix concurrency (not really a big deal)
            failure_ctr = 0
            while not flow_actual or not dut_regs:
                #return if continual error
                # ctx.log('None type detected')
                ctx.sleep(.1)
                if failure_ctr > 5:
                    df.to_csv('failed_test.csv')
                    ctx.log('Test failed!')
                    ctx.set_isolation_valve(False)
                    ctx.set_pid_enable(False)
                    ctx._stop.set()
                    return
                failure_ctr += 1
                flow_actual = ctx.read_flow_actual()
                dut_regs = ctx.read_dut_regs()
            
            #add new data to row
            row = {'TARGET':flow,'FLOW':flow_actual,'UP':ieee754_to_float(0,dut_regs),'DOWN':ieee754_to_float(2,dut_regs),'AMB':ieee754_to_float(4,dut_regs),'SYS':ieee754_to_float(6,dut_regs)}
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            #continue to get next reading
    ctx.log("Flow ramp done")
    print(df)
    datetime.date
    file_name = f'DUT{dut}-{datetime.now().strftime("%Y-%m-%d-%H-%M")}test'
    df = ta.mod_dataset(df)
    # further processing
    df.to_csv(f'.//python//tests//batch//{file_name}.csv')
    df.to_sql(f'{file_name}',conn,if_exists='replace',index=False)
    ctx.clear_heater()
    ctx.clear_heater()
    #allow flow to ramp down before closing valves
    ctx.set_target_flow(0)
    ctx.sleep(10)
    ctx.set_isolation_valve(False)
    ctx.set_pid_enable(False)
    cur.close()
    conn.close()

def _test_ramp_continous(ctx: TestContext):
    while not ctx.stopped:
        for dut in range(0,5):
            ctx.log(f'Starting tests for DUT{dut}')
            ctx.set_active_dut(dut)
            _test_flow_ramp(ctx,dut)
            pass

def _test_flush(ctx: TestContext):
    #flush dut number 1 (index 0)!!!!
    ctx.log('Flushing')
    ctx.flush_active_line()

def _test_set_heater(ctx: TestContext):
    ctx.log('Setting heater')
    ctx.set_heater()

def _test_clear_heater(ctx: TestContext):
    ctx.log('Setting heater')
    ctx.clear_heater()


def _test_coil_sequence(ctx: TestContext):
    """Skeleton: exercise coils in sequence."""
    ctx.log("Testing each coil")
    # TODO: step through coils, set/clear, verify state
    for i in range(0,5):
        ctx.set_active_dut(i)
        ctx.log(f'Set coil {i}')
        ctx.sleep(7)
    ctx.clear_duts()
    ctx.log("Coil sequence done")


def _test_dut_cycle(ctx: TestContext):
    ctx.log('Opening active line')
    ctx.set_active_dut(ctx.read_active_dut())

def _test_single_meter_continuous(ctx: TestContext):
    dut = ctx.read_active_dut()
    # making sure concurrent reads don't always return 0
    #kinda jank
    if ctx.read_active_dut() != dut:
        dut = ctx.read_active_dut()
    while not ctx.stopped:
        ctx.log(f'Reading contents from {dut}')
        ctx.set_active_dut(dut)
        _test_flow_ramp(ctx,dut)
    

def _test_steady_state(ctx: TestContext):
    """Skeleton: hold a setpoint and log stability over time."""
    ctx.log(f'BATCH: {ctx.read_dut_regs()[8]}, SN:{ctx.read_dut_regs()[9]}')
    

# Registry: (display name, function)
TESTS = [
    ("Flow Ramp",       _test_flow_ramp),
    ("Coil Sequence",   _test_coil_sequence),
    ("Continous Flow Measure",_test_ramp_continous),
    ("Get Batch Info",    _test_steady_state),
    ("Flush",    _test_flush),
    ("Heater ON",    _test_set_heater),
    ("Heater OFF",    _test_clear_heater),
    ("Open Active DUT",    _test_dut_cycle),
    ("Continous DUT",    _test_single_meter_continuous),

]


# ─────────────────────────────────────────────────────────────────────────────
#  WIDGETS
# ─────────────────────────────────────────────────────────────────────────────

class ReadingRow(tk.Frame):
    def __init__(self, parent, label, reg_addr, **kwargs):
        super().__init__(parent, bg=PANEL, **kwargs)
        self.configure(highlightbackground=BORDER, highlightthickness=1, padx=16, pady=10)
        left = tk.Frame(self, bg=PANEL)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(left, text=label, bg=PANEL, fg=TEXT,
                 font=("Helvetica", 11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(left, text=f"Reg  {reg_addr} / {reg_addr+1}", bg=PANEL, fg=SUBTEXT,
                 font=("Courier", 9), anchor="w").pack(anchor="w")
        self.value_label = tk.Label(self, text="---", bg=PANEL, fg=ACCENT,
                                    font=("Courier", 13, "bold"), anchor="e")
        self.value_label.pack(side=tk.RIGHT)

    def update_value(self, val: float):
        self.value_label.config(text=f"{val:.6f}")


class TargetFlowRow(tk.Frame):
    def __init__(self, parent, initial_value=0, **kwargs):
        super().__init__(parent, bg=PANEL, **kwargs)
        self.configure(highlightbackground=BORDER, highlightthickness=1, padx=16, pady=10)
        left = tk.Frame(self, bg=PANEL)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(left, text="Target Flow", bg=PANEL, fg=TEXT,
                 font=("Helvetica", 11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(left, text=f"Reg  {REG_TARGET_FLOW}", bg=PANEL, fg=SUBTEXT,
                 font=("Courier", 9), anchor="w").pack(anchor="w")
        right = tk.Frame(self, bg=PANEL)
        right.pack(side=tk.RIGHT, padx=(12, 0))
        self.entry = tk.Entry(right, width=8, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                              font=("Courier", 12), relief=tk.FLAT, justify="right")
        self.entry.pack(side=tk.LEFT, padx=(0, 8))
        self.entry.insert(0, str(initial_value))
        self.send_btn = tk.Button(right, text="Set", bg=ACCENT, fg="white",
                                  font=("Helvetica", 10, "bold"), relief=tk.FLAT,
                                  padx=10, pady=4, cursor="hand2",
                                  activebackground="#3a7de0", activeforeground="white",
                                  command=self.send)
        self.send_btn.pack(side=tk.LEFT)
        self.status = tk.Label(right, text="", bg=PANEL, fg=SUBTEXT,
                               font=("Helvetica", 8), width=4)
        self.status.pack(side=tk.LEFT, padx=(6, 0))
        self.entry.bind("<Return>", lambda e: self.send())

    def update_value(self, val: float):
        self.entry.delete(0,tk.END)
        self.entry.insert(0,f'{val:.1f}')

    def send(self):
        try:
            val = int(self.entry.get())
            if val < 0 or val > 65535:
                raise ValueError
        except ValueError:
            self.status.config(text="ERR", fg=OFF_COLOR)
            return
        success = c.write_single_register(REG_TARGET_FLOW, val)
        # print(f'Wrote {self.entry.get()} to {REG_TARGET_FLOW}')
        self.status.config(text="OK" if success else "FAIL",
                           fg=ON_COLOR if success else OFF_COLOR)
        self.after(2000, lambda: self.status.config(text=""))


class ActiveDutRow(tk.Frame):
    def __init__(self, parent, initial_value=0, **kwargs):
        super().__init__(parent, bg=PANEL, **kwargs)
        self.configure(highlightbackground=BORDER, highlightthickness=1, padx=16, pady=10)
        left = tk.Frame(self, bg=PANEL)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(left, text="Active DUT", bg=PANEL, fg=TEXT,
                 font=("Helvetica", 11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(left, text=f"Reg  {REG_ACTIVE_DUT}", bg=PANEL, fg=SUBTEXT,
                 font=("Courier", 9), anchor="w").pack(anchor="w")
        right = tk.Frame(self, bg=PANEL)
        right.pack(side=tk.RIGHT, padx=(12, 0))
        self.entry = tk.Entry(right, width=8, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                              font=("Courier", 12), relief=tk.FLAT, justify="right")
        self.entry.pack(side=tk.LEFT, padx=(0, 8))
        self.entry.insert(0, str(initial_value))
        self.send_btn = tk.Button(right, text="Set", bg=ACCENT, fg="white",
                                  font=("Helvetica", 10, "bold"), relief=tk.FLAT,
                                  padx=10, pady=4, cursor="hand2",
                                  activebackground="#3a7de0", activeforeground="white",
                                  command=self.send)
        self.send_btn.pack(side=tk.LEFT)
        self.status = tk.Label(right, text="", bg=PANEL, fg=SUBTEXT,
                               font=("Helvetica", 8), width=4)
        self.status.pack(side=tk.LEFT, padx=(6, 0))
        self.entry.bind("<Return>", lambda e: self.send())

    def update_value(self, val: float):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, f'{val:.1f}')

    def send(self):
        try:
            val = int(self.entry.get())
            if val < 0 or val > 65535:
                raise ValueError
        except ValueError:
            self.status.config(text="ERR", fg=OFF_COLOR)
            return
        success = c.write_single_register(REG_ACTIVE_DUT, val)
        # print(f'Wrote {self.entry.get()} to {REG_ACTIVE_DUT}')
        self.status.config(text="OK" if success else "FAIL",
                           fg=ON_COLOR if success else OFF_COLOR)
        self.after(2000, lambda: self.status.config(text=""))


class CoilToggle(tk.Frame):
    def __init__(self, parent, label, address, initial_state=False, **kwargs):
        super().__init__(parent, bg=PANEL, **kwargs)
        self.address = address
        self.state = initial_state
        self._write_pending = False
        self.configure(highlightbackground=BORDER, highlightthickness=1, padx=16, pady=12)
        left = tk.Frame(self, bg=PANEL)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(left, text=label, bg=PANEL, fg=TEXT,
                 font=("Helvetica", 11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(left, text=f"Coil  {address}", bg=PANEL, fg=SUBTEXT,
                 font=("Courier", 9), anchor="w").pack(anchor="w")
        right = tk.Frame(self, bg=PANEL)
        right.pack(side=tk.RIGHT, padx=(12, 0))
        init_text  = "ON"  if initial_state else "OFF"
        init_color = ON_COLOR if initial_state else OFF_COLOR
        self.status_label = tk.Label(right, text=init_text, bg=init_color, fg="white",
                                     font=("Helvetica", 9, "bold"), width=5, pady=2, padx=6)
        self.status_label.pack(side=tk.LEFT, padx=(0, 10))
        self.btn = tk.Button(right, text="Toggle", bg=ACCENT, fg="white",
                             font=("Helvetica", 10, "bold"), relief=tk.FLAT,
                             padx=12, pady=4, cursor="hand2",
                             activebackground="#3a7de0", activeforeground="white",
                             command=self.toggle)
        self.btn.pack(side=tk.LEFT)

    def toggle(self):
        self.state = not self.state
        self._write_pending = True
        success = c.write_single_coil(self.address + COIL_ADDRESS_BASE - 1, self.state)
        if success:
            self.status_label.config(text="ON" if self.state else "OFF",
                                     bg=ON_COLOR if self.state else OFF_COLOR)
            self.after(1000, self._clear_pending)
        else:
            self.state = not self.state
            self._write_pending = False
            self.status_label.config(text="ERR", bg="#e67e22")

    def _clear_pending(self):
        self._write_pending = False

    def update_from_poll(self, state: bool):
        if self._write_pending:
            return
        self.state = state
        self.status_label.config(text="ON" if state else "OFF",
                                 bg=ON_COLOR if state else OFF_COLOR)


class SparkGraph(tk.Frame):
    W = 340
    H = 120
    PAD = 8

    def __init__(self, parent, label, color, data_deque, **kwargs):
        super().__init__(parent, bg=PANEL, **kwargs)
        self.configure(highlightbackground=BORDER, highlightthickness=1)
        self.color = color
        self.data  = data_deque
        header = tk.Frame(self, bg=PANEL)
        header.pack(fill=tk.X, padx=10, pady=(8, 0))
        tk.Label(header, text=label, bg=PANEL, fg=TEXT,
                 font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        self.live_label = tk.Label(header, text="---", bg=PANEL, fg=color,
                                   font=("Courier", 11, "bold"))
        self.live_label.pack(side=tk.RIGHT)
        self.canvas = tk.Canvas(self, bg=PANEL, width=self.W, height=self.H,
                                highlightthickness=0)
        self.canvas.pack(padx=10, pady=(4, 8))
        self._draw()

    def update(self):
        self._draw()

    def _draw(self):
        cv = self.canvas
        cv.delete("all")
        data = list(self.data)
        if not data:
            return
        self.live_label.config(text=f"{data[-1]:.4f}")
        for frac in (0.25, 0.5, 0.75):
            y = self.PAD + frac * (self.H - 2 * self.PAD)
            cv.create_line(0, y, self.W, y, fill=BORDER, width=1)
        mn, mx = min(data), max(data)
        rng = mx - mn if mx != mn else 1.0

        def px(i):
            return self.PAD + i * (self.W - 2 * self.PAD) / max(len(data) - 1, 1)
        def py(v):
            return self.H - self.PAD - (v - mn) / rng * (self.H - 2 * self.PAD)

        pts = []
        for i, v in enumerate(data):
            pts += [px(i), py(v)]
        fill_pts = [self.PAD, self.H - self.PAD] + pts + [px(len(data)-1), self.H - self.PAD]
        cv.create_polygon(fill_pts, fill=self.color, stipple="gray25", outline="")
        if len(data) >= 2:
            cv.create_line(pts, fill=self.color, width=2, smooth=True)
        cv.create_text(self.W - 2, self.PAD,          anchor="ne", text=f"{mx:.3f}", fill=SUBTEXT, font=("Courier", 7))
        cv.create_text(self.W - 2, self.H - self.PAD, anchor="se", text=f"{mn:.3f}", fill=SUBTEXT, font=("Courier", 7))
        cv.create_text(2,          self.H // 2,        anchor="w",  text=f"{len(data)}", fill=SUBTEXT, font=("Courier", 7))


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self, initial_state: dict):
        super().__init__()
        self.title("Flow Rig Control")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(500, 560)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._test_thread   = None
        self._test_stop     = threading.Event()

        connected = any(v is not None for v in initial_state.values())

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TNotebook",      background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",  background=PANEL, foreground=SUBTEXT,
                        padding=[14, 6],  font=("Helvetica", 9, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", BG)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.grid(row=0, column=0, sticky="nsew")

        # ── Tab 1: Control ───────────────────────────────────────────────────
        tab_ctrl = tk.Frame(nb, bg=BG)
        tab_ctrl.rowconfigure(1, weight=1)
        tab_ctrl.columnconfigure(0, weight=1)
        nb.add(tab_ctrl, text="  Control  ")

        header = tk.Frame(tab_ctrl, bg=BG, pady=14, padx=24)
        header.grid(row=0, column=0, sticky="ew")
        tk.Label(header, text="FLOW RIG CONTROL", bg=BG, fg=ACCENT,
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        tk.Label(header, text="Flow Rig", bg=BG, fg=TEXT,
                 font=("Helvetica", 18, "bold")).pack(anchor="w")
        conn_color = ON_COLOR if connected else OFF_COLOR
        conn_text  = "172.16.100.50 : 502  ·  Connected" if connected else \
                     "172.16.100.50 : 502  ·  No connection at startup"
        tk.Label(header, text=conn_text, bg=BG, fg=conn_color,
                 font=("Courier", 9)).pack(anchor="w")
        tk.Frame(tab_ctrl, bg=BORDER, height=1).grid(row=0, column=0, sticky="sew", padx=24)

        outer = tk.Frame(tab_ctrl, bg=BG)
        outer.grid(row=1, column=0, sticky="nsew")
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        container = tk.Frame(canvas, bg=BG, padx=24, pady=16)
        cw = canvas.create_window((0, 0), window=container, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._section_label(container, "READINGS")
        init_target = initial_state['target_flow'] or 0
        self.target_flow_row = TargetFlowRow(container, initial_value=init_target)
        self.target_flow_row.pack(fill=tk.X, pady=4)

        init_active_dut = initial_state['active_dut'] or 0
        self.active_dut_row = ActiveDutRow(container, initial_value=init_active_dut)
        self.active_dut_row.pack(fill=tk.X, pady=4)

        self.flow_actual_row = ReadingRow(container, "Flow Actual", REG_FLOW_ACTUAL)
        self.flow_actual_row.pack(fill=tk.X, pady=4)
        if initial_state['flow_actual'] is not None:
            self.flow_actual_row.update_value(initial_state['flow_actual'])

        self.dut_rows = {}
        dut_fields = [
            ("DUT Upstream",   REG_DUT_UP_MSB,   0),
            ("DUT Downstream", REG_DUT_DOWN_MSB,  2),
            ("DUT Ambient",    REG_DUT_AMB_MSB,   4),
            ("DUT System",     REG_DUT_SYS_MSB,   6),
        ]
        for label, msb_addr, offset in dut_fields:
            row = ReadingRow(container, label, msb_addr)
            row.pack(fill=tk.X, pady=4)
            self.dut_rows[msb_addr] = row
            if initial_state['dut_regs'] is not None:
                regs = initial_state['dut_regs']
                row.update_value(msb_lsb_to_float(regs[offset], regs[offset+1]))

        self._section_label(container, "COILS")
        self.coil_toggles = []
        coil_states = initial_state['coils'] or [False] * 8
        for i, (label, addr) in enumerate(COILS):
            toggle = CoilToggle(container, label, addr, initial_state=coil_states[i])
            toggle.pack(fill=tk.X, pady=4)
            self.coil_toggles.append(toggle)

        tk.Frame(tab_ctrl, bg=BORDER, height=1).grid(row=2, column=0, sticky="ew", padx=24)
        self.poll_status = tk.Label(tab_ctrl, text="Starting poll...", bg=BG, fg=SUBTEXT,
                                    font=("Helvetica", 8), pady=6)
        self.poll_status.grid(row=3, column=0)

        # ── Tab 2: Graphs ────────────────────────────────────────────────────
        tab_graph = tk.Frame(nb, bg=BG)
        tab_graph.rowconfigure(1, weight=1)
        tab_graph.columnconfigure(0, weight=1)
        tab_graph.columnconfigure(1, weight=1)
        nb.add(tab_graph, text="  Graphs  ")

        live_bar = tk.Frame(tab_graph, bg=PANEL, pady=10)
        live_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(live_bar, text="ACTUAL FLOW", bg=PANEL, fg=SUBTEXT,
                 font=("Helvetica", 8, "bold")).pack(side=tk.LEFT, padx=(20, 8))
        self.flow_live_big = tk.Label(live_bar, text="---", bg=PANEL, fg=C_FLOW,
                                      font=("Courier", 22, "bold"))
        self.flow_live_big.pack(side=tk.LEFT)
        tk.Label(live_bar, text="units", bg=PANEL, fg=SUBTEXT,
                 font=("Helvetica", 9)).pack(side=tk.LEFT, padx=(4, 0))
        self.graph_poll_status = tk.Label(live_bar, text="", bg=PANEL, fg=SUBTEXT,
                                          font=("Helvetica", 8))
        self.graph_poll_status.pack(side=tk.RIGHT, padx=20)

        graph_frame = tk.Frame(tab_graph, bg=BG)
        graph_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=16, pady=16)
        for i in range(2):
            graph_frame.rowconfigure(i, weight=1)
            graph_frame.columnconfigure(i, weight=1)

        self.graph_up   = SparkGraph(graph_frame, "DUT Upstream",   C_UP,   history_up)
        self.graph_down = SparkGraph(graph_frame, "DUT Downstream", C_DOWN, history_down)
        self.graph_amb  = SparkGraph(graph_frame, "DUT Ambient",    C_AMB,  history_amb)
        self.graph_flow = SparkGraph(graph_frame, "Flow Actual",    C_FLOW, history_flow)
        self.graph_up.grid  (row=0, column=0, padx=6, pady=6, sticky="nsew")
        self.graph_down.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        self.graph_amb.grid (row=1, column=0, padx=6, pady=6, sticky="nsew")
        self.graph_flow.grid(row=1, column=1, padx=6, pady=6, sticky="nsew")

        # ── Tab 3: Tests ─────────────────────────────────────────────────────
        tab_test = tk.Frame(nb, bg=BG)
        tab_test.rowconfigure(1, weight=1)
        tab_test.columnconfigure(0, weight=1)
        nb.add(tab_test, text="  Tests  ")

        # Header bar
        test_header = tk.Frame(tab_test, bg=BG, pady=14, padx=24)
        test_header.grid(row=0, column=0, sticky="ew")
        tk.Label(test_header, text="TEST RUNNER", bg=BG, fg=ACCENT,
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        tk.Label(test_header, text="Flow Rig Tests", bg=BG, fg=TEXT,
                 font=("Helvetica", 18, "bold")).pack(anchor="w")
        tk.Frame(tab_test, bg=BORDER, height=1).grid(row=0, column=0, sticky="sew", padx=24)

        # Body: test list left, log right
        body = tk.Frame(tab_test, bg=BG)
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=12)
        body.rowconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        # Left: test selector
        left_panel = tk.Frame(body, bg=PANEL,
                              highlightbackground=BORDER, highlightthickness=1)
        left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 8))

        tk.Label(left_panel, text="SELECT TEST", bg=PANEL, fg=SUBTEXT,
                 font=("Helvetica", 8, "bold"), padx=14, pady=8).pack(anchor="w")
        tk.Frame(left_panel, bg=BORDER, height=1).pack(fill=tk.X)

        self._test_var = tk.StringVar(value=TESTS[0][0])
        for name, _ in TESTS:
            rb = tk.Radiobutton(left_panel, text=name, variable=self._test_var,
                                value=name, bg=PANEL, fg=TEXT, selectcolor=ENTRY_BG,
                                activebackground=PANEL, activeforeground=ACCENT,
                                font=("Helvetica", 10), padx=14, pady=6,
                                indicatoron=True)
            rb.pack(anchor="w", fill=tk.X)

        tk.Frame(left_panel, bg=BORDER, height=1).pack(fill=tk.X, pady=(8, 0))

        btn_row = tk.Frame(left_panel, bg=PANEL, padx=12, pady=10)
        btn_row.pack(fill=tk.X)

        self._run_btn = tk.Button(btn_row, text="▶  Run", bg=ON_COLOR, fg="white",
                                  font=("Helvetica", 10, "bold"), relief=tk.FLAT,
                                  padx=12, pady=6, cursor="hand2",
                                  command=self._run_test)
        self._run_btn.pack(side=tk.LEFT, padx=(0, 6))

        self._stop_btn = tk.Button(btn_row, text="■  Stop", bg=OFF_COLOR, fg="white",
                                   font=("Helvetica", 10, "bold"), relief=tk.FLAT,
                                   padx=12, pady=6, cursor="hand2", state=tk.DISABLED,
                                   command=self._stop_test)
        self._stop_btn.pack(side=tk.LEFT)

        self._test_status = tk.Label(left_panel, text="Idle", bg=PANEL, fg=SUBTEXT,
                                     font=("Helvetica", 8), pady=4)
        self._test_status.pack()

        # Right: log output
        right_panel = tk.Frame(body, bg=PANEL,
                               highlightbackground=BORDER, highlightthickness=1)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        log_header = tk.Frame(right_panel, bg=PANEL)
        log_header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(8, 4))
        tk.Label(log_header, text="TEST LOG", bg=PANEL, fg=SUBTEXT,
                 font=("Helvetica", 8, "bold")).pack(side=tk.LEFT)
        tk.Button(log_header, text="Clear", bg=ENTRY_BG, fg=SUBTEXT,
                  font=("Helvetica", 8), relief=tk.FLAT, padx=6, pady=2,
                  cursor="hand2", command=self._clear_log).pack(side=tk.RIGHT)

        tk.Frame(right_panel, bg=BORDER, height=1).grid(row=0, column=0,
                                                         columnspan=2, sticky="sew", padx=0)

        self._log_text = tk.Text(right_panel, bg=PANEL, fg=TEXT,
                                 font=("Courier", 9), relief=tk.FLAT,
                                 wrap=tk.WORD, state=tk.DISABLED,
                                 insertbackground=TEXT, padx=12, pady=8)
        log_scroll = tk.Scrollbar(right_panel, orient="vertical",
                                  command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=log_scroll.set)
        self._log_text.grid(row=1, column=0, sticky="nsew")
        log_scroll.grid(row=1, column=1, sticky="ns")

        # Footer
        tk.Frame(tab_test, bg=BORDER, height=1).grid(row=2, column=0, sticky="ew", padx=24)

        #faciliates focus shifting        
        self.bind_all("<Button-1>", lambda event: event.widget.focus_set())

        self.after(100, self._poll)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=SUBTEXT,
                 font=("Helvetica", 8, "bold"), anchor="w").pack(fill=tk.X, pady=(8, 2))

    def _append_log(self, msg: str):
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.insert(tk.END, msg + "\n")
        self._log_text.see(tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def _clear_log(self):
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.delete("1.0", tk.END)
        self._log_text.configure(state=tk.DISABLED)

    # ── Test runner ───────────────────────────────────────────────────────────

    def _run_test(self):
        if self._test_thread and self._test_thread.is_alive():
            return

        name = self._test_var.get()
        fn   = next(f for n, f in TESTS if n == name)

        self._test_stop.clear()
        self._run_btn.config(state=tk.DISABLED)
        self._stop_btn.config(state=tk.NORMAL)
        self._test_status.config(text=f"Running: {name}", fg=WARN)
        self._append_log(f"{'─'*40}")
        self._append_log(f"START  {name}")
        self._append_log(f"{'─'*40}")

        ctx = TestContext(
            log_fn     = lambda msg: self.after(0, lambda m=msg: self._append_log(m)),
            stop_event = self._test_stop,
        )

        def _worker():
            try:
                fn(ctx)
                result = "STOPPED" if ctx.stopped else "COMPLETE"
            except Exception as e:
                result = f"ERROR: {e}"
            self.after(0, lambda r=result: self._on_test_done(r))

        self._test_thread = threading.Thread(target=_worker, daemon=True)
        self._test_thread.start()

    def _stop_test(self):
        self._test_stop.set()

    def _on_test_done(self, result: str):
        color = ON_COLOR if result == "COMPLETE" else OFF_COLOR
        self._append_log(f"{'─'*40}")
        self._append_log(f"RESULT  {result}")
        self._run_btn.config(state=tk.NORMAL)
        self._stop_btn.config(state=tk.DISABLED)
        self._test_status.config(text=result, fg=color)

    # ── Poll ──────────────────────────────────────────────────────────────────

    def _poll(self):
        def fetch():
            try:
                dut_regs = c.read_holding_registers(REG_DUT_UP_MSB, 8)
                flow_reg = c.read_holding_registers(REG_FLOW_ACTUAL, 3)
                coil_reg = c.read_coils(COIL_ADDRESS_BASE, 8)

                results = {}
                if flow_reg and flow_reg[0] < 40000:
                    results['flow_actual'] = flow_reg[0] / 10
                    results['target_flow'] = flow_reg[1]
                    results['active_dut']  = flow_reg[2]
                else:
                    results['flow_actual'] = 0.0
                if dut_regs and len(dut_regs) == 8:
                    results[REG_DUT_UP_MSB]   = msb_lsb_to_float(dut_regs[0], dut_regs[1])
                    results[REG_DUT_DOWN_MSB] = msb_lsb_to_float(dut_regs[2], dut_regs[3])
                    results[REG_DUT_AMB_MSB]  = msb_lsb_to_float(dut_regs[4], dut_regs[5])
                    results[REG_DUT_SYS_MSB]  = msb_lsb_to_float(dut_regs[6], dut_regs[7])
                if coil_reg and len(coil_reg) == 8:
                    results['coils'] = coil_reg

                self.after(0, lambda: self._update_ui(results, ok=True))
            except Exception:
                self.after(0, lambda: self._update_ui({}, ok=False))

        threading.Thread(target=fetch, daemon=True).start()
        self.after(POLL_INTERVAL_MS, self._poll)

    def _update_ui(self, results, ok: bool):
        if not ok:
            self.poll_status.config(text="Connection error", fg=OFF_COLOR)
            self.graph_poll_status.config(text="Connection error", fg=OFF_COLOR)
            return

        status_text = f"Live  ·  {POLL_INTERVAL_MS}ms poll"
        self.poll_status.config(text=status_text, fg=ON_COLOR)
        self.graph_poll_status.config(text=status_text, fg=ON_COLOR)

        if 'flow_actual' in results:
            self.flow_actual_row.update_value(results['flow_actual'])
            history_flow.append(results['flow_actual'])
            self.flow_live_big.config(text=f"{results['flow_actual']:.4f}")

        if 'target_flow' in results:
            if self.focus_get() == self.target_flow_row.entry:
                pass
            else:
                self.target_flow_row.update_value(results['target_flow'])

        if 'active_dut' in results:
            if self.focus_get() == self.active_dut_row.entry:
                pass
            else:
                self.active_dut_row.update_value(results['active_dut'])

        for msb_addr, row in self.dut_rows.items():
            if msb_addr in results:
                row.update_value(results[msb_addr])

        if REG_DUT_UP_MSB   in results: history_up.append(results[REG_DUT_UP_MSB])
        if REG_DUT_DOWN_MSB in results: history_down.append(results[REG_DUT_DOWN_MSB])
        if REG_DUT_AMB_MSB  in results: history_amb.append(results[REG_DUT_AMB_MSB])

        self.graph_up.update()
        self.graph_down.update()
        self.graph_amb.update()
        self.graph_flow.update()

        if 'coils' in results:
            for i, toggle in enumerate(self.coil_toggles):
                toggle.update_from_poll(results['coils'][i])


if __name__ == "__main__":
    print("Connecting to 172.16.100.50:502 ...")
    initial_state = read_initial_state()

    if any(v is not None for v in initial_state.values()):
        print("  Startup read OK")
        print(f"  Target flow : {initial_state['target_flow']}")
        print(f"  Flow actual : {initial_state['flow_actual']}")
        print(f"  Active DUT  : {initial_state['active_dut']}")
        print(f"  Coils       : {initial_state['coils']}")
        print(f"  DUT regs    : {initial_state['dut_regs']}")
    else:
        print("  WARNING: Could not read initial state — check connection")

    app = App(initial_state)
    app.mainloop()