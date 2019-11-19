#!/usr/bin/env python3
import sys

from pylib import procs


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
    js_function
  ])
  if __name__ == "__main__":
    exit(result.returncode)


def find_generic_password(label: str) -> str:
  status, pw = procs.run_and_parse_output([
    "security",
    "find-generic-password",
    "-ws",
    label,
  ])
  if status != 0:
    raise Exception("Could not find generic keychain password for label: %s" % label)

  return pw.strip()


def _main():
  result = globals()[sys.argv[1]](*sys.argv[2:])
  if result is not None:
    print(result)


if __name__ == "__main__":
  _main()
