import tkinter as tk
import threading
import struct
from pyModbusTCP.client import ModbusClient

# Modbus client
c = ModbusClient(host='172.16.100.50', port=502, unit_id=1, auto_open=True, auto_close=True)

POLL_INTERVAL_MS = 500  # poll every 500ms

# Coil definitions: (label, coil_address)
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

# Holding register addresses
REG_TARGET_FLOW  = 101
REG_FLOW_ACTUAL  = 102
REG_DUT_UP_MSB   = 200
REG_DUT_UP_LSB   = 201
REG_DUT_DOWN_MSB = 202
REG_DUT_DOWN_LSB = 203
REG_DUT_AMB_MSB  = 204
REG_DUT_AMB_LSB  = 205
REG_DUT_SYS_MSB  = 206
REG_DUT_SYS_LSB  = 207

# Colors
BG       = "#1a1e2e"
PANEL    = "#232842"
ACCENT   = "#4f8ef7"
ON_COLOR = "#2ecc71"
OFF_COLOR= "#e74c3c"
TEXT     = "#e8eaf0"
SUBTEXT  = "#7a80a0"
BORDER   = "#2e3450"
ENTRY_BG = "#2e3450"


def msb_lsb_to_float(msb: int, lsb: int) -> float:
    """Combine two 16-bit unsigned registers into an IEEE 754 float (big-endian word order)."""
    raw = ((msb & 0xFFFF) << 16) | (lsb & 0xFFFF)
    return struct.unpack('>f', struct.pack('>I', raw))[0]


def read_initial_state() -> dict:
    """
    Read all coils and registers once at startup.
    Returns a dict with coil states, target_flow, flow_actual, and dut_regs.
    Any failed read leaves that key as None — UI shows --- for missing values.
    """
    state = {
        'coils': None,
        'target_flow': None,
        'flow_actual': None,
        'dut_regs': None,
    }
    try:
        coils = c.read_coils(1, 8)
        if coils and len(coils) == 8:
            state['coils'] = coils

        target = c.read_holding_registers(REG_TARGET_FLOW, 1)
        if target:
            state['target_flow'] = target[0]

        flow = c.read_holding_registers(REG_FLOW_ACTUAL, 1)
        if flow:
            state['flow_actual'] = float(flow[0])

        dut = c.read_holding_registers(REG_DUT_UP_MSB, 8)
        if dut and len(dut) == 8:
            state['dut_regs'] = dut

    except Exception:
        pass

    return state


class ReadingRow(tk.Frame):
    """A read-only display row for a polled float value."""
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
        self.value_label.config(text=f"{val:.4f}")


class TargetFlowRow(tk.Frame):
    """Editable row for target flow (single UINT register)."""
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

    def send(self):
        try:
            val = int(self.entry.get())
            if val < 0 or val > 65535:
                raise ValueError
        except ValueError:
            self.status.config(text="ERR", fg=OFF_COLOR)
            return

        success = c.write_single_register(REG_TARGET_FLOW, val)
        if success:
            self.status.config(text="OK", fg=ON_COLOR)
        else:
            self.status.config(text="FAIL", fg=OFF_COLOR)
        self.after(2000, lambda: self.status.config(text=""))


