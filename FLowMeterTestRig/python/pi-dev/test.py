from pymodbus.client import ModbusTcpClient
import sqlite3
import struct
import time
import pandas as pd


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

COIL_FLOW_CONTROLLER = 0
COIL_ISOLATION_VALVE = 1
COIL_PUMP_ENABLE = 2
COIL_DUT1 = 3
COIL_DUT2 = 4
COIL_DUT3 = 5
COIL_DUT4 = 6
COIL_DUT5 = 7
COIL_HEATER_ON = 8
COIL_HEATER_OFF = 9

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

NORMALIZED_SUFFIX = '_N'



def ieee754_to_float(base_addr, regs):
    raw = ((regs[base_addr] & 0xFFFF) << 16) | (regs[base_addr+1] & 0xFFFF)
    return struct.unpack('>f', struct.pack('>I', raw))[0]

def normalize(data):
    return data - min(data)

def mod_dataset(df):
    df['t'] = normalize(df['SYS'])
    df['DELTA'] = df['UP'] - df['DOWN']
    df[f'UP{NORMALIZED_SUFFIX}'] = normalize(df['UP'])
    df[f'DOWN{NORMALIZED_SUFFIX}'] = normalize(df['DOWN'])
    df[f'AMB{NORMALIZED_SUFFIX}'] = normalize(df['AMB'])
    df[f'DELTA{NORMALIZED_SUFFIX}'] = normalize(df['DELTA'])
    return df


class SQL_storage:
    
    def __init__(self,db_name : str,data_fields : list):
        self.conn = sqlite3.connect(f'{db_name}.db')
        self.cur = self.conn.cursor()
        self.data_list = data_fields
        # class represents test that was run in full
        self.cur.execute('CREATE TABLE IF NOT EXISTS tests(test_id,dut,test_name,test_type_id)')
        self.cur.execute('CREATE TABLE IF NOT EXISTS readings(test_id,TARGET,FLOW,UP,DOWN,AMB,SYS,t,DELTA,UP_N,DOWN_N,AMB_N,DELTA_N)')
        self.conn.commit()
        pass

    def generate_testid():
        return int(time.time())

    def add_test(self,test_id,dut,test_name,test_type_id):
        self.cur.execute(f'INSERT INTO tests (test_id,dut,test_name,test_type_id) VALUES ({test_id},{dut},\'{test_name}\',{test_type_id});',)
        self.conn.commit()
        pass

    def add_reading(self,test_id,TARGET,FLOW,UP,DOWN,AMB,SYS,t,DELTA,UP_N,DOWN_N,AMB_N,DELTA_N):
        self.cur.execute(f'INSERT INTO readings (test_id,TARGET,FLOW,UP,DOWN,AMB,SYS,t,DELTA,UP_N,DOWN_N,AMB_N,DELTA_N) VALUES ({test_id},{TARGET},{FLOW},{UP},{DOWN},{AMB},{SYS},{t},{DELTA},{UP_N},{DOWN_N},{AMB_N},{DELTA_N});')
        pass
    
    def get_all_tests(self):
        return self.cur.execute('SELECT * FROM tests').fetchall()

    def get_test(self,name):
        return self.cur.execute(f'SELECT * FROM tests WHERE test_id LIKE \'%{name}%\'').fetchall()
    
    def filter_test(self,filter):
        return self.cur.execute(f'SELECT * FROM tests WHERE {filter}').fetchall()
    
    def select_from_test(self):
        pass

    def save_dataframe(self,test_id : int,df : pd.DataFrame):
        for field in self.data_list:
            if field not in list(df):
                raise Exception('Data fields for the database are not supplied')
        pass

    #hardcoded values does not allow for adding or removing measurements 
    def save_dataframe_static(self, test_id: int, df: pd.DataFrame):
        measurements = ['TARGET', 'FLOW', 'UP', 'DOWN', 'AMB', 'SYS', 't', 'DELTA', 'UP_N', 'DOWN_N', 'AMB_N', 'DELTA_N']
        for field in measurements:
            if field not in list(df):
                raise Exception('Data fields for the database are not supplied')
        for _, row in df.iterrows():
            self.add_reading(
                test_id, row['TARGET'], row['FLOW'], row['UP'], row['DOWN'], row['AMB'], row['SYS'],
                row['t'], row['DELTA'], row['UP_N'], row['DOWN_N'], row['AMB_N'], row['DELTA_N']
            )
        self.conn.commit()

