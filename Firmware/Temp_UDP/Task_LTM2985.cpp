#include "LTM2985.h"
#include "GlobalHandles.h"
#include "Custom_Structures.h"
#include "Command_Define.h"

/**
 * @brief Interrupt Service Routine for LTM2985 INT_PIN1
 *
 * This handler is triggered when the LTM2985 asserts its interrupt pin.
 * It notifies the LTM2985 task that a measurement is ready.
 */
void IRS_Pin1_handle();

/**
 * @brief Task for handling LTM2985 temperature sensor readings
 *
 * This task is responsible for:
 * - Configuring the LTM2985 sensor and its SPI interface
 * - Managing the measurement cycle across all channels
 * - Handling interrupt-based measurement ready notifications
 * - Processing temperature readings and fault status
 * - Sending results to the Command task via queue
 * - Providing debug output via serial
 *
 * @param pvParameters Task parameters (unused)
 */
void Task_LTM2985(void *pvParameters)
{
    // Suppress unused parameter warning
    (void)pvParameters;

    // Add initialization timeout to prevent hanging
    unsigned long initStartTime = millis();
    const unsigned long initTimeout = 10000; // 10 second timeout for initialization

    RTD_result_type RTD_result; // Stores results from temperature readings
    RTD_result_type RTD1_result;
    RTD_result_type RTD2_result;
    RTD_result_type RTD3_result;
    RTD_result_type RTD4_result;
    RTD_result_type RTD5_result;
    RTD_result_type RTD6_result;
    RTD_result_type RTD7_result;
    RTD_result_type RTD8_result;

    RTD1_result.channel = RTD1;
    RTD2_result.channel = RTD2;
    RTD3_result.channel = RTD3;
    RTD4_result.channel = RTD4;
    RTD5_result.channel = RTD5;
    RTD6_result.channel = RTD6;
    RTD7_result.channel = RTD7;
    RTD8_result.channel = RTD8;

    constexpr uint8_t channel_index[4] = {4, 6, 8, 10}; // Channel addresses
    uint8_t channel_nb_iterator;                        // Tracks current channel being measured
    channel_nb_iterator = 0;
    unsigned long startTime = millis(); // Timer for measurement timeout
    const unsigned long timeout = 2000; // 2 second timeout for measurements (ms)

    set_SPI_LTM2985();             // Configure SPI interface for LTM2985
    configure_global_parameters(); // Configure global sensor parameters

    delay(10); // Allow other tasks to run

    attachInterrupt(digitalPinToInterrupt(INT_PIN1), IRS_Pin1_handle, RISING);

    // Start measurement cycle

    measure_request(channel_index[channel_nb_iterator]); // Initiate first measurement

    // Main task loop
    for (;;) // A Task shall never return or exit.
    {
        // Check for measurement ready notification (blocking with timeout)
        uint32_t IRS_Pin1_flag = ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(100));

        if (IRS_Pin1_flag || (millis() - startTime > timeout))
        {
            IRS_Pin1_flag = false; // Reset notification flag
            startTime = millis();  // Reset timeout timer

            // Read temperature from current channel
            RTD_result = read_temp(channel_index[channel_nb_iterator]);

            // Store results in appropriate channel variables
            switch (RTD_result.channel)
            {
            case channel_index[0]: // Channel 1 results
                RTD1_result.value = RTD_result.value;
                RTD1_result.fault = RTD_result.fault;
                xQueueSend(q_LTM2985_to_UDP, &RTD1_result, 0);
                break;

            case channel_index[1]: // Channel 2 results
                RTD2_result.value = RTD_result.value;
                RTD2_result.fault = RTD_result.fault;
                xQueueSend(q_LTM2985_to_UDP, &RTD2_result, 0);
                break;

            case channel_index[2]: // Channel 3 results
                RTD3_result.value = RTD_result.value;
                RTD3_result.fault = RTD_result.fault;
                xQueueSend(q_LTM2985_to_UDP, &RTD3_result, 0);
                break;

            case channel_index[3]: // Channel 4 results
                RTD4_result.value = RTD_result.value;
                RTD4_result.fault = RTD_result.fault;
                xQueueSend(q_LTM2985_to_UDP, &RTD4_result, 0);
                break;
            }

            // Send results to Command task via queue

            // Move to next channel
            channel_nb_iterator++;

            // If we've cycled through all channels, print debug output
            if (channel_nb_iterator >= 0)
            {
                channel_nb_iterator = 0; // Reset channel counter
            }

            // Initiate next measurement
            measure_request(channel_index[channel_nb_iterator]);
        }

        delay(10);
    }
}

/**
 * @brief Interrupt Service Routine for LTM2985 INT_PIN1
 *
 * This handler is called when the LTM2985 asserts its interrupt pin
 * to indicate a measurement is ready. It notifies the LTM2985 task
 * to process the measurement.
 *
 * Note: Uses FreeRTOS ISR-safe notification mechanism
 */
void IRS_Pin1_handle()
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    // Notify the LTM2985 task that a measurement is ready
    vTaskNotifyGiveFromISR(Task_LTM2985_Handle, &xHigherPriorityTaskWoken);

    // Perform context switch if needed
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}