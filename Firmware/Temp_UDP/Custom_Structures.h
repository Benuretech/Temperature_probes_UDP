#pragma once
#include <cstdint>

/*
 * Struct to hold the result of an RTD reading.
 * It contains the channel number, fault status, and the value of the reading.
 */
struct RTD_result_type
{
  uint8_t channel;
  uint8_t fault;
  int32_t value;
};

struct ADC_struct
{
  int ADC1;
  int ADC2;
};
