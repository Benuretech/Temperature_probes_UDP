#include "GlobalHandles.h"
#include "QuickMedianLib.h"
#define MAX_ARRAY 20

void Task_read_ADC(void *pvParameters)
{
  (void)pvParameters;

  int measurements_A[MAX_ARRAY];
  int ADC_reading = 0;

  int measurements_index = 0;
  unsigned long startcount = millis();

  for (;;) // A Task shall never return or exit.
  {

    // Thread has a delay of 10 ms, hence the sampling rate will be 100/s
    delay(10);

    // If the maximum of elements in the array hasn't been reach, keep sampling every 10 ms
    if (measurements_index < MAX_ARRAY)
    {
      measurements_A[measurements_index] = (analogRead(A0));
      measurements_index++;
    }

    // After 50ms, find the median of the array, reset the array, submit the value. The 50ms is the filtered streaming rate of the ADC
    if (millis() - startcount > 50)
    {

      ADC_reading = QuickMedian<int>::GetMedian(measurements_A, measurements_index);

      // Send the data and reset the streaming rate

      xQueueSend(q_ADC_to_UDP, &ADC_reading, 0);
      measurements_index = 0;
      startcount = millis();
    }
  }
}
