cmd_src/modules/src/p2pDTR/token_ring.o := arm-none-eabi-gcc -Wp,-MD,src/modules/src/p2pDTR/.token_ring.o.d    -I/home/bitcraze/projects/crazyflie-firmware/src/modules/src/p2pDTR -Isrc/modules/src/p2pDTR -D__firmware__ -fno-exceptions -Wall -Wmissing-braces -fno-strict-aliasing -ffunction-sections -fdata-sections -Wdouble-promotion -std=gnu11 -DCRAZYFLIE_FW   -I/home/bitcraze/projects/crazyflie-firmware/vendor/CMSIS/CMSIS/Core/Include   -I/home/bitcraze/projects/crazyflie-firmware/vendor/CMSIS/CMSIS/DSP/Include   -I/home/bitcraze/projects/crazyflie-firmware/vendor/libdw1000/inc   -I/home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include   -I/home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/portable/GCC/ARM_CM4F   -I/home/bitcraze/projects/crazyflie-firmware/src/config   -I/home/bitcraze/projects/crazyflie-firmware/src/platform/interface   -I/home/bitcraze/projects/crazyflie-firmware/src/deck/interface   -I/home/bitcraze/projects/crazyflie-firmware/src/deck/drivers/interface   -I/home/bitcraze/projects/crazyflie-firmware/src/drivers/interface   -I/home/bitcraze/projects/crazyflie-firmware/src/drivers/bosch/interface   -I/home/bitcraze/projects/crazyflie-firmware/src/drivers/esp32/interface   -I/home/bitcraze/projects/crazyflie-firmware/src/hal/interface   -I/home/bitcraze/projects/crazyflie-firmware/src/modules/interface   -I/home/bitcraze/projects/crazyflie-firmware/src/modules/interface/kalman_core   -I/home/bitcraze/projects/crazyflie-firmware/src/modules/interface/lighthouse   -I/home/bitcraze/projects/crazyflie-firmware/src/modules/interface/outlierfilter   -I/home/bitcraze/projects/crazyflie-firmware/src/modules/interface/cpx   -I/home/bitcraze/projects/crazyflie-firmware/src/modules/interface/p2pDTR   -I/home/bitcraze/projects/crazyflie-firmware/src/modules/interface/controller   -I/home/bitcraze/projects/crazyflie-firmware/src/modules/interface/estimator   -I/home/bitcraze/projects/crazyflie-firmware/src/utils/interface   -I/home/bitcraze/projects/crazyflie-firmware/src/utils/interface/kve   -I/home/bitcraze/projects/crazyflie-firmware/src/utils/interface/lighthouse   -I/home/bitcraze/projects/crazyflie-firmware/src/utils/interface/tdoa   -I/home/bitcraze/projects/crazyflie-firmware/src/lib/FatFS   -I/home/bitcraze/projects/crazyflie-firmware/src/lib/CMSIS/STM32F4xx/Include   -I/home/bitcraze/projects/crazyflie-firmware/src/lib/STM32_USB_Device_Library/Core/inc   -I/home/bitcraze/projects/crazyflie-firmware/src/lib/STM32_USB_OTG_Driver/inc   -I/home/bitcraze/projects/crazyflie-firmware/src/lib/STM32F4xx_StdPeriph_Driver/inc   -I/home/bitcraze/projects/crazyflie-firmware/src/lib/vl53l1   -I/home/bitcraze/projects/crazyflie-firmware/src/lib/vl53l1/core/inc   -I/home/bitcraze/projects/LAB_IAA/code/stm32/build/include/generated -fno-delete-null-pointer-checks --param=allow-store-data-races=0 -Wno-unused-but-set-variable -Wno-unused-const-variable -fomit-frame-pointer -fno-var-tracking-assignments -Wno-pointer-sign -fno-strict-overflow -fconserve-stack -Werror=implicit-int -Werror=date-time -DCC_HAVE_ASM_GOTO -mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16 -g3 -fno-math-errno -DARM_MATH_CM4 -D__FPU_PRESENT=1 -mfp16-format=ieee -Wno-array-bounds -Wno-stringop-overread -Wno-stringop-overflow -DSTM32F4XX -DSTM32F40_41xxx -DHSE_VALUE=8000000 -DUSE_STDPERIPH_DRIVER -Os -Werror   -c -o src/modules/src/p2pDTR/token_ring.o /home/bitcraze/projects/crazyflie-firmware/src/modules/src/p2pDTR/token_ring.c