class CoilToggle(tk.Frame):
    def __init__(self, parent, label, address, initial_state=False, **kwargs):
        super().__init__(parent, bg=PANEL, **kwargs)
        self.address = address
        self.state = initial_state
        self.configure(highlightbackground=BORDER, highlightthickness=1, padx=16, pady=12)

        left = tk.Frame(self, bg=PANEL)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left, text=label, bg=PANEL, fg=TEXT,
                 font=("Helvetica", 11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(left, text=f"Coil  {address}", bg=PANEL, fg=SUBTEXT,
                 font=("Courier", 9), anchor="w").pack(anchor="w")

        right = tk.Frame(self, bg=PANEL)
        right.pack(side=tk.RIGHT, padx=(12, 0))

        init_text = "ON" if initial_state else "OFF"
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
        success = c.write_single_coil(self.address, self.state)
        if success:
            self.status_label.config(text="ON" if self.state else "OFF",
                                     bg=ON_COLOR if self.state else OFF_COLOR)
        else:
            self.state = not self.state
            self.status_label.config(text="ERR", bg="#e67e22")


class App(tk.Tk):
    def __init__(self, initial_state: dict):
        super().__init__()
        self.title("Flow Rig Control")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(460, 500)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        connected = any(v is not None for v in initial_state.values())

        # ── Header ──────────────────────────────────────────
        header = tk.Frame(self, bg=BG, pady=16, padx=24)
        header.grid(row=0, column=0, sticky="ew")

        tk.Label(header, text="FLOW RIG CONTROL", bg=BG, fg=ACCENT,
                 font=("Helvetica", 9, "bold")).pack(anchor="w")
        tk.Label(header, text="Flow Rig", bg=BG, fg=TEXT,
                 font=("Helvetica", 18, "bold")).pack(anchor="w")

        # Connection status in header
        conn_color = ON_COLOR if connected else OFF_COLOR
        conn_text  = "172.16.100.50 : 502  ·  Connected" if connected else "172.16.100.50 : 502  ·  No connection at startup"
        tk.Label(header, text=conn_text, bg=BG, fg=conn_color,
                 font=("Courier", 9)).pack(anchor="w")

        tk.Frame(self, bg=BORDER, height=1).grid(row=1, column=0, sticky="ew", padx=24)

        # ── Scrollable body ──────────────────────────────────
        outer = tk.Frame(self, bg=BG)
        outer.grid(row=2, column=0, sticky="nsew")
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)

        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        container = tk.Frame(canvas, bg=BG, padx=24, pady=16)
        container_window = canvas.create_window((0, 0), window=container, anchor="nw")

        def on_canvas_resize(event):
            canvas.itemconfig(container_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_resize)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        container.bind("<Configure>", on_frame_configure)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # ── Section: Readings ────────────────────────────────
        self._section_label(container, "READINGS")

        init_target = initial_state['target_flow'] or 0
        self.target_flow_row = TargetFlowRow(container, initial_value=init_target)
        self.target_flow_row.pack(fill=tk.X, pady=4)

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
                row.update_value(msb_lsb_to_float(regs[offset], regs[offset + 1]))

        # ── Section: Coils ───────────────────────────────────
        self._section_label(container, "COILS")

        coil_states = initial_state['coils'] or [False] * 8
        for i, (label, addr) in enumerate(COILS):
            CoilToggle(container, label, addr,
                       initial_state=coil_states[i]).pack(fill=tk.X, pady=4)

        # ── Footer ───────────────────────────────────────────
        tk.Frame(self, bg=BORDER, height=1).grid(row=3, column=0, sticky="ew", padx=24)

        self.poll_status = tk.Label(self, text="Starting poll...", bg=BG, fg=SUBTEXT,
                                    font=("Helvetica", 8), pady=8)
        self.poll_status.grid(row=4, column=0)

        self.after(100, self._poll)

    def _section_label(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=SUBTEXT,
                 font=("Helvetica", 8, "bold"), anchor="w").pack(fill=tk.X, pady=(8, 2))

    def _poll(self):
        def fetch():
            try:
                dut_regs = c.read_holding_registers(REG_DUT_UP_MSB, 8)
                flow_reg = c.read_holding_registers(REG_FLOW_ACTUAL, 1)

                results = {}

                if flow_reg:
                    results['flow_actual'] = float(flow_reg[0])

                if dut_regs and len(dut_regs) == 8:
                    results[REG_DUT_UP_MSB]  = msb_lsb_to_float(dut_regs[0], dut_regs[1])
                    results[REG_DUT_DOWN_MSB] = msb_lsb_to_float(dut_regs[2], dut_regs[3])
                    results[REG_DUT_AMB_MSB]  = msb_lsb_to_float(dut_regs[4], dut_regs[5])
                    results[REG_DUT_SYS_MSB]  = msb_lsb_to_float(dut_regs[6], dut_regs[7])

                self.after(0, lambda: self._update_ui(results, ok=True))
            except Exception:
                self.after(0, lambda: self._update_ui({}, ok=False))

        threading.Thread(target=fetch, daemon=True).start()
        self.after(POLL_INTERVAL_MS, self._poll)

    def _update_ui(self, results, ok: bool):
        if not ok:
            self.poll_status.config(text="Connection error", fg=OFF_COLOR)
            return

        self.poll_status.config(text=f"Live  ·  {POLL_INTERVAL_MS}ms poll", fg=ON_COLOR)

        if 'flow_actual' in results:
            self.flow_actual_row.update_value(results['flow_actual'])

        for msb_addr, row in self.dut_rows.items():
            if msb_addr in results:
                row.update_value(results[msb_addr])


if __name__ == "__main__":
    print("Connecting to 172.16.100.50:502 ...")
    initial_state = read_initial_state()

    if any(v is not None for v in initial_state.values()):
        print("  Startup read OK")
        print(f"  Target flow : {initial_state['target_flow']}")
        print(f"  Flow actual : {initial_state['flow_actual']}")
        print(f"  Coils       : {initial_state['coils']}")
        print(f"  DUT regs    : {initial_state['dut_regs']}")
    else:
        print("  WARNING: Could not read initial state — check connection")

    app = App(initial_state)
    app.mainloop()