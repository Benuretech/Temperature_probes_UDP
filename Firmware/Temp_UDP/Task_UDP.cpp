#include "Task_UDP.h"

static WiFiClient net;
WiFiUDP Udp;
// ================== Helpers (task context only) ==================
static void wifiEnsureConnected()
{
  if (WiFi.status() == WL_CONNECTED)
    return;
  Serial.print("WiFi: connecting");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print("WiFi...");
    vTaskDelay(pdMS_TO_TICKS(500));
  }
  Serial.print("\nWiFi OK: ");
  Serial.println(WiFi.localIP());
}

// === Stack Monitoring Task ===
void Task_UDP(void *pvParameters)
{

  Serial.println("UDTP: Starting...");
  // Local connection variables
  bool UDP_Connection_OK = false; // Connection status flag
  bool UDP_Fail_Applied = false;  // Failure applied flag
  bool initialized = false;       // Initialization flag

  int reset_count = 0; // Reset count for watchdog timer

  // Queue variables
  PPP_data ADC_ppp;
  ADC_ppp.CMD = LOCAL_ADC;

  PPP_data LTM2985_ppp;
  LTM2985_ppp.CMD = LOCAL_RTD;

  // ppp object for encoding/decoding
  Serial_PPP ppp;

  // local receiving variable from queue

  RTD_result LTM2985_result;
  int ADC_reading_int;

  int remote_Port = 8888;

  // UDP connection variables
  int packetSize = 0;
  IPAddress remote_IP;

  wifiEnsureConnected();
  Udp.begin(LOCAL_PORT);
  Serial.println("Ethernet_UDP: Initialized");

  for (;;)
  {
    Serial.println("cycling");
    // Keep WiFi/MQTT alive
    if (WiFi.status() != WL_CONNECTED)
    {
      wifiEnsureConnected();
    }

    if (!initialized)
    {
      initialized = true;
      UDP_Connection_OK = true;
      UDP_Fail_Applied = false;
      Serial.println("UDP: Initialized");

      reset_count = 0;
    }

    reset_count = 0; // Reset the reset count

    // Drain TX queue (non-blocking)

    while (xQueueReceive(q_ADC_to_UDP, &ADC_reading_int, 0) == pdTRUE)
    {
      ADC_ppp.VAL.L_type = ADC_reading_int;

      if (WiFi.status() == WL_CONNECTED)
      {
        UDP_Connection_OK = 1;
        // Pass the data to PPP encoder

        ppp.add_CMD_VAL_out(ADC_ppp.CMD, ADC_ppp.VAL.L_type);
        ppp.convert_out();
        Udp.beginPacket(REMOTE_IP, REMOTE_PORT);
        Udp.write((uint8_t *)ppp.escaped_stream_out, ppp.size_result_out);
        Udp.endPacket();
        Serial.println("UDP: ADC data sent");
      }
    }

    // Example: periodic heartbeat (optional)
  }
}