source_src/modules/src/p2pDTR/token_ring.o := /home/bitcraze/projects/crazyflie-firmware/src/modules/src/p2pDTR/token_ring.c

deps_src/modules/src/p2pDTR/token_ring.o := \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/p2pDTR/token_ring.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/FreeRTOS.h \
  /usr/lib/gcc/arm-none-eabi/9.2.1/include/stddef.h \
  /usr/lib/gcc/arm-none-eabi/9.2.1/include/stdint.h \
  /home/bitcraze/projects/crazyflie-firmware/src/config/FreeRTOSConfig.h \
    $(wildcard include/config/h.h) \
    $(wildcard include/config/debug/queue/monitor.h) \
  /home/bitcraze/projects/crazyflie-firmware/src/config/config.h \
    $(wildcard include/config/h/.h) \
    $(wildcard include/config/block/address.h) \
  /home/bitcraze/projects/crazyflie-firmware/src/drivers/interface/nrf24l01.h \
  /usr/lib/gcc/arm-none-eabi/9.2.1/include/stdbool.h \
  /home/bitcraze/projects/crazyflie-firmware/src/drivers/interface/nRF24L01reg.h \
  /home/bitcraze/projects/crazyflie-firmware/src/config/trace.h \
  /home/bitcraze/projects/crazyflie-firmware/src/hal/interface/usec_time.h \
  /home/bitcraze/projects/crazyflie-firmware/src/utils/interface/cfassert.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/projdefs.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/portable.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/deprecated_definitions.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/portable/GCC/ARM_CM4F/portmacro.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/mpu_wrappers.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/timers.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/task.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/list.h \
  /usr/include/newlib/string.h \
  /usr/include/newlib/_ansi.h \
  /usr/include/newlib/newlib.h \
  /usr/include/newlib/_newlib_version.h \
  /usr/include/newlib/sys/config.h \
    $(wildcard include/config/h//.h) \
  /usr/include/newlib/machine/ieeefp.h \
  /usr/include/newlib/sys/features.h \
  /usr/include/newlib/sys/reent.h \
  /usr/include/newlib/_ansi.h \
  /usr/include/newlib/sys/_types.h \
  /usr/include/newlib/machine/_types.h \
  /usr/include/newlib/machine/_default_types.h \
  /usr/include/newlib/sys/lock.h \
  /usr/include/newlib/sys/cdefs.h \
  /usr/include/newlib/sys/_locale.h \
  /usr/include/newlib/strings.h \
  /usr/include/newlib/sys/string.h \
  /home/bitcraze/projects/crazyflie-firmware/src/hal/interface/radiolink.h \
  /home/bitcraze/projects/crazyflie-firmware/src/hal/interface/syslink.h \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/log.h \
    $(wildcard include/config/debug/log/enable.h) \
  /home/bitcraze/projects/crazyflie-firmware/src/utils/interface/configblock.h \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/p2pDTR/DTR_types.h \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/p2pDTR/DTR_handlers.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/task.h \
  /usr/include/newlib/stdlib.h \
  /usr/include/newlib/machine/stdlib.h \
  /usr/include/newlib/alloca.h \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/p2pDTR/token_ring.h \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/p2pDTR/DTR_p2p_interface.h \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/p2pDTR/queueing.h \
  /home/bitcraze/projects/crazyflie-firmware/vendor/FreeRTOS/include/queue.h \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/queuemonitor.h \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/static_mem.h \
  /home/bitcraze/projects/crazyflie-firmware/src/utils/interface/debug.h \
    $(wildcard include/config/debug/print/on/uart1.h) \
  /home/bitcraze/projects/crazyflie-firmware/src/config/config.h \
  /home/bitcraze/projects/crazyflie-firmware/src/modules/interface/console.h \
  /home/bitcraze/projects/crazyflie-firmware/src/utils/interface/eprintf.h \
  /usr/lib/gcc/arm-none-eabi/9.2.1/include/stdarg.h \

src/modules/src/p2pDTR/token_ring.o: $(deps_src/modules/src/p2pDTR/token_ring.o)

$(deps_src/modules/src/p2pDTR/token_ring.o):
