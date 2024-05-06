#include "pmsis.h"
#include "cpx.h"
#include "wifi.h"
#include "bsp/bsp.h"
#include "bsp/camera/himax.h"
#include "bsp/buffer.h"

#define IMG_ORIENTATION 0x0101
#define CAM_WIDTH 324
#define CAM_HEIGHT 244
#define CAM_IMG 0



void sendToSTM32(void);
void rx_wifi_task(void *parameters);
void send_image_via_wifi(unsigned char *image, uint16_t width, uint16_t height);
int open_pi_camera_himax(struct pi_device *device);
static void capture_done_cb(void *arg);
void camera_task(void *parameters);

static int wifiClientConnected = 0;
static struct pi_device camera;
unsigned char *imgBuff;
static pi_buffer_t buffer;
static SemaphoreHandle_t capture_sem = NULL;


void start(void) {

    cpxInit();
    cpxEnableFunction(CPX_F_WIFI_CTRL);
    
    BaseType_t xTask;

    vTaskDelay(2000);
    cpxPrintToConsole(LOG_TO_CRTP, "\n\n*** IAA LAB03 ***\n\n");
    

    /* Create wifi listener task */
    xTask = xTaskCreate(rx_wifi_task, "rx_wifi_task", configMINIMAL_STACK_SIZE * 2,
                      NULL, tskIDLE_PRIORITY + 1, NULL);
    

    /* Open and init camera buffer */
    if (open_pi_camera_himax(&camera)) {
        cpxPrintToConsole(LOG_TO_CRTP, "Failed to open camera\n");
        return;
    }

    pi_buffer_init(&buffer, PI_BUFFER_TYPE_L2, imgBuff);
    pi_buffer_set_format(&buffer, CAM_WIDTH, CAM_HEIGHT, 1, PI_BUFFER_FORMAT_GRAY);

    imgBuff = (unsigned char *)pmsis_l2_malloc(CAM_WIDTH*CAM_HEIGHT);
    

    /* Create Camera task */
    xTask = xTaskCreate(camera_task, "camera_task", configMINIMAL_STACK_SIZE * 4,
                      NULL, tskIDLE_PRIORITY + 1, NULL);

    while(1) {
        sendToSTM32();
        pi_yield();
        vTaskDelay(100);
    }
}

static CPXPacket_t packet;
/**
 * @brief transfer UART to stm32
 * - Retrieves FC frequencies
 * - Sends a buffer from gap8 to STM32
 * - Need a program on stm32 to read uart
 */
void sendToSTM32(void) {

    cpxPrintToConsole(LOG_TO_CRTP, "Entering sendToSTM32\n");

    // Récuperation de la Fréquence
    uint32_t fcFreq = pi_freq_get(PI_FREQ_DOMAIN_FC);

    // Assignation de la route
    cpxInitRoute(CPX_T_GAP8, CPX_T_STM32, CPX_F_APP, &packet.route);

    // Preparation du payload
    for(unsigned  i = 0 ; i < sizeof(fcFreq); i++){
        packet.data[i] = *((uint8_t *)&fcFreq + i);
    }
    packet.dataLength = sizeof(fcFreq);

    // Envoie du packet
    cpxSendPacketBlocking(&packet);
    cpxPrintToConsole(LOG_TO_CRTP, "Sending FC frequency to STM32 : %u\n", fcFreq);
}

static int wifiConnected = 0;

static CPXPacket_t rxp;
/**
 * @brief Task wifi management
 * be able to:
 * - know if a PC is connected to the drone
 */
void rx_wifi_task(void *parameters) {

  while (1)
  {
    cpxReceivePacketBlocking(CPX_F_WIFI_CTRL, &rxp);

    WiFiCTRLPacket_t * wifiCtrl = (WiFiCTRLPacket_t*) rxp.data;

    switch (wifiCtrl->cmd)
    {
      case WIFI_CTRL_STATUS_WIFI_CONNECTED:
        cpxPrintToConsole(LOG_TO_CRTP, "Wifi connected (%u.%u.%u.%u)\n",
                          wifiCtrl->data[0], wifiCtrl->data[1],
                          wifiCtrl->data[2], wifiCtrl->data[3]);
        wifiConnected = 1;
        break;
      case WIFI_CTRL_STATUS_CLIENT_CONNECTED:
        cpxPrintToConsole(LOG_TO_CRTP, "Wifi client connection status: %u\n", wifiCtrl->data[0]);
        wifiClientConnected = wifiCtrl->data[0];
        break;
      default:
        break;
    }
  }

}

