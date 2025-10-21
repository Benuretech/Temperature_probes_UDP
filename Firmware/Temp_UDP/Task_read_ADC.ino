#include "GlobalHandles.h"
#include "QuickMedianLib.h"
#include "Custom_Structures.h"

#define MAX_ARRAY 20

void Task_read_ADC(void *pvParameters)
{
  (void)pvParameters;

  ADC_struct ADC_reading;

  int measurements_ADC1[MAX_ARRAY];
  int ADC1_reading = 0;

  int measurements_ADC2[MAX_ARRAY];
  int ADC2_reading = 0;

  int measurements_index = 0;
  unsigned long startcount = millis();

  for (;;) // A Task shall never return or exit.
  {

    // Thread has a delay of 1 ms, hence the sampling rate will be 100/s
    delay(100);

    // If the maximum of elements in the array hasn't been reach, keep sampling every 10 ms
    if (measurements_index < MAX_ARRAY)
    {
      measurements_ADC1[measurements_index] = (analogRead(A0));
      measurements_index++;

      measurements_ADC2[measurements_index] = (analogRead(A1));
      measurements_index++;
    }

    // After 1000ms, find the median of the array, reset the array, submit the value. The 1000ms is the filtered streaming rate of the ADC
    if (millis() - startcount > 1000)
    {

      ADC1_reading = QuickMedian<int>::GetMedian(measurements_ADC1, measurements_index);
      ADC2_reading = QuickMedian<int>::GetMedian(measurements_ADC2, measurements_index);

      // Send the data and reset the streaming rate
      ADC_reading.ADC1 = ADC1_reading;
      ADC_reading.ADC2 = ADC2_reading;
      xQueueSend(q_ADC_to_UDP, &ADC_reading, 0);
      measurements_index = 0;
      startcount = millis();
    }
  }
}
