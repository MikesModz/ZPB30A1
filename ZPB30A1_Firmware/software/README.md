# Module interface
* NAME_init(): Initialize hardware and variables. Set module to a safe state
* NAME_timer(): Called when the systick timer counts from the main loop.
* NAME_handler(): Called when the main loop is idle. Can be used to move longer running tasks out of interrupts.

# Timers
* TIM1: CCR1: I-set
* TIM2: Systick
* TIM3: CCR2: Fan
* TIM4:
