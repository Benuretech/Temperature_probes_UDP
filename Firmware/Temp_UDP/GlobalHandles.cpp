/**
 * @file GlobalHandles.cpp
 * @brief Definitions of global FreeRTOS handles declared in GlobalHandles.h
 *
 * This file defines and initializes the actual memory for global task handles,
 * semaphores, and queues used across different modules of the system.
 *
 * These handles enable coordination between FreeRTOS tasks like LTM2985 reading,
 * command handling, and PWM signal generation.
 */

#include "GlobalHandles.h"

SemaphoreHandle_t stopSemaphore;
SemaphoreHandle_t UDP_Connection_Init_Semaphore;

TaskHandle_t Task_LTM2985_Handle = NULL;
TaskHandle_t Task_read_ADC_Handle = NULL;
TaskHandle_t Task_UDP_Handle = NULL;

QueueHandle_t q_LTM2985_to_UDP;
QueueHandle_t q_ADC_to_UDP;
