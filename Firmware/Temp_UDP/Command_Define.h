#pragma once // Tells the compiler to include this file only once during compilation

#define RTD_OFFSET 20

#define RTD_BASE_1 1 // Command to send/receive channel 1 reading
#define RTD_BASE_2 2 // Command to send/receive channel 2 reading
#define RTD_BASE_3 3 // Command to send/receive channel 3 reading
#define RTD_BASE_4 4 // Command to send/receive channel 4 reading

#define RTD_BASE_5 5 // Command to send/receive channel 5 reading
#define RTD_BASE_6 6 // Command to send/receive channel 6 reading
#define RTD_BASE_7 7 // Command to send/receive channel 7 reading
#define RTD_BASE_8 8 // Command to send/receive channel 8 reading

#define FAULT_RTD_BASE 11 // Command to send/receive channel RTDA reading
#define RTD_BASE_ADC1 12  // ADC1 from RTDA
#define RTD_BASE_ADC2 13  // ADC2 from RTDA

#define OFFSETTING(VAL, OFFSET) ((VAL) + (OFFSET))

#define RTD1 OFFSETTING(RTD_BASE_1, RTD_OFFSET) // Command to send/receive channel 1 reading
#define RTD2 OFFSETTING(RTD_BASE_2, RTD_OFFSET) // Command to send/receive channel 2 reading
#define RTD3 OFFSETTING(RTD_BASE_3, RTD_OFFSET) // Command to send/receive channel 3 reading
#define RTD4 OFFSETTING(RTD_BASE_4, RTD_OFFSET) // Command to send/receive channel 4 reading

#define RTD5 OFFSETTING(RTD_BASE_5, RTD_OFFSET) // Command to send/receive channel 5 reading
#define RTD6 OFFSETTING(RTD_BASE_6, RTD_OFFSET) // Command to send/receive channel 6 reading
#define RTD7 OFFSETTING(RTD_BASE_7, RTD_OFFSET) // Command to send/receive channel 7 reading
#define RTD8 OFFSETTING(RTD_BASE_8, RTD_OFFSET) // Command to send/receive channel 8 reading

#define FAULT_RTD OFFSETTING(FAULT_RTD_BASE, RTD_OFFSET) // Command to send/receive channel RTD8 reading
#define RTD_ADC1 OFFSETTING(RTD_BASE_ADC1, RTD_OFFSET)   // ADC1
#define RTD_ADC2 OFFSETTING(RTD_BASE_ADC2, RTD_OFFSET)   // ADC2

#define LOCAL_RTD 101       // Command to send/receive channel 1 reading
#define LOCAL_FAULT_RTD 111 // Command to send/receive channel 1 reading
#define LOCAL_ADC 121       // Command to send/receive channel 1 reading

#define ALL_STATUS 200 // Command to send all status information such as channel readings, PWM settings, and errors.

#define WIFI_SSID "TestBench"
#define WIFI_PASS "0123456789"
#define LOCAL_PORT 8888
#define REMOTE_IP "192.168.0.168"
#define REMOTE_PORT 8888