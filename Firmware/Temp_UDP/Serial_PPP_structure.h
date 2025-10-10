#pragma once

/**
 * Union to hold different types of values.
 * It can store a float, a long integer, or a byte array of size 4.
 */
union union_val
{
  float F_type;
  long L_type;
  char B_type[4];
};

/*
 * Struct to hold the data for the PPP (Point-to-Point Protocol) command.
 * It contains a command character and a union for the value.
 */
typedef struct
{
  char CMD;
  union_val VAL;
} PPP_data;