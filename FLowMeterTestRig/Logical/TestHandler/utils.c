#include "utils.h"

uint32_t get_ieee754(float val) {    uint32_t result;memcpy(&result,&val,sizeof(float));return result;}
uint16_t get_u32_msb(uint32_t val) {return (val >> 16) & 0xFFFF;}
uint16_t get_u32_lsb(uint32_t val) {return val & 0xFFFF;}
