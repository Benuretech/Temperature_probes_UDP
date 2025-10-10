#pragma once

#include <Arduino.h>
#include <FreeRTOS.h>
#include <task.h>
#include <queue.h>
#include <semphr.h>
#include "Custom_Structures.h"

/**
 * @file GlobalHandles.h
 * @brief Declarations of global FreeRTOS handles used across the application.
 *
 * This file declares global task handles, queue handles, and semaphore handles
 * used for coordination between different FreeRTOS tasks in the system.
 * These handles are shared across modules and initialized in GlobalHandles.cpp.
 *
 * Tasks: LTM2985, Command handler, PWM controllers.
 * Semaphores: For system init and UDP connection status.
 * Queues: For inter-task communication (e.g., UDP <-> Command, PWM <-> Command).
 */

extern SemaphoreHandle_t stopSemaphore;
extern SemaphoreHandle_t UDP_Connection_Init_Semaphore;

extern TaskHandle_t Task_LTM2985_Handle;
extern TaskHandle_t Task_read_ADC_Handle;
extern TaskHandle_t Task_UDP_Handle;

extern QueueHandle_t q_LTM2985_to_UDP;
extern QueueHandle_t q_ADC_to_UDP;
