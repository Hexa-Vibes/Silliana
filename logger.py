# (C) 2025 Hexa Vibes. Licensed under the MIT License.

from datetime import datetime
import sys

class Logger:
  prefix = ""

  def __init__(self, prefix="MISC"):
    self.prefix = prefix

  def time(self):
    now = datetime.now()
    time = now.strftime("%d.%m.%Y %H:%M:%S")
    return time

  def info(self, message):
    print(f"{self.time()} {self.prefix}.INF: {message}", file=sys.stdout)

  def error(self, message):
    print(f"{self.time()} {self.prefix}.ERR: {message}", file=sys.stderr)

  def warn(self, message):
    print(f"{self.time()} {self.prefix}.WAR: {message}", file=sys.stderr)
