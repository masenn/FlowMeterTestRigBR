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
class Tester:

    def __init__(self):
        self.c = ModbusTcpClient('172.16.100.50')

        pass
    #included for compatability 
    def log(msg):
        print(msg)

    
    # Modbus helpers
    def set_target_flow(self, value: int):
        self.c.write_single_register(REG_TARGET_FLOW, value)
        
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
    



    def _test_flow_ramp(self,dut=0,heater_tries=1):
        conn = sqlite3.connect(f'python/contdut.db')
        cur = conn.cursor()
        self.log("Flow ramp - Starting up!")
        #remember, this is 1 indexed to align with physical cables 
        self.set_isolation_valve(True)
        set_pid_enable(True)
        sleep(3)
        flush_active_line(duration=25)
        set_heater()
        set_heater()
        steps = range(300, 2500, 100)
        df = pd.DataFrame(columns=['TARGET','FLOW','UP', 'DOWN', 'AMB', 'SYS'])
        meta_data = get_batch_and_sn()
        batch_sn = 0
        if(len(meta_data) > 1):
            batch_sn = meta_data[0]
            log(f'Found board SN:{batch_sn}')
        log(f'Starting tests with meter: {batch_sn} at dut pos:{dut}')
        for flow in steps:
            # number of sub readings 
            set_target_flow(flow)
            sleep(3)
            # log(f'Setting flow to {flow}')
            #obtain 5 readings per flow
            for n in range(0,3):
                if stopped:
                    return
                sleep(2)
                #get data points
                flow_actual = read_flow_actual()
                dut_regs = read_dut_regs()

                #concurrent access from this thread and UI thread periodically cause Nones to occur
                # TODO fix concurrency (not really a big deal)
                failure_ctr = 0
                while not flow_actual or not dut_regs:
                    #return if continual error
                    # log('None type detected')
                    sleep(.1)
                    if failure_ctr > 5:
                        df.to_csv('failed_test.csv')
                        log('Test failed!')
                        set_isolation_valve(False)
                        set_pid_enable(False)
                        _stop.set()
                        return
                    failure_ctr += 1
                    flow_actual = read_flow_actual()
                    dut_regs = read_dut_regs()
                
                #add new data to row
                row = {'TARGET':flow,'FLOW':flow_actual,'UP':ieee754_to_float(0,dut_regs),'DOWN':ieee754_to_float(2,dut_regs),'AMB':ieee754_to_float(4,dut_regs),'SYS':ieee754_to_float(6,dut_regs)}
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                #continue to get next reading
        log("Flow ramp done")
        print(df)
        datetime.date
        file_name = f'DUT{dut}-{datetime.now().strftime("%Y-%m-%d-%H-%M")}test'
        df = ta.mod_dataset(df)
        # further processing
        df.to_csv(f'.//python//tests//batch//{file_name}.csv')
        df.to_sql(f'{file_name}',conn,if_exists='replace',index=False)
        clear_heater()
        clear_heater()
        #allow flow to ramp down before closing valves
        set_target_flow(0)
        sleep(10)
        set_isolation_valve(False)
        set_pid_enable(False)
        cur.close()
        conn.close()

