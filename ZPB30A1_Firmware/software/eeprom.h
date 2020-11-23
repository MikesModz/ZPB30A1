#ifndef _EEPROM_H_
#define _EEPROM_H_
#include <stdint.h>
uint8_t eeprom_read8(uint16_t address);
uint16_t eeprom_read16(uint16_t address);
void eeprom_write8(uint16_t address, uint8_t data);
void eeprom_write16(uint16_t address, uint16_t data);
#endif
