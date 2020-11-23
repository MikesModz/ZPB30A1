#include "eeprom.h"
#include "inc/stm8s_flash.h"
#define _MEM_(mem_addr) (*(volatile uint8_t *)(mem_addr))

uint8_t eeprom_read8(uint16_t address) {
    return _MEM_(address + FLASH_DATA_START_PHYSICAL_ADDRESS);
}

uint16_t eeprom_read16(uint16_t address) {
    return ((uint16_t)eeprom_read8(address) << 8) | eeprom_read8(address + 1);
}

void eeprom_write8(uint16_t address, uint8_t data) {
    if (eeprom_read8(address) == data) return; //Avoid unnecessary writes
    _MEM_(address + FLASH_DATA_START_PHYSICAL_ADDRESS) = data;
}

void eeprom_write16(uint16_t address, uint16_t data) {
    eeprom_write8(address, data >> 8);
    eeprom_write8(address + 1, data & 0xFF);
}
