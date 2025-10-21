#pragma once

#include <stdint.h>
#include "Custom_Structures.h"
#include "SPI.h"
#include "LTM2985_configuration_constants.h"
#include <Arduino.h>

// -----------------------------
// Pin Definitions
// -----------------------------

#define SPI_RX 0      // SPI MISO (Master In Slave Out) pin
#define CHIP_SELECT 1 // SPI Chip Select pin
#define SPI_SCK 2     // SPI Clock pin
#define SPI_TX 3      // SPI MOSI (Master Out Slave In) pin
#define INT_PIN1 4    // Interrupt pin

// -----------------------------
// Initialization & Configuration
// -----------------------------

/**
 * @brief Initializes SPI communication for the LTM2985.
 */
void set_SPI_LTM2985();

/**
 * @brief Assigns specific sensors to selected channels (e.g., sense resistor, RTDs).
 *         Channel configuration is hardcoded for common sensor setups.
 */
void configure_channels();

/**
 * @brief Configures global parameters like temperature unit and line rejection.
 */
void configure_global_parameters();

/**
 * @brief Writes channel-specific configuration data to the LTM2985.
 *
 * @param channel_number Channel to assign configuration to
 * @param channel_assignment_data Bitmask containing sensor type, wiring, excitation, etc.
 */
void assign_channel(uint8_t channel_number, uint32_t channel_assignment_data);

// -----------------------------
// Temperature Measurement
// -----------------------------

/**
 * @brief Reads temperature and fault status from the specified channel.
 *
 * @param channel_number Channel to read from
 * @return RTD_result Struct containing raw value and fault code
 */
RTD_result_type read_temp(uint8_t channel_number);

/**
 * @brief Sends a command to the LTM2985 to begin temperature conversion on the selected channel.
 *
 * @param channel_number Target channel for measurement
 */
void measure_request(uint8_t channel_number);

/**
 * @brief Waits until the temperature conversion process is complete.
 */
void wait_for_process_to_finish();

/**
 * @brief Calculates the memory address for a given channel based on a base address.
 *
 * @param base_address Starting address of memory block (e.g., channel or result base)
 * @param channel_number Channel number (1-based index)
 * @return uint16_t Address offset for that channel
 */
uint16_t get_start_address(uint16_t base_address, uint8_t channel_number);

// -----------------------------
// SPI Communication Layer 2 (Protocol-Level Transfers)
// -----------------------------

/**
 * @brief Transfers a single byte to/from the LTM2985's RAM.
 *
 * @param rw READ_FROM_RAM or WRITE_TO_RAM
 * @param address Target memory address
 * @param data Byte to send
 * @return Received byte (if reading)
 */
uint8_t transfer_byte_LTM2985(uint8_t rw, uint16_t address, uint8_t data);

/**
 * @brief Transfers 4 bytes (32 bits) to/from the LTM2985.
 *         Used for channel configurations and reading conversion results.
 *
 * @param rw READ_FROM_RAM or WRITE_TO_RAM
 * @param address Memory address to read from or write to
 * @param data 32-bit data (input or dummy if reading)
 * @return Received 32-bit data (if reading)
 */
uint32_t transfer_four_bytes_LTM2985(uint8_t rw, uint16_t address, uint32_t data);

// -----------------------------
// SPI Communication Layer 1 (Low-Level Transfers)
// -----------------------------

/**
 * @brief Transfers a single byte via SPI.
 *
 * @param tx Byte to send
 * @param rx Pointer to store received byte
 */
void spi_transfer_byte_LTM2985(uint8_t tx, uint8_t *rx);

/**
 * @brief Transfers a 16-bit word via SPI.
 *
 * @param tx Word to send
 * @param rx Pointer to store received word
 */
void spi_transfer_word_LTM2985(uint16_t tx, uint16_t *rx);

/**
 * @brief Transfers an entire block (array) of bytes over SPI.
 *
 * @param tx Pointer to transmit buffer
 * @param rx Pointer to receive buffer
 * @param length Number of bytes to transfer
 */
void spi_transfer_block_LTM2985(uint8_t *tx, uint8_t *rx, uint8_t length);
