#include "fixedaddr_modbustcp.h"

_GLOBAL REAL flow_actual;
_GLOBAL UINT target_flow;
static uint16_t new_target_flow,old_target_flow;

_GLOBAL BOOL enable_isolation_valve;
_GLOBAL BOOL enable_pump;
_GLOBAL BOOL dut_solenoids[5];
_GLOBAL BOOL enable_flow_controller;

// helper structs for use in the below functions
struct mbSlWordPut wordput_t = {
    .station = "IF4.MODBUSSLAVE_1",
    .enable = 1,
};

struct mbSlWordGet wordget_t = {
    .station = "IF4.MODBUSSLAVE_1",
    .enable = 1,
};

struct mbSlBoolGet boolget_t = {
    .station = "IF4.MODBUSSLAVE_1",
    .enable = 1,
};

struct mbSlBoolPut boolput_t = {
    .station = "IF4.MODBUSSLAVE_1",
    .enable = 1,
};

// old settings 
bool coil_state_old[COIL_BUFFER_SIZE], coil_state_new[COIL_BUFFER_SIZE];

_LOCAL UINT TEST_UINT16;
_LOCAL UINT TEST_ARRAY[128];
_LOCAL UINT ERR;

static void write_single_holding_register(uint8_t offset,uint16_t value)
{
    wordput_t.startAddress = 24576 + offset;
    wordput_t.data = &value;
    wordput_t.nrOfItems = 1;
    mbSlWordPut(&wordput_t);
}

static void write_float_to_holding_register(uint8_t address, float f)
{
    uint32_t f_ieee754 = get_ieee754(f);
    write_single_holding_register(address,get_u32_msb(f_ieee754));
    write_single_holding_register(address+1,get_u32_lsb(f_ieee754));
}

static void write_u32_to_holding_register(uint8_t address, uint32_t val)
{
    write_single_holding_register(address,get_u32_msb(val));
    write_single_holding_register(address+1,get_u32_lsb(val));
}

static void read_single_holding_register(uint8_t offset,uint16_t* value)
{
    wordget_t.startAddress = 24576 + offset;
    wordget_t.data = value;
    wordget_t.nrOfItems = 1;
    mbSlWordGet(&wordget_t);
	ERR = wordget_t.status;
}

static void read_coils(uint8_t address, bool* to_read, uint8_t read_len)
{
    boolget_t.startAddress = COIL_ADDRESS_BASE + address;
    boolget_t.data = to_read;
    boolget_t.nrOfItems = read_len;
    mbSlBoolGet(&boolget_t);
}

static void write_single_coil(uint8_t address,bool val)
{
    boolput_t.startAddress = COIL_ADDRESS_BASE + address;
    boolput_t.data = &val;
    boolput_t.nrOfItems = 1;
    mbSlBoolPut(&boolput_t);
}

static void DUT_data_to_modbus_tcp_fixed(DUT_Slot_t* dut)
{
    FlowMeter_t meter = dut->flow_meter_dut;
    write_float_to_holding_register(REG_DUT_UP,meter.DEBUG_UP);
    write_float_to_holding_register(REG_DUT_DOWN,meter.DEBUG_DOWN);
    write_float_to_holding_register(REG_DUT_AMB,meter.DEBUG_AMB);
    write_float_to_holding_register(REG_DUT_SYS,meter.DEBUG_SYSTICK);
    write_single_holding_register(REG_DUT_BATCH,meter.BATCH);
    write_single_holding_register(REG_DUT_BATCHSN,meter.BATCH_SN);

}

