/**
 * @file Serial_PPP.h
 * @brief Serial_PPP protocol class for sending and receiving binary messages with CRC and framing.
 *
 * This class implements a lightweight PPP-style messaging protocol over a serial interface. It supports framing, escaping special characters, and CRC-8 validation 
 * using the AceCRC library.
 *
 * Message Format:
 *   - Start byte: '\r' (0x0D)
 *   - End byte: '\n' (0x0A)
 *   - Escaped characters: '\r', '\n', '\e'
 *   - Payload: command + 4-byte value
 *   - CRC-8: for message integrity
 */

#pragma once
#include "Serial_PPP_structure.h"
#include <Arduino.h>
#include <AceCRC.h>
using namespace ace_crc::crc8_byte;

/**
 * @brief Serial_PPP class for handling PPP-style serial communication.
 */
class Serial_PPP
{
public:
  Serial_PPP();  // Constructor initializes internal state of the Serial_PPP class

  // Input (Receiving)
  void reset_in();            ///< Reset internal state for receiving
  char read_in(char byte_in); ///< Process incoming byte and return state
  PPP_data single_in;         ///< Stores the most recently decoded message

  // Output (Sending)
  void reset_out();                                   ///< Reset internal state for sending
  void add_CMD_VAL_out(char CMD, long VAL);           ///< Add message with CMD and long VAL
  void add_single_out(PPP_data *ppp_single);          ///< Add message by pointer
  void add_array_out(PPP_data *ppp_single, int size); ///< Add multiple messages
  void convert_out();                                 ///< Finalize the output stream (add CRC, count, etc.)

  // Accessors
  char *getStream();    ///< Get pointer to finalized output stream
  char getStreamSize(); ///< Get size of finalized output stream

  // Utility
  char length_crc_check_in(char *buffer, int size_buf); ///< Validate incoming buffer
  char crc_out;                                         ///< Last calculated output CRC
  char tot_mess_out;                                    ///< Total messages in output

  char stream_out[200];
  char escaped_stream_out[200];
  char size_result_out;

private:
  // Input handling

  bool convert_in();
  void escape_char_out();
  bool _flag_start_in;
  bool _flag_special_char_in;
  char _stream_in[200];
  char *_stream_in_pt;
  char _stream_length_in;

  crc_t _crc_in;

  // Output handling
  PPP_data _mess_temp_out;

  char *_stream_out_pt;         ///< Pointer to the current position in the output stream
  char *_escaped_stream_out_pt; ///< Pointer to the current position in the output stream

  crc_t _crc_out;
  char _tot_mess_out; ///< Total messages in the output stream
  char _stream_length_out;
  char _escaped_stream_length_out;
  // Debug
  char _ppp_hexCar[20]; // Optional ASCII representation for debugging
};
