#pragma once
#include "Command_Define.h"
#include "GlobalHandles.h"
#include <cstdint>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <SPI.h>
#include <Arduino.h>
#include <task.h>

#include <task.h>
#include <queue.h>
#include <semphr.h>
#include "Serial_PPP.h"
#include "Custom_Structures.h"

// Define UDP_TX_PACKET_MAX_SIZE if not defined already.
#ifndef UDP_TX_PACKET_MAX_SIZE
#define UDP_TX_PACKET_MAX_SIZE 512
#endif

// Task function declaration
void Task_UDP(void *pvParameters);
