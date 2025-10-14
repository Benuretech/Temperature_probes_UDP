/**
 * @file main.cpp
 * @brief Main entry point for the embedded system using FreeRTOS and Ethernet UDP.
 *
 * This file initializes hardware pins, sets up communication queues and semaphores,
 * and starts FreeRTOS tasks for handling LTM2985 sensor, command processing,
 * and PWM control. It also runs an Ethernet UDP handler in the main loop.
 */

#include <Arduino.h>
#include <stdint.h>
#include <stdbool.h>
#include "Wire.h"

#include "stdio.h"
#include "math.h"
#include "LTM2985.h"
#include <FreeRTOS.h>
#include <queue.h>
#include <semphr.h>
#include "GlobalHandles.h"
#include "Custom_Structures.h"
#include "Task_UDP.h"

// ---------------------- Global Variables ----------------------

// Temporary hex character buffer
char hexCar[20];

// Ethernet UDP object

// Task function declarations
void Task_LTM2985(void *pvParameters);
void Task_read_ADC(void *pvParameters);
void Task_UDP(void *pvParameters);
// ---------------------- Main Setup Function ----------------------

/**
 * @brief Arduino setup function.
 *
 * Initializes serial communication, I/O pins, semaphores, queues, and FreeRTOS tasks.
 */
void setup()
{
  Serial.begin(921600); // Start serial communication
  delay(5000);          // Wait for serial port to initialize
  Serial.println("Starting...");

  pinMode(8, OUTPUT);
  pinMode(22, OUTPUT);
  pinMode(INT_PIN1, INPUT_PULLUP);

  // Create binary semaphores
  UDP_Connection_Init_Semaphore = xSemaphoreCreateBinary();

  // Clear any existing tokens in semaphores
  xSemaphoreTake(UDP_Connection_Init_Semaphore, 0);

  // ---------------------- Create Queues ----------------------

  // Sensor result queue
  q_LTM2985_to_UDP = xQueueCreate(20, sizeof(struct RTD_result));
  q_ADC_to_UDP = xQueueCreate(20, sizeof(int));

  // xTaskCreate(Task_LTM2985,
  //             "Task_LTM2985",
  //             1024, // Stack size
  //             NULL,
  //             1, // Priority
  //             &Task_LTM2985_Handle);

  xTaskCreate(Task_read_ADC,
              "Task_read_ADC",
              1024, // Stack size
              NULL,
              1, // Priority
              &Task_read_ADC_Handle);

  xTaskCreate(Task_UDP,
              "Task_UDP",
              2048, // Larger stack size for network operations
              NULL,
              2, // Higher priority for network
              &Task_UDP_Handle);

  rp2040.wdt_begin(2000);
}

// ---------------------- Main Loop ----------------------

/**
 * @brief Main application loop (core0).
 *
 * Continuously processes Ethernet UDP packets.
 */
void loop()
{
  static unsigned long lastHeartbeat = 0;

  rp2040.wdt_reset();

  // Print heartbeat every 5 seconds to confirm board is running
  if (millis() - lastHeartbeat > 5000)
  {
    Serial.println("Main loop running...");
    lastHeartbeat = millis();
  }
  delay(1);
  // Small delay to prevent busy-waiting, could also use yield()
}

// ---------------------- Secondary Core Setup ----------------------

/**
 * @brief Setup function for second core (if used).
 */
void setup1()
{
  // Currently unused
}

/**
 * @brief Loop for second core (if used).
 */
void loop1()
{
  delay(1);
}
