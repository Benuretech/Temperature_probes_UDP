#include "LTM2985.h"

// Assigns specific sensors to selected channels (e.g., sense resistor, RTDs).
void configure_channels()
{
  uint8_t channel_number;
  uint32_t channel_assignment_data;

  // ----- Channel 2: Assign Sense Resistor -----
  channel_assignment_data = SENSOR_TYPE__SENSE_RESISTOR | (uint32_t)0xFA000 << SENSE_RESISTOR_VALUE_LSB; // sense resistor - value: 1000.
  assign_channel(2, channel_assignment_data);
  // ----- Channel 4: Assign RTD PT-100 -----
  channel_assignment_data =
      SENSOR_TYPE__RTD_PT_100 | RTD_RSENSE_CHANNEL__2 | RTD_NUM_WIRES__2_WIRE | RTD_EXCITATION_MODE__NO_ROTATION_SHARING | RTD_EXCITATION_CURRENT__500UA | RTD_STANDARD__AMERICAN;
  assign_channel(4, channel_assignment_data);

  // // ----- Channel 6: Assign RTD PT-100 -----
  // channel_assignment_data =
  //     SENSOR_TYPE__RTD_PT_100 | RTD_RSENSE_CHANNEL__2 | RTD_NUM_WIRES__2_WIRE | RTD_EXCITATION_MODE__NO_ROTATION_SHARING | RTD_EXCITATION_CURRENT__500UA | RTD_STANDARD__AMERICAN;
  // assign_channel(6, channel_assignment_data);
  // // ----- Channel 8: Assign RTD PT-100 -----
  // channel_assignment_data =
  //     SENSOR_TYPE__RTD_PT_100 | RTD_RSENSE_CHANNEL__2 | RTD_NUM_WIRES__2_WIRE | RTD_EXCITATION_MODE__NO_ROTATION_SHARING | RTD_EXCITATION_CURRENT__500UA | RTD_STANDARD__AMERICAN;
  // assign_channel(8, channel_assignment_data);
  // // ----- Channel 10: Assign RTD PT-100 -----
  // channel_assignment_data =
  //     SENSOR_TYPE__RTD_PT_100 | RTD_RSENSE_CHANNEL__2 | RTD_NUM_WIRES__2_WIRE | RTD_EXCITATION_MODE__NO_ROTATION_SHARING | RTD_EXCITATION_CURRENT__500UA | RTD_STANDARD__AMERICAN;
  // assign_channel(10, channel_assignment_data);
}

// Setup overall global parameters for the LTM2985.
void configure_global_parameters()
{
  // -- Set global parameters
  transfer_byte_LTM2985(WRITE_TO_RAM, 0xF0, TEMP_UNIT__C | REJECTION__50_60_HZ);

  // -- Set any extra delay between conversions (in this case, 0*100us)
  transfer_byte_LTM2985(WRITE_TO_RAM, 0xFF, 0);
}
///////////////////////////////////////////////////////////////////////////////////////////////////
// ***********************
// Program the part
// ***********************
void assign_channel(uint8_t channel_number, uint32_t channel_assignment_data)
{
  uint16_t start_address = get_start_address(CH_ADDRESS_BASE, channel_number);
  transfer_four_bytes_LTM2985(WRITE_TO_RAM, start_address, channel_assignment_data);
}

// Reads temperature data from a given channel of the LTM2985
RTD_result_type read_temp(uint8_t channel_number)
{
  RTD_result_type RTD_result;
  RTD_result.channel = channel_number;

  float scaled_result;

  // Calculate memory address based on channel number
  uint16_t start_address = get_start_address(CONVERSION_RESULT_MEMORY_BASE, channel_number);
  uint32_t raw_conversion_result;

  uint32_t raw_data = transfer_four_bytes_LTM2985(READ_FROM_RAM, start_address, 0);
  RTD_result.fault = raw_data >> 24;
  raw_conversion_result = raw_data & 0xFFFFFF;

  RTD_result.value = raw_conversion_result;

  // Convert the 24 LSB's into a signed 32-bit integer
  if (RTD_result.value & 0x800000)
    RTD_result.value = RTD_result.value | 0xFF000000;

  return RTD_result;
}

