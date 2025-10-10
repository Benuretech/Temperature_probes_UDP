#pragma once // Tells the compiler to include this file only once during compilation

/////////////////////    Pin Control    ///////////////////

#define RTD1 101 // Command to send/receive channel 1 reading
#define RTD2 102 // Command to send/receive channel 1 reading
#define RTD3 103 // Command to send/receive channel 1 reading
#define RTD4 104 // Command to send/receive channel 1 reading

#define FAULT_RTD1 111 // Command to send/receive channel 1 reading
#define FAULT_RTD2 112 // Command to send/receive channel 1 reading
#define FAULT_RTD3 113 // Command to send/receive channel 1 reading
#define FAULT_RTD4 114 // Command to send/receive channel 1 reading

#define ADC1 121 // Command to send/receive channel 1 reading
#define ADC2 122 // Command to send/receive channel 1 reading
#define ADC3 123 // Command to send/receive channel 1 reading
#define ADC4 124 // Command to send/receive channel 1 reading

#define LOCAL_RTD 101       // Command to send/receive channel 1 reading
#define LOCAL_FAULT_RTD 111 // Command to send/receive channel 1 reading
#define LOCAL_ADC 121       // Command to send/receive channel 1 reading

#define ALL_STATUS 200 // Command to send all status information such as channel readings, PWM settings, and errors.

#define WIFI_SSID "TestBench"
#define WIFI_PASS "0123456789"
#define LOCAL_PORT 8888
#define REMOTE_IP "192.168.0.168"
#define REMOTE_PORT 8888