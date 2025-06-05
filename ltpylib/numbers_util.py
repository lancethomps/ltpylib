#!/usr/bin/env python
from decimal import Decimal, ROUND_HALF_DOWN
from typing import Union


def convert_decimal_precision(val: Union[Decimal, float, str], precision: int, rounding: str = ROUND_HALF_DOWN) -> Decimal:
  if precision == 0:
    exp = Decimal("1")
  else:
    exp = Decimal("." + ("0" * (precision - 1)) + "1")

  if not isinstance(val, Decimal):
    val = Decimal(val)

  return val.quantize(
    exp,
    rounding=rounding,
  )


def format_number(number: Union[Decimal, float, int], precision: int = 0, default_value: str = "") -> str:
  if number is None:
    return default_value

  format_str = "{:,.%sf}" % precision
  return format_str.format(number)