class Tester:

    _PLC_ADDRESS = '172.16.100.50'

    def __init__(self):
        self.c = ModbusTcpClient(self._PLC_ADDRESS,timeout=3,reconnect_delay=.1,reconnect_delay_max=30)
        print(self.c)
        pass

    #B&R is a bitch and randomly disconnects so reopening on each transmission (NOT efficient but necesarry)
    def restart_conn(self):
        self.c.close()
        self.c = ModbusTcpClient(self._PLC_ADDRESS)
        time.sleep(.5)

    # helper functions
    def write_reg(self,address,value):
        self.restart_conn()
        self.c.write_register(HOLDING_ADDRESS_BASE + address,value)

    def read_reg(self,address):
        self.restart_conn()
        regs = self.c.read_holding_registers(HOLDING_ADDRESS_BASE + address).registers
        if len(regs) < 1:
            return 0
        return regs[0]
    
    def read_regs(self,address,count):
        self.restart_conn()
        regs = self.c.read_holding_registers(HOLDING_ADDRESS_BASE + address,count=count).registers
        if(len(regs) < count):
            raise Exception('Could not get full register map')
        return regs
    
    def write_coil(self,address,state):
        self.restart_conn()
        self.c.write_coil(COIL_ADDRESS_BASE + address,state)
    
    def write_coils(self,address,values):
        self.restart_conn()
        self.c.write_coils(COIL_ADDRESS_BASE + address,values)

    # LIBRARY FUNCTIONS
    #    addressing happens at system level, not using B&R's offsets
    #       i.e. write_coil(0,True) -- actually writes to coil COIL_ADDRESS_BASE + 0

    # Modbus helpers
    def set_target_flow(self, value: int):
        self.write_reg(REG_TARGET_FLOW, value)
        
    def read_actual_flow(self):

        return self.read_reg(REG_FLOW_ACTUAL)/10

    def read_target_flow(self):
        return self.read_reg(REG_TARGET_FLOW)

    def set_active_dut(self):
        self.write_reg(REG_ACTIVE_DUT)

    def select_dut_solenoid(self,dut):
        states = [False, False, False, False, False]
        states[dut] = True
        self.write_coils(COIL_DUT1,states) 
        pass

    # up, down, amb, sys
    def get_debug_registers(self):
        regs = self.read_regs(REG_DUT_UP_MSB,8)
        return ieee754_to_float(0,regs),\
            ieee754_to_float(2,regs), \
            ieee754_to_float(4,regs), \
            ieee754_to_float(6,regs)
    
    def set_isolation_valve(self,value):
        self.write_coil(COIL_ISOLATION_VALVE,value)
    
    def set_pump_enable(self,value):
        self.write_coil(COIL_PUMP_ENABLE,value)
    
    def set_heater(self):
        self.write_coil(COIL_HEATER_ON, True)

    def clear_heater(self):
        self.write_coil(COIL_HEATER_OFF, True)

    def get_batch_and_sn(self):
        """
            @return batch and sn in an array
        """
        regs = self.read_regs(REG_DUT_BATCH,2)
        if not regs: return [0,0]
        # batch, sn
        return [regs[0],regs[1]]
                    
    
    ################### TESTS ###################

    def cycle_test(self,dut,flush_duration=25,flush_flow=1500):
        self.clear_heater()
        self.set_isolation_valve(True)
        self.set_pump_enable(True)
        self.select_dut_solenoid(dut)

        time.sleep(3)
        print(f'Flushing out at {flush_flow} ccm')
        #flushing 
        self.set_target_flow(flush_flow)
        time.sleep(flush_duration)
        print('Prepping for Tests')
        #test prep
        self.set_heater()
        steps = range(300, 2500, 100)
        df = pd.DataFrame(columns=['TARGET','FLOW','UP', 'DOWN', 'AMB', 'SYS'])
        storage = SQL_storage('./python/pi-dev/test_db',[])
        test_id = SQL_storage.generate_testid()
        storage.add_test(test_id,dut,f'test',-2)
        meta_data = self.get_batch_and_sn()
        batch_sn = 0
        if(len(meta_data) > 1):
            batch_sn = meta_data[0]
            print(f'Found board SN:{batch_sn}')

        
        print(f'Starting tests with meter: {batch_sn} at dut pos:{dut}')
        for flow in steps:
            # number of sub readings 
            self.set_target_flow(flow)
            time.sleep(3)
            # print(f'Setting flow to {flow}')
            #obtain 5 readings per flow
            for n in range(0,3):
                time.sleep(2)
                #get data points
                flow_actual = self.read_actual_flow()
                up,down,amb,sys = self.get_debug_registers()

                #concurrent access from this thread and UI thread periodically cause Nones to occur
                # TODO fix concurrency (not really a big deal)
                failure_ctr = 0
                while not flow_actual or not up:
                    #return if continual error
                    # print('None type detected')
                    time.sleep(.1)
                    if failure_ctr > 5:
                        print('Test failed!')
                        self.set_isolation_valve(False)
                        self.set_pump_enable(False)
                        self._stop.set()
                        return
                    failure_ctr += 1
                    flow_actual = self.read_actual_flow()
                    up,down,amb,sys = self.get_debug_registers()
                
                #add new data to row
                row = {'TARGET':flow,'FLOW':flow_actual,'UP':up,'DOWN':down,'AMB':amb,'SYS':sys}
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                #continue to get next reading
        print("Flow ramp done")
        print(df)
        
        # file_name = f'DUT{dut}-{time..strftime("%Y-%m-%d-%H-%M")}test'
        df = mod_dataset(df)
        # further processing
        # df.to_csv(f'.//python//tests//batch//{file_name}.csv')
        # df.to_sql(f'{file_name}',conn,if_exists='replace',index=False)
        storage.save_dataframe_static(test_id,df)
        self.clear_heater()
        self.clear_heater()
        #allow flow to ramp down before closing valves
        self.set_target_flow(0)
        time.sleep(10)
        self.set_isolation_valve(False)
        self.set_pump_enable(False)
        pass

    
t = Tester()
print('Hello world')
print(f'Target Flow: {t.read_target_flow()}, Actual Flow {t.read_actual_flow()}')
print(t.get_debug_registers())
for i in range(0,10):
    t.cycle_test(0)
