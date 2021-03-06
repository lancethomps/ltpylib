#!/usr/bin/env python3
import logging
from getpass import getpass, getuser

from ltpylib import inputs, procs


def notify(message: str, title: str = "Terminal Notification", sound_name: str = "Ping", subtitle: str = ""):
  message = message.replace('"', '\\"')
  title = title.replace('"', '\\"')
  sound_name = sound_name.replace('"', '\\"')
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


def find_generic_password(label: str, ask_if_missing: bool = True, add_if_missing: bool = False, prompt_to_add_if_missing: bool = True) -> str:
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
