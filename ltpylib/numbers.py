#!/usr/bin/env python
import decimal
from decimal import Decimal


def convert_decimal_precision(val: Decimal, precision: int, rounding: str = decimal.ROUND_HALF_DOWN) -> Decimal:
  if precision == 0:
    exp = Decimal("1")
  else:
    exp = Decimal("." + ("0" * (precision - 1)) + "1")

  return val.quantize(
    exp,
    rounding=rounding,
  )
