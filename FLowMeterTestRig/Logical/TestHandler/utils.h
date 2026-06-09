#pragma once

#include <bur/plctypes.h>
#include <brsystem.h>
#include <stdint.h>
#include <stdbool.h>


uint32_t get_ieee754(float val);
uint16_t get_u32_msb(uint32_t val);
uint16_t get_u32_lsb(uint32_t val);