// Sends command to start temperature conversion for a specific channel
void measure_request(uint8_t channel_number)
{
  // Start conversion
  transfer_byte_LTM2985(WRITE_TO_RAM, COMMAND_STATUS_REGISTER, CONVERSION_CONTROL_BYTE | channel_number);
}

// Waits for the LTM2985 process to finish
void wait_for_process_to_finish()
{
  uint8_t process_finished = 0;
  uint8_t data;
  while (process_finished == 0)
  {
    data = transfer_byte_LTM2985(READ_FROM_RAM, COMMAND_STATUS_REGISTER, 0);
    process_finished = data & 0x40;
  }
}

// Calculates the start address for a given channel number based on the base address
uint16_t get_start_address(uint16_t base_address, uint8_t channel_number)
{
  return base_address + 4 * (channel_number - 1);
}

// Reads and sends a byte array
void set_SPI_LTM2985()
{
  pinMode(CHIP_SELECT, OUTPUT);

  SPI.setSCK(SPI_SCK);
  SPI.setTX(SPI_TX);
  SPI.setRX(SPI_RX);
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
  SPI.begin();
}

// Reads and sends a 4-byte data block
uint32_t transfer_four_bytes_LTM2985(uint8_t ram_read_or_write, uint16_t start_address, uint32_t input_data)
{
  uint32_t output_data;
  uint8_t tx[7], rx[7];

  tx[6] = ram_read_or_write;
  tx[5] = highByte(start_address);
  tx[4] = lowByte(start_address);
  tx[3] = (uint8_t)(input_data >> 24);
  tx[2] = (uint8_t)(input_data >> 16);
  tx[1] = (uint8_t)(input_data >> 8);
  tx[0] = (uint8_t)input_data;

  spi_transfer_block_LTM2985(tx, rx, 7);

  output_data = (uint32_t)rx[3] << 24 |
                (uint32_t)rx[2] << 16 |
                (uint32_t)rx[1] << 8 |
                (uint32_t)rx[0];

  return output_data;
}

// Reads and sends a byte to the LTM2985
uint8_t transfer_byte_LTM2985(uint8_t ram_read_or_write, uint16_t start_address, uint8_t input_data)
{
  uint8_t tx[4], rx[4];

  tx[3] = ram_read_or_write;
  tx[2] = (uint8_t)(start_address >> 8);
  tx[1] = (uint8_t)start_address;
  tx[0] = input_data;
  spi_transfer_block_LTM2985(tx, rx, 4);

  return rx[0];
}

// SPI LAYER 1
// Reads and sends a byte
// Return 0 if successful, 1 if failed
void spi_transfer_byte_LTM2985(uint8_t tx, uint8_t *rx)
{

  digitalWrite(CHIP_SELECT, false); //! 1) Pull CS low
  *rx = SPI.transfer(tx);           //! 2) Read byte and send byte

  digitalWrite(CHIP_SELECT, HIGH); //! 3) Pull CS high
}

// Reads and sends a word
// Return 0 if successful, 1 if failed
void spi_transfer_word_LTM2985(uint16_t tx, uint16_t *rx)
{
  union
  {
    uint8_t b[2];
    uint16_t w;
  } data_tx;

  union
  {
    uint8_t b[2];
    uint16_t w;
  } data_rx;

  data_tx.w = tx;

  digitalWrite(CHIP_SELECT, false); //! 1) Pull CS low

  data_rx.b[1] = SPI.transfer(data_tx.b[1]); //! 2) Read MSB and send MSB
  data_rx.b[0] = SPI.transfer(data_tx.b[0]); //! 3) Read LSB and send LSB

  *rx = data_rx.w;

  digitalWrite(CHIP_SELECT, HIGH); //! 4) Pull CS high
}

// Reads and sends a byte array
void spi_transfer_block_LTM2985(uint8_t *tx, uint8_t *rx, uint8_t length)
{
  int8_t i;

  digitalWrite(CHIP_SELECT, false); //! 1) Pull CS low

  for (i = (length - 1); i >= 0; i--)
    rx[i] = SPI.transfer(tx[i]);   //! 2) Read and send byte array
  digitalWrite(CHIP_SELECT, HIGH); //! 3) Pull CS high
}
