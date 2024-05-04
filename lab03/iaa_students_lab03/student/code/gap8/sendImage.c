#include "pmsis.h"

#include "bsp/bsp.h"
#include "bsp/camera/himax.h"
#include "bsp/buffer.h"
#include "gaplib/jpeg_encoder.h"
#include "stdio.h"

#include "cpx.h"
#include "wifi.h"

#define IMG_ORIENTATION 0x0101
#define CAM_WIDTH 324
#define CAM_HEIGHT 244

static pi_task_t task1;
static unsigned char *imgBuff;
static struct pi_device camera;
static pi_buffer_t buffer;

static EventGroupHandle_t evGroup;
#define CAPTURE_DONE_BIT (1 << 0)

// Performance menasuring variables
static uint32_t start = 0;
static uint32_t captureTime = 0;
static uint32_t transferTime = 0;
static uint32_t encodingTime = 0;
// #define OUTPUT_PROFILING_DATA

static int open_pi_camera_himax(struct pi_device *device)
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

static int wifiClientConnected = 0;

static CPXPacket_t rxp;
void rx_task(void *parameters)
{
  while (1)
  {
    cpxReceivePacketBlocking(CPX_F_WIFI_CTRL, &rxp);

    WiFiCTRLPacket_t * wifiCtrl = (WiFiCTRLPacket_t*) rxp.data;

    if (wifiCtrl->cmd == WIFI_CTRL_STATUS_CLIENT_CONNECTED) {
        cpxPrintToConsole(LOG_TO_CRTP, "Wifi client connection status: %u\n", wifiCtrl->data[0]);
        wifiClientConnected = wifiCtrl->data[0];
    }
  }
}

typedef struct
{
  uint16_t width;
  uint16_t height;
  uint32_t size;
} __attribute__((packed)) img_header_t;

pi_buffer_t header;
uint32_t headerSize;
pi_buffer_t footer;
uint32_t footerSize;
pi_buffer_t image_data;
uint32_t imageSize;

static CPXPacket_t txp;

void createImageHeaderPacket(CPXPacket_t * packet, uint32_t imgSize) {
    img_header_t *imgHeader = (img_header_t *) packet->data;
    imgHeader->width = CAM_WIDTH;
    imgHeader->height = CAM_HEIGHT;
    imgHeader->size = imgSize;
    packet->dataLength = sizeof(img_header_t);
}

void sendBufferViaCPX(CPXPacket_t * packet, uint8_t * buffer, uint32_t bufferSize) {
    uint32_t offset = 0;
    uint32_t size = 0;
    do {
        size = sizeof(packet->data);
        if (offset + size > bufferSize)
        {
            size = bufferSize - offset;
        }
        memcpy(packet->data, &buffer[offset], sizeof(packet->data));
        packet->dataLength = size;
        cpxSendPacketBlocking(packet);
        offset += size;
    } while (size == sizeof(packet->data));
}

void camera_task(void *parameters)
{
    vTaskDelay(2000);

    cpxPrintToConsole(LOG_TO_CRTP, "Starting camera task...\n");
    uint32_t resolution = CAM_WIDTH * CAM_HEIGHT;
    uint32_t captureSize = resolution * sizeof(unsigned char);
    imgBuff = (unsigned char *)pmsis_l2_malloc(captureSize);
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

    header.size = 1024;
    header.data = pmsis_l2_malloc(1024);

    footer.size = 10;
    footer.data = pmsis_l2_malloc(10);

    if (header.data == 0 || footer.data == 0 || jpeg_data.data == 0) {
        cpxPrintToConsole(LOG_TO_CRTP, "Could not allocate memory for JPEG image\n");
        return;
    }

    pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);

    // We're reusing the same packet, so initialize the route once
    cpxInitRoute(CPX_T_GAP8, CPX_T_WIFI_HOST, CPX_F_APP, &txp.route);

    uint32_t imgSize = 0;

    while (1)
    {
        if (wifiClientConnected == 1)
        {
            pi_camera_capture_async(&camera, imgBuff, resolution, pi_task_callback(&task1, capture_done_cb, NULL));
            pi_camera_control(&camera, PI_CAMERA_CMD_START, 0);
            pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);

            imgSize = headerSize + imgSize + footerSize;

            // First send information about the image
            createImageHeaderPacket(&txp, imgSize);
            cpxSendPacketBlocking(&txp);

            // First send header
            memcpy(txp.data, header.data, headerSize);
            txp.dataLength = headerSize;
            cpxSendPacketBlocking(&txp);

            // Send image data
            sendBufferViaCPX(&txp, (uint8_t*) jpeg_data.data, jpegSize);

            // Send footer
            memcpy(txp.data, footer.data, footerSize);
            txp.dataLength = footerSize;
            cpxSendPacketBlocking(&txp);
        }
        else
        {
            vTaskDelay(10);
        }
    }
}