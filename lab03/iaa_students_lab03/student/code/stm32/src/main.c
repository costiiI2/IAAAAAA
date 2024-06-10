#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#include "app.h"

#include "FreeRTOS.h"
#include "task.h"

#define DEBUG_MODULE "IAALAB03"
#include "debug.h"
#include "commander.h"
#include "pm.h"
#include "log.h"

#include "cpx_internal_router.h"

void receive_app_msg(const CPXPacket_t *cpxRx)
{

  DEBUG_PRINT("CL FREQ = %d\n", *(int *)(cpxRx->data));
}

static void setVelocitySetpoint(setpoint_t *setpoint, float vx,
                                float vy, float z, float yawrate)
{
  setpoint->mode.z = modeAbs;
  setpoint->position.z = z;
  setpoint->mode.yaw = modeVelocity;
  setpoint->attitudeRate.yaw = yawrate;
  setpoint->mode.x = modeVelocity;
  setpoint->mode.y = modeVelocity;
  setpoint->velocity.x = vx;
  setpoint->velocity.y = vy;
  setpoint->velocity_body = true;
}
void appMain()
{
  setpoint_t s;
  setVelocitySetpoint(&s, 0, 0, 0.5, 0);
  // wait for the initialization to complete
  vTaskDelay(M2T(5000));
  int i = 0;
  while (1)
  {
    if(i++ < 10000)
    {
      commanderSetSetpoint(&s, 3);
      vTaskDelay(M2T(10));
      
    }
  }
}
