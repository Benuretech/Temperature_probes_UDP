#include "LTM2985.h"
#include "GlobalHandles.h"
#include "Custom_Structures.h"

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

    // Variables to store temperature readings and fault status for each channel
    int32_t val1 = 0;   // Channel 1 temperature value
    uint8_t fault1 = 0; // Channel 1 fault status
    int32_t val2 = 0;   // Channel 2 temperature value
    uint8_t fault2 = 0; // Channel 2 fault status
    int32_t val3 = 0;   // Channel 3 temperature value
    uint8_t fault3 = 0; // Channel 3 fault status
    int32_t val4 = 0;   // Channel 4 temperature value
    uint8_t fault4 = 0; // Channel 4 fault status

    uint8_t channel_nb_iterator;        // Tracks current channel being measured
    RTD_result task_results;            // Stores results from temperature readings
    unsigned long startTime = millis(); // Timer for measurement timeout
    const unsigned long timeout = 2000; // 2 second timeout for measurements (ms)

    // Initialize LTM2985 hardware interface and configuration
    set_SPI1_LTM2985();                       // Configure SPI interface for LTM2985
    uint8_t channel_index[4] = {4, 6, 8, 10}; // Channel addresses
    configure_channels();                     // Set up measurement channels
    configure_global_parameters();            // Configure global sensor parameters

    // Set up interrupt handler for measurement ready signal
    attachInterrupt(digitalPinToInterrupt(INT_PIN1), IRS_Pin1_handle, RISING);

    // Start measurement cycle
    channel_nb_iterator = 0;
    measure_request(channel_index[channel_nb_iterator]); // Initiate first measurement

    // Main task loop
    for (;;) // A Task shall never return or exit.
    {
        // Check for measurement ready notification (either interrupt or timeout)
        uint32_t IRS_Pin1_flag = ulTaskNotifyTake(pdTRUE, 0);

        if (IRS_Pin1_flag || (millis() - startTime > timeout))
        {
            IRS_Pin1_flag = false; // Reset notification flag
            startTime = millis();  // Reset timeout timer

            // Read temperature from current channel
            task_results = read_temp(channel_index[channel_nb_iterator]);

            // Store results in appropriate channel variables
            switch (task_results.channel)
            {
            case 4: // Channel 1 results
                val1 = task_results.value;
                fault1 = task_results.fault;
                break;

            case 6: // Channel 2 results
                val2 = task_results.value;
                fault2 = task_results.fault;
                break;

            case 8: // Channel 3 results
                val3 = task_results.value;
                fault3 = task_results.fault;
                break;

            case 10: // Channel 4 results
                val4 = task_results.value;
                fault4 = task_results.fault;
                break;
            }

            // Send results to Command task via queue
            xQueueSend(q_LTM2985_to_UDP, &task_results, 0);

            // Move to next channel
            channel_nb_iterator++;

            // If we've cycled through all channels, print debug output
            if (channel_nb_iterator >= 4)
            {
                // Serial debug output showing all channel readings and faults
                Serial.print("TL2985 :");
                Serial.print("ch1: ");
                Serial.print(val1);
                Serial.print(" err: ");
                Serial.print(fault1);
                Serial.print(" ch2: ");
                Serial.print(val2);
                Serial.print(" err: ");
                Serial.print(fault2);
                Serial.print(" ch3: ");
                Serial.print(val3);
                Serial.print(" err: ");
                Serial.print(fault3);
                Serial.print(" ch4: ");
                Serial.print(val4);
                Serial.print(" err: ");
                Serial.print(fault4);
                Serial.println();

                channel_nb_iterator = 0; // Reset channel counter
            }

            // Initiate next measurement
            measure_request(channel_index[channel_nb_iterator]);
        }
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