#include "beeper.h"
#include "settings.h"
#include "config.h"
#include "inc/stm8s_beep.h"
#include "inc/stm8s_flash.h"

void beeper_init()
{
    // Unlock flash
    FLASH->DUKR = FLASH_RASS_KEY2;
    FLASH->DUKR = FLASH_RASS_KEY1;
    while (!(FLASH->IAPSR & FLASH_IAPSR_DUL));

    // Set option bytes
    #define OPT2_BEEP 0x80
    if(!(OPT->OPT2 & OPT2_BEEP)) {
        FLASH->CR2 |= FLASH_CR2_OPT; // unlock option bytes for writing
        FLASH->NCR2 &= ~FLASH_NCR2_NOPT;
        while (!(FLASH->IAPSR & FLASH_IAPSR_DUL));

        OPT->OPT2 |= OPT2_BEEP;
        OPT->NOPT2 &= ~ OPT2_BEEP;

        while (!(FLASH->IAPSR & FLASH_IAPSR_EOP)); // wait for write finish

        FLASH->CR2 &= ~FLASH_CR2_OPT;    // lock back
        FLASH->NCR2 |= FLASH_NCR2_NOPT;

        WWDG->CR = WWDG_CR_WDGA; // Reset system
    }

    // Setup buzzer
    // For buzzer working you must set option bytes: AFR7 - port D4 alternate function = BEEP and LSI_EN - LSI clock enable as CPU clock source
    // You can do this e.g. from graphic STVP
    BEEP->CSR &= ~BEEP_CSR_BEEPEN; // Disable Buzzer
    BEEP->CSR &= ~BEEP_CSR_BEEPDIV; // Clear DIV register
    BEEP->CSR |= BEEP_CALIBRATION_DEFAULT; // Set register with default calibration
    BEEP->CSR &= ~BEEP_CSR_BEEPSEL; // Clear SEL register
    #if F_BEEP_KHZ == 1
        BEEP->CSR |= BEEP_FREQUENCY_1KHZ;
    #elif F_BEEP_KHZ == 2
        BEEP->CSR |= BEEP_FREQUENCY_2KHZ;
    #elif F_BEEP_KHZ == 4
        BEEP->CSR |= BEEP_FREQUENCY_4KHZ;
    #else
        #error "F_BEEP_KHZ must be one of 1, 2 or 4"
    #endif
}

void beeper_on()
{
    if (settings.beeper_enabled && !(BEEP->CSR & BEEP_CSR_BEEPEN)) {
        BEEP->CSR |= BEEP_CSR_BEEPEN;
    }
}

void beeper_off()
{
    if (BEEP->CSR & BEEP_CSR_BEEPEN) {
        BEEP->CSR &= ~BEEP_CSR_BEEPEN;
    }
}

void beeper_toggle()
{
    if (BEEP->CSR & BEEP_CSR_BEEPEN) {
        beeper_off();
    } else {
        beeper_on();
    }
}