typedef struct
{
  uint8_t magic;
  uint16_t width;
  uint16_t height;
  uint8_t depth;
  uint8_t type;
  uint32_t size;
} __attribute__((packed)) img_header_t;

/**
 * @brief transfer WIFI gap8 to PC
 * Send a gap8 buffer to the PC
 * Need python code to receives data on PC
 */
void send_image_via_wifi(unsigned char *image, uint16_t width, uint16_t height) {
    static CPXPacket_t img_packet;

    if(wifiClientConnected != 0){

      // init route
      cpxInitRoute(CPX_T_GAP8, CPX_T_WIFI_HOST, CPX_F_APP, &img_packet.route);

      // filling header
      img_header_t *imgHeader = (img_header_t *) img_packet.data;
      size_t size = width * height;

      imgHeader->magic = 0xBC;
      imgHeader->width = width;
      imgHeader->height = height;
      imgHeader->depth = 1;
      imgHeader->type = CAM_IMG;
      imgHeader->size = size;
      img_packet.dataLength = sizeof(img_header_t);

      // sending header
      cpxSendPacketBlocking(&img_packet);

      // Sending the image data 
      sendBufferViaCPXBlocking(&img_packet,image,size);

    }

}


static SemaphoreHandle_t capture_sem;

/**
 * @brief Callback called when a capture is completed by the camera
 * - must release the acquisition task in order to take a new capture
 */
static void capture_done_cb(void *arg) {
    /* DONE */
  pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);
  xSemaphoreGive(capture_sem);
}

/**
 * @brief Task enabling the acquisition/sending of an image
 * - Set the callback called at the end of a capture 
 * - Starts a new capture
 * - Calls the function for sending the image by wifi 
 */
void camera_task(void *parameters) {
    /* DONE */
  vTaskDelay(2000);
  
  static pi_buffer_t buffer;
  
  imgBuff = (unsigned char *)pmsis_l2_malloc(CAM_WIDTH*CAM_HEIGHT);

  if (imgBuff == NULL)
  {
    cpxPrintToConsole(LOG_TO_CRTP, "Failed to allocate Memory for Image \n");
    return;
  }

  if (open_pi_camera_himax(&camera))
  {
    cpxPrintToConsole(LOG_TO_CRTP, "Failed to open camera\n");
    return;
  }

  pi_buffer_init(&buffer, PI_BUFFER_TYPE_L2, imgBuff);
  pi_buffer_set_format(&buffer, CAM_WIDTH, CAM_HEIGHT, 1, PI_BUFFER_FORMAT_GRAY);

  capture_sem = xSemaphoreCreateBinary();

  pi_task_t task1;

  pi_camera_capture_async(&camera, imgBuff, CAM_HEIGHT*CAM_WIDTH, pi_task_callback(&task1, capture_done_cb, NULL));
  pi_camera_control(&camera, PI_CAMERA_CMD_START, 0);

  xSemaphoreTake(capture_sem, portMAX_DELAY);

  for (int i = 0; i < 200; i++) {
    for (int j = 0; j < 200; j++) {
      imgBuff[i*200 + j] = imgBuff[(i+CAM_HEIGHT-200)*CAM_WIDTH + (j+(CAM_WIDTH-200)/2)];
    }
  }

  send_image_via_wifi(imgBuff, 200, 200);

  pmsis_l2_malloc_free(imgBuff, CAM_WIDTH*CAM_HEIGHT);
}

int open_pi_camera_himax(struct pi_device *device)
{
  struct pi_himax_conf cam_conf;

  pi_himax_conf_init(&cam_conf);

  cam_conf.format = PI_CAMERA_QVGA;

  pi_open_from_conf(device, &cam_conf);
  if (pi_camera_open(device))
    return -1;

  // rotate image
  pi_camera_control(device, PI_CAMERA_CMD_START, 0);
  uint8_t set_value = 3;
  uint8_t reg_value;
  pi_camera_reg_set(device, IMG_ORIENTATION, &set_value);
  pi_time_wait_us(1000000);
  pi_camera_reg_get(device, IMG_ORIENTATION, &reg_value);
  if (set_value != reg_value)
  {
    cpxPrintToConsole(LOG_TO_CRTP, "Failed to rotate camera image\n");
    return -1;
  }
  pi_camera_control(device, PI_CAMERA_CMD_STOP, 0);
  pi_camera_control(device, PI_CAMERA_CMD_AEG_INIT, 0);

  return 0;
}


/* Program Entry. */
int main(void) {
    pi_bsp_init();
    
    return pmsis_kickoff((void *) start);
}
