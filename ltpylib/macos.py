#!/usr/bin/env python
import logging
import os.path
from getpass import getpass, getuser
from pathlib import Path
from typing import List, Union

from ltpylib import enums, inputs, procs

MAC_SOUND_DIRS = [
  "/System/Library/Sounds",
  "~/Library/Sounds",
]


class MacSoundsSystem(enums.EnumAutoName):
  BASSO = "Basso"
  BLOW = "Blow"
  BOTTLE = "Bottle"
  FROG = "Frog"
  FUNK = "Funk"
  GLASS = "Glass"
  HERO = "Hero"
  MORSE = "Morse"
  PING = "Ping"
  POP = "Pop"
  PURR = "Purr"
  SOSUMI = "Sosumi"
  SUBMARINE = "Submarine"
  TINK = "Tink"


MAC_SOUND_FAILURE = MacSoundsSystem.BASSO
MAC_SOUND_FINISHED = MacSoundsSystem.FUNK


def notify(message: str, title: str = "Terminal Notification", sound_name: Union[str, MacSoundsSystem] = MacSoundsSystem.PING, subtitle: str = ""):
  message = message.replace('"', '\\"').replace("\n", "\\n")
  title = title.replace('"', '\\"')
  sound_name = (sound_name.name if isinstance(sound_name, MacSoundsSystem) else sound_name).replace('"', '\\"')
  subtitle = subtitle.replace('"', '\\"')

  js_function = f"""
var app = Application.currentApplication()

app.includeStandardAdditions = true

app.displayNotification("{message}", {{
    withTitle: "{title}",
    subtitle: "{subtitle}",
    soundName: "{sound_name}"
}})
"""
  result = procs.run_with_regular_stdout([
    "/usr/bin/osascript",
    "-l",
    "JavaScript",
    "-e",
    js_function,
  ])
  if __name__ == "__main__":
    exit(result.returncode)


def pbcopy(val: str):
  procs.run_with_regular_stdout(
    ["pbcopy"],
    input=val,
    check=True,
  )


def find_sound_file(sound: Union[MacSoundsSystem, str]):
  sound_name = (sound.name if isinstance(sound, MacSoundsSystem) else sound)
  for sounds_dir in MAC_SOUND_DIRS:
    for file_ext in ["", ".aiff"]:
      sound_file = Path(os.path.expanduser(sounds_dir)).joinpath(sound_name + file_ext)
      if sound_file.is_file():
        return sound_file

  if isinstance(sound, MacSoundsSystem):
    raise ValueError("sound file not found for: %s" % sound)

  sound_file = Path(os.path.expanduser(sound_name))
  if sound_file.is_file():
    return sound_file

  raise ValueError("sound file not found for: %s" % sound)


def play_sound(sound: Union[MacSoundsSystem, str]):
  procs.run_with_regular_stdout(["afplay", find_sound_file(sound).as_posix()], check=True)


def add_generic_password(label: str, pw: str, account: str = None) -> bool:
  if account is None:
    account = getuser()

  result = procs.run_with_regular_stdout([
    "security",
    "add-generic-password",
    "-a",
    account,
    "-s",
    label,
    "-w",
    pw,
  ])
  if result.returncode != 0:
    raise Exception("Could not add generic keychain password: label=%s account=%s" % (label, account))

  return True


def find_generic_password(
  label: str,
  ask_if_missing: bool = True,
  add_if_missing: bool = False,
  prompt_to_add_if_missing: bool = True,
) -> str:
  status, pw = procs.run_and_parse_output([
    "security",
    "find-generic-password",
    "-ws",
    label,
  ])
  if status != 0:
    if ask_if_missing:
      prompt = 'Please enter your password for %s.' % (label)
      if not add_if_missing:
        prompt += ' You can skip entering your password by running: security add-generic-password -a "$USER" -s "%s" -w' % (label)

      pw = getpass(prompt="%s\n> " % prompt)
      if add_if_missing and pw:
        if not prompt_to_add_if_missing or inputs.confirm('Add this password to your keychain in order to skip this prompt next time?', default="y"):
          logging.info('Adding generic password to keychain...')
          add_generic_password(label, pw, account=getuser())
    else:
      raise Exception("Could not find generic keychain password for label: %s" % label)

  return pw.strip()


def add_internet_password(host: str, pw: str, user: str = None) -> bool:
  if user is None:
    user = getuser()

  result = procs.run_with_regular_stdout([
    "security",
    "add-internet-password",
    "-t",
    "dflt",
    "-a",
    user,
    "-s",
    host,
    "-w",
    pw,
  ])
  if result.returncode != 0:
    raise Exception("Could not add internet keychain password: host=%s user=%s" % (host, user))

  return True


def find_internet_password(
  host: str,
  user: str = None,
  ask_if_missing: bool = True,
  add_if_missing: bool = False,
  prompt_to_add_if_missing: bool = True,
):
  if user is None:
    user = getuser()

  status, pw = procs.run_and_parse_output([
    "/usr/bin/security",
    "find-internet-password",
    "-t",
    "dflt",
    "-a",
    user,
    "-ws",
    host,
  ])
  if status != 0:
    if ask_if_missing:
      prompt = 'Please enter your password for %s.' % (host)
      if not add_if_missing:
        prompt += ' You can skip entering your password by running: security add-internet-password -a "$USER" -s "%s" -w' % (host)

      pw = getpass(prompt="%s\n> " % prompt)
      if add_if_missing and pw:
        if not prompt_to_add_if_missing or inputs.confirm('Add this password to your keychain in order to skip this prompt next time?', default="y"):
          logging.info('Adding internet password to keychain...')
          add_internet_password(host, pw, user=user)
    else:
      raise Exception("Could not find internet keychain password for label: %s" % host)

  return pw.strip()


def open_url(url: str):
  return procs.run_with_regular_stdout(["open", url], check=True)


def trash(paths: Union[List[Path], List[str], Path, str], check: bool = True) -> bool:
  if not isinstance(paths, list):
    paths = [paths]

  paths = [p.as_posix() if isinstance(p, Path) else p for p in paths]

  return procs.run_with_regular_stdout(["trash", "-Fv"] + paths, check=check).returncode == 0


def _main():
  import sys

  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)


if __name__ == "__main__":
  try:
    _main()
  except KeyboardInterrupt:
    exit(130)