static void load_current_coil_state()
{
    int i;
    for(i = 0; i < COIL_BUFFER_SIZE;i++)
    {
        switch (i)
        {
            case COIL_FLOW_CONTROLLER_ENABLE:
                write_single_coil(COIL_FLOW_CONTROLLER_ENABLE,enable_flow_controller);
                break;
            case COIL_ISOLATION_VALVE_ENABLE:
                write_single_coil(COIL_ISOLATION_VALVE_ENABLE,enable_isolation_valve);
                break;
            case COIL_PUMP_ENABLE:
                write_single_coil(COIL_PUMP_ENABLE,enable_pump);
                break;
            // i know this could be simplified, i'm leaving it bc i was having funky problems before 
            case COIL_DUT1:
                write_single_coil(COIL_DUT1,dut_solenoids[0]);
                break;
            case COIL_DUT2:
                write_single_coil(COIL_DUT2,dut_solenoids[1]);
                break;
            case COIL_DUT3:
                write_single_coil(COIL_DUT3,dut_solenoids[2]);
                break;
            case COIL_DUT4:
                write_single_coil(COIL_DUT4,dut_solenoids[3]);
                break;
            case COIL_DUT5:
                write_single_coil(COIL_DUT5,dut_solenoids[4]);
                break;
            default:
                break;
        }
    }
}

static void process_writeable_values()
{
    read_coils(0x00, coil_state_new, COIL_BUFFER_SIZE);
    int i;
    for (i = 0; i < COIL_BUFFER_SIZE; i++)
    {
        if (coil_state_old[i] != coil_state_new[i])
        {
            switch (i)
            {
                case COIL_FLOW_CONTROLLER_ENABLE:
                    enable_flow_controller = coil_state_new[i];
                    break;
                case COIL_ISOLATION_VALVE_ENABLE:
                    enable_isolation_valve = coil_state_new[i];
                    break;
                case COIL_PUMP_ENABLE:
                    enable_pump = coil_state_new[i];
                    break;
                case COIL_DUT1:
                case COIL_DUT2:
                case COIL_DUT3:
                case COIL_DUT4:
                case COIL_DUT5:
                    dut_solenoids[i - COIL_DUT1] = coil_state_new[i];  // ← fixed
                    break;
                default:
                    break;
            }
            coil_state_old[i] = coil_state_new[i];
        }
    }
    load_current_coil_state();

    //handling writable integers
    read_single_holding_register(REG_FLOW_TARGET,&new_target_flow);
    if (new_target_flow != old_target_flow)
    {
        target_flow = new_target_flow;
    }
    old_target_flow = new_target_flow;
    //ensuring that any changes from the GUI are written into modbus registers
    write_single_holding_register(REG_FLOW_TARGET,target_flow);
}



//loads persistent states from the boolean to sync
// PRIMARILY IMPORTANT WHEN FLASHING NEW CODE WITHOUT WARM RESET
void modbus_tcp_load_initial_states()
{
    int i;
    for(i = 0; i < COIL_BUFFER_SIZE;i++)
    {
        switch (i)
        {
            case COIL_FLOW_CONTROLLER_ENABLE:
                coil_state_old[i] = enable_flow_controller;
                coil_state_new[i] = enable_flow_controller;
                write_single_coil(COIL_FLOW_CONTROLLER_ENABLE,enable_flow_controller);
                break;
            case COIL_ISOLATION_VALVE_ENABLE:
                coil_state_old[i] = enable_isolation_valve;
                coil_state_new[i] = enable_isolation_valve;
                write_single_coil(COIL_ISOLATION_VALVE_ENABLE,enable_isolation_valve);
                break;
            case COIL_PUMP_ENABLE:
                coil_state_old[i] = enable_pump;
                coil_state_new[i] = enable_pump;
                write_single_coil(COIL_PUMP_ENABLE,enable_pump);
                break;
            case COIL_DUT1:
            case COIL_DUT2:
            case COIL_DUT3:
            case COIL_DUT4:
            case COIL_DUT5:
            {
                int j;
                for (j = 0; j < 5; j++)
                {
                    coil_state_old[COIL_DUT1 + j] = dut_solenoids[j];
                    coil_state_new[COIL_DUT1 + j] = dut_solenoids[j];
                    write_single_coil(COIL_DUT1 + j,dut_solenoids[j]);

                }
                break;
            }
            default:
                break;
        }
    }

    new_target_flow = target_flow;
    old_target_flow = target_flow;
    write_single_holding_register(REG_FLOW_TARGET,target_flow);
}

void update_modbus_tcp_fixed(DUT_Slot_t* dut)
{
    DUT_data_to_modbus_tcp_fixed(dut);
    process_writeable_values();
    //scaled value
    write_single_holding_register(REG_FLOW_ACTUAL,(uint16_t)(flow_actual*10));

}


