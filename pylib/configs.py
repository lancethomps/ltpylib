#!/usr/bin/env python3

import glob
import os
from collections import OrderedDict

try:
  import configparser as cp
except:
  import ConfigParser as cp

try:
  import io as io_compat
except:
  import StringIO as io_compat


def get_host(key, use_key_as_default=True):
  hosts_dir = os.path.abspath('%s/config/hosts' % os.getenv('DOTFILES', '%s/.dotfiles' % os.getenv('HOME')))
  hosts = cp.ConfigParser()
  host_files = glob.glob(hosts_dir + '/*.properties')
  host_files.extend(glob.glob(hosts_dir + '/*/*.properties'))
  for hosts_file in host_files:
    hosts = _py2_read_properties(hosts_file, config=hosts)

  if use_key_as_default:
    try:
      return hosts.get('DEFAULT', key)
    except cp.NoOptionError:
      return key
    except cp.NoSectionError:
      return key
  else:
    return hosts.get('DEFAULT', key)


def config_parser_to_string(config, sort_keys=False):
  if sort_keys:
    if config._defaults:
      config._defaults = OrderedDict(sorted(config._defaults.items(), key=lambda t: t[0]))

    for section in config._sections:
      config._sections[section] = OrderedDict(sorted(config._sections[section].items(), key=lambda t: t[0]))

    config._sections = OrderedDict(sorted(config._sections.items(), key=lambda t: t[0]))

  sio = io_compat.StringIO()
  config.write(sio)
  return sio.getvalue()


def _py2_read_properties(file, use_mock_default_section=True, config=None):
  if not os.path.isfile(file):
    raise ValueError("File does not exist: %s" % file)

  if config is None:
    config = cp.ConfigParser(allow_no_value=True)
    config.optionxform = str

  if use_mock_default_section:
    with open(file, 'r') as configfile:
      try:
        config.read_string('[DEFAULT]\n' + configfile.read())
      except:
        import StringIO

        config.readfp(StringIO.StringIO('[DEFAULT]\n' + configfile.read()))
  else:
    config.read(file)

  return config


if __name__ == "__main__":
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)
