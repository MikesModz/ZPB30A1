#ifndef _SETTINGS_H_
#define _SETTINGS_H_
#include <stdbool.h>
#include <stdint.h>

typedef enum {
    MODE_CC,
    MODE_CW,
    MODE_CR,
    MODE_CV,
    NUM_MODES
} sink_mode_t;

typedef enum {
    MAX_P_OFF = 0,
    MAX_P_LIM = 1,
} max_power_action_t;

typedef struct {
    sink_mode_t mode;
    uint16_t setpoints[NUM_MODES]; // CC (mA)/CW(mW)/CR/CV(mV)
    bool beeper_enabled;
    bool cutoff_enabled;
    uint16_t cutoff_voltage; //mV
    uint16_t current_limit; //mA
    uint8_t max_power_action;
} settings_t;

extern settings_t settings;

void settings_init();
void settings_update();
#endif
