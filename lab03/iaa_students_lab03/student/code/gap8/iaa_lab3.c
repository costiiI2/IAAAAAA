#include "pmsis.h"
#include "cpx.h"
#include "wifi.h"
#include "bsp/bsp.h"
#include "bsp/camera/himax.h"
#include "bsp/buffer.h"

#define IMG_ORIENTATION 0x0101
#define CAM_WIDTH 324
#define CAM_HEIGHT 244
#define PIC_WIDTH 200
#define PIC_HEIGHT 200

void sendToSTM32(void);
void rx_wifi_task(void *parameters);
void send_image_via_wifi(unsigned char *image, uint16_t width, uint16_t height);
int open_pi_camera_himax(struct pi_device *device);
static void capture_done_cb(void *arg);
void camera_task(void *parameters);

static struct pi_device camera;
unsigned char *imgBuff;
static pi_buffer_t buffer;
static SemaphoreHandle_t capture_sem = NULL;
static int wifiClientConnected = 0;
static CPXPacket_t rxp;
static CPXPacket_t txp;
static pi_task_t task1;

typedef struct
{
    uint8_t magic;
    uint16_t width;
    uint16_t height;
    uint8_t depth;
    uint8_t type;
    uint32_t size;
} __attribute__((packed)) img_header_t;

void start(void)
{

    cpxInit();
    cpxEnableFunction(CPX_F_WIFI_CTRL);

    BaseType_t xTask;

    vTaskDelay(2000);
    cpxPrintToConsole(LOG_TO_CRTP, "\n\n*** IAA LAB03 ***\n\n");

    /* Create wifi listener task */
    xTask = xTaskCreate(rx_wifi_task, "rx_wifi_task", configMINIMAL_STACK_SIZE * 2,
                        NULL, tskIDLE_PRIORITY + 1, NULL);

    /* Open and init camera buffer */
    if (open_pi_camera_himax(&camera))
    {
        cpxPrintToConsole(LOG_TO_CRTP, "Failed to open camera\n");
        return;
    }

    imgBuff = (unsigned char *)pmsis_l2_malloc(CAM_WIDTH * CAM_HEIGHT);
    if (imgBuff == NULL)
    {
        cpxPrintToConsole(LOG_TO_CRTP, "Failed to allocate image buffer\n");
    }
    pi_buffer_init(&buffer, PI_BUFFER_TYPE_L2, imgBuff);
    pi_buffer_set_format(&buffer, CAM_WIDTH, CAM_HEIGHT, 1, PI_BUFFER_FORMAT_GRAY);

    /* Create Camera task */
    xTask = xTaskCreate(camera_task, "camera_task", configMINIMAL_STACK_SIZE * 4,
                        NULL, tskIDLE_PRIORITY + 1, NULL);

    capture_sem = xSemaphoreCreateBinary();

    bool fcFreqSent = false;
    while (1)
    {
        if (!fcFreqSent)
        {
            sendToSTM32();
            fcFreqSent = true;
        }

        pi_yield();
        vTaskDelay(100);
    }
}

/**
 * @brief transfer UART to stm32
 * - Retrieves FC frequencies
 * - Sends a buffer from gap8 to STM32
 * - Need a program on stm32 to read uart
 */
void sendToSTM32(void)
{
    cpxEnableFunction(CPX_F_APP);

    // Récupère et place la fréquence de la FC dans le paquet
    uint32_t fcFreq = pi_freq_get(PI_FREQ_DOMAIN_FC);
    memcpy(txp.data, &fcFreq, sizeof(uint32_t));
    txp.dataLength = sizeof(uint32_t);

    // Initialise la route et envoie le paquet
    cpxInitRoute(CPX_T_GAP8, CPX_T_STM32, CPX_F_APP, &txp.route);
    cpxSendPacketBlocking(&txp);
    cpxPrintToConsole(LOG_TO_CRTP, "Sent FC frequency: %u\n", fcFreq);
}

/**
 * @brief Task wifi management
 * be able to:
 * - know if a PC is connected to the drone
 */
