#include "Serial_PPP.h"

// Constructor - initialize start character and reset buffers
Serial_PPP::Serial_PPP(void)
{
  stream_out[0] = 0x0D;         // Start frame marker '\r'
  escaped_stream_out[0] = 0x0D; // Start frame marker '\r'
  reset_out();
  reset_in();
}

// Reset the input buffer and state flags
void Serial_PPP::reset_in()
{
  _flag_start_in = false;
  _flag_special_char_in = false;
  _stream_in_pt = _stream_in;
  _stream_length_in = 0;
  _crc_in = crc_init();
}

// Process incoming byte and update the input buffer/state
char Serial_PPP::read_in(char byte_in)
{
  if (_flag_start_in)
  {
    switch (byte_in)
    {
    case '\r':
      reset_in();
      _flag_start_in = true;
      return 9;

    case '\e':
      _flag_special_char_in = true;
      return 3;

    case '\n':
      if (convert_in())
      {
        reset_in();
        return 4; // Valid message
      }
      reset_in();
      return 5; // Invalid message

    default:
      if (_flag_special_char_in)
      {
        _stream_in_pt[0] = 255 - byte_in;
        _flag_special_char_in = false;
      }
      else
      {
        _stream_in_pt[0] = byte_in;
      }
      _stream_in_pt++;
      return 2; // Byte added to stream
    }
  }
  else if (byte_in == '\r')
  {
    reset_in();
    _flag_start_in = true;
    return 1; // Start frame received
  }
  return 0; // Waiting for start frame
}

// Convert received input stream to structured data and validate CRC
bool Serial_PPP::convert_in()
{
  _stream_in_pt--;
  _stream_length_in = _stream_in_pt - _stream_in;

  if ((_stream_in_pt[-1]) * 5 + 1 != _stream_length_in)
  {
    Serial.write(0x0D);
    Serial.print("Err_mcu_l!");
    Serial.write(0x0A);
    return 0; // Length mismatch
  }
  else
  {
    _crc_in = (char)crc_calculate(_stream_in, _stream_length_in);

    if (_crc_in == _stream_in_pt[0])
    {
      single_in.CMD = _stream_in[0];
      single_in.VAL.B_type[0] = _stream_in[1];
      single_in.VAL.B_type[1] = _stream_in[2];
      single_in.VAL.B_type[2] = _stream_in[3];
      single_in.VAL.B_type[3] = _stream_in[4];
      return 1; // Valid CRC
    }
    else
    {
      Serial.write(0x0D);
      Serial.print("wrong CRC");
      Serial.write(0x0A);
      return 0; // CRC mismatch
    }
  }
}

// Reset the output stream and counters
void Serial_PPP::reset_out()
{
  stream_out[0] = 0x0D;         // Start frame marker '\r'
  escaped_stream_out[0] = 0x0D; // Start frame marker '\r'
  _tot_mess_out = 0;
  _stream_out_pt = stream_out + 1;
  _escaped_stream_out_pt = escaped_stream_out + 1;
  _crc_out = crc_init();
}

// Add a command and value to the outgoing message stream
void Serial_PPP::add_CMD_VAL_out(char CMD, long VAL)
{
  _mess_temp_out.CMD = CMD;
  _mess_temp_out.VAL.L_type = VAL;
  add_single_out(&_mess_temp_out);
}

// Add a single PPP_data message to the output stream
void Serial_PPP::add_single_out(PPP_data *ppp_single)
{
  _stream_out_pt[0] = ppp_single->CMD; // Add command byte to the stream
  memcpy((_stream_out_pt + 1), (&ppp_single->VAL.B_type), 4);
  // Compute CRC on the 5 bytes of the struct directly
  _crc_out = crc_update(_crc_out, _stream_out_pt, 5);
  _stream_out_pt += 5;
  _tot_mess_out++;
}

// Add multiple messages to the output stream
void Serial_PPP::add_array_out(PPP_data *ppp_single, int size)
{
  for (int i = 0; i < size; i++)
  {
    add_single_out(ppp_single + i);
  }
}

// Finalize output stream by appending count, CRC, and end byte
void Serial_PPP::convert_out()
{
  *_stream_out_pt = _tot_mess_out;                      // Add message count to the second last byte of stream
  _crc_out = crc_update(_crc_out, _stream_out_pt, 1);   // update the CRC for count byte
  _stream_out_pt++;                                     // Move to the next byte
  _crc_out = crc_finalize(_crc_out);                    // Finalize CRC calculation
  *_stream_out_pt++ = _crc_out;                         // Add CRC to the last byte of stream
  *_stream_out_pt++ = 0x0A;                             // End frame '\n'
  _stream_length_out = _stream_out_pt - stream_out + 1; // Calculate the length of the stream

  escape_char_out(); // Escape special characters in the stream
  size_result_out = _escaped_stream_length_out;
  reset_out();
}

// Escape special characters in the outgoing stream
void Serial_PPP::escape_char_out()
{
  char last_raw_escaped = _stream_length_out - 2;

  for (int i = 1; i < last_raw_escaped; i++)
  {
    char c = stream_out[i];
    if (c == '\r' || c == '\n' || c == '\e')
    {
      *_escaped_stream_out_pt++ = '\e';
      *_escaped_stream_out_pt++ = 255 - c;
    }
    else
    {
      *_escaped_stream_out_pt++ = c;
    }
  }
  *_escaped_stream_out_pt = 0x0A; // End frame '\n'
  _escaped_stream_length_out = _escaped_stream_out_pt - escaped_stream_out + 1;
}

// Validate length and CRC of incoming buffer; return message count
char Serial_PPP::length_crc_check_in(char *buffer, int size_buf)
{
  _crc_in = (char)crc_calculate(buffer, (size_buf - 1));
  if (_crc_in == buffer[size_buf - 1])
  {
    if (buffer[size_buf - 2] * 5 + 2 == size_buf)
    {
      return buffer[size_buf - 2];
    }
  }
  return 0;
}
