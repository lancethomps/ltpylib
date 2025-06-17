#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse

from ltpylib import opts


def get_python_available_functions():
  import importlib
  from ltpylib import reflections

  arg_parser = opts.create_default_with_positionals_arg_parser(positionals_key="module")
  arg_parser.add_argument("--include-signature", "-is", action=argparse.BooleanOptionalAction, default=False)
  arg_parser.add_argument("--attr", "--class-name", "-a", "-c", help="Attribute to get functions from, such as a class name.")
  arg_parser.add_argument("--sep-char", "-s", default=" ")

  args = opts.parse_args_with_positionals_and_init_others(arg_parser, log_use_stderr=True)

  imported = importlib.import_module(args.module[0])
  if args.attr:
    imported = getattr(imported, args.attr)

  funcs = reflections.get_functions_of_class(imported, include_signature=args.include_signature)
  print(args.sep_char.join(funcs))