void rx_wifi_task(void *parameters)
{
    cpxEnableFunction(CPX_F_WIFI_CTRL);

    while (1)
    {
        cpxReceivePacketBlocking(CPX_F_WIFI_CTRL, &rxp);

        WiFiCTRLPacket_t *wifiCtrl = (WiFiCTRLPacket_t *)rxp.data;

        if (wifiCtrl->cmd == WIFI_CTRL_STATUS_CLIENT_CONNECTED)
        {
            cpxPrintToConsole(LOG_TO_CRTP, "Wifi client connection status: %u\n", wifiCtrl->data[0]);
            wifiClientConnected = wifiCtrl->data[0];
        }
    }
}

/**
 * @brief transfer WIFI gap8 to PC
 * Send a gap8 buffer to the PC
 * Need python code to receives data on PC
 */
void send_image_via_wifi(unsigned char *image, uint16_t width, uint16_t height)
{
    uint32_t imgSize = width * height;

    img_header_t *imgHeader = (img_header_t *)txp.data;
    imgHeader->magic = 0xBC;
    imgHeader->width = width;
    imgHeader->height = height;
    imgHeader->depth = 1;
    imgHeader->type = 1;
    imgHeader->size = imgSize;
    txp.dataLength = sizeof(img_header_t);
    cpxInitRoute(CPX_T_GAP8, CPX_T_WIFI_HOST, CPX_F_APP, &txp.route);
    cpxSendPacketBlocking(&txp);

    sendBufferViaCPXBlocking(&txp, (uint8_t *)&image, imgSize);
}

/**
 * @brief Callback called when a capture is completed by the camera
 * - must release the acquisition task in order to take a new capture
 */
static void capture_done_cb(void *arg)
{
    // cpxPrintToConsole(LOG_TO_CRTP, "Stop image capture\n");
    // Arrêter la capture
    pi_camera_control(&camera, PI_CAMERA_CMD_STOP, 0);

    // Libérer la sémaphore pour indiquer que la capture est terminée
    xSemaphoreGive(capture_sem);
}

/**
 * @brief Task enabling the acquisition/sending of an image
 * - Set the callback called at the end of a capture
 * - Starts a new capture
 * - Calls the function for sending the image by wifi
 */
void camera_task(void *parameters)
{

    while (1)
    {
        // Si aucun utilisateur est connecté ne fait pas de capture d'image
        if (wifiClientConnected == 0)
        {
            vTaskDelay(50);
            continue;
        }

        cpxPrintToConsole(LOG_TO_CRTP, "Client connected...");

        // Set le callback appelé lorsque la capture sera terminée + démarre la capture
        uint32_t resolution = CAM_WIDTH * CAM_HEIGHT;
        pi_camera_capture_async(&camera, imgBuff, resolution, pi_task_callback(&task1, capture_done_cb, NULL));
        pi_camera_control(&camera, PI_CAMERA_CMD_START, 0);

        cpxPrintToConsole(LOG_TO_CRTP, " starting capture.\n");

        xSemaphoreTake(capture_sem, portMAX_DELAY);

        unsigned char cropped_image[PIC_HEIGHT * PIC_WIDTH]; // TODO: Change by cropped image

        // cropping to PIC_heigt and witdh
        // get only bottom 200 pixec and crop 62 from left and from right

        for (int i = 0; i < PIC_HEIGHT; i++)
        {
            for (int j = 0; j < PIC_WIDTH; j++)
            {
                cropped_image[i * PIC_WIDTH + j] = imgBuff[(i + CAM_HEIGHT-PIC_HEIGHT) * CAM_WIDTH + j + (CAM_WIDTH-PIC_WIDTH)/2];
            }
        }

        if (wifiClientConnected == 1)
        {
            send_image_via_wifi(cropped_image, PIC_WIDTH, PIC_HEIGHT);
        }
        else
        {
            cpxPrintToConsole(LOG_TO_CRTP, "Client disconnected while capturing image. Image has not been sent.\n");
        }
    }
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
int main(void)
{
    pi_bsp_init();

    return pmsis_kickoff((void *)start);
}
