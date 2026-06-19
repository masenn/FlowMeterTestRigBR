from pymodbus.client import ModbusTcpClient
import sqlite3

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

COIL_FLOW_CONTROLLER = 1
COIL_ISOLATION_VALVE = 2
COIL_PUMP_ENABLE = 3
COIL_DUT1 = 4
COIL_DUT2 = 5
COIL_DUT3 = 6
COIL_DUT4 = 7
COIL_DUT5 = 8
COIL_HEATER_ON = 9
COIL_HEATER_OFF = 10

REG_FLOW_ACTUAL  = 0x00
REG_TARGET_FLOW  = 0x01
REG_ACTIVE_DUT   = 0x02
REG_DUT_UP_MSB   = 0x10
REG_DUT_UP_LSB   = 0x11
REG_DUT_DOWN_MSB = 0x12
REG_DUT_DOWN_LSB = 0x13
REG_DUT_AMB_MSB  = 0x14
REG_DUT_AMB_LSB  = 0x15
REG_DUT_SYS_MSB  = 0x16
REG_DUT_SYS_LSB  = 0x17
REG_DUT_BATCH = 0x18
REG_DUT_BATCHSN = 0x19

class Tester:

    def __init__(self):
        self.c = ModbusTcpClient('172.16.100.50',timeout=3)
        pass

    #included for compatability 
    def log(msg):
        print(msg)

    # Modbus helpers
    def set_target_flow(self, value: int):
        self.c.write_register(REG_TARGET_FLOW, value)
        
    def read_target_flow(self):
        regs = self.c.read_holding_registers(REG_TARGET_FLOW+HOLDING_ADDRESS_BASE,count=1).registers
        if len(regs) < 1:
            return 0
        return regs[0]

    
t = Tester()
print('Hello world')
print(f'Target Flow: {t.read_target_flow()}')