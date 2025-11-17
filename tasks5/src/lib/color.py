from __future__ import annotations

import sys
from typing import Literal

from colorama import Fore, Style, init as colorama_init


# Initialize colorama for Windows ANSI support; autoreset to simplify usage
colorama_init(autoreset=True)

Urgency = Literal["overdue", "soon", "later", "none"]


def supports_color(stream=None) -> bool:
    stream = stream or sys.stdout
    return hasattr(stream, "isatty") and stream.isatty()


def color_for(urgency: Urgency) -> str:
    if urgency == "overdue":
        return Fore.RED
    if urgency == "soon":
        return Fore.YELLOW
    # later/none
    return Fore.WHITE


def colorize(text: str, urgency: Urgency, enable: bool) -> str:
    if not enable:
        return text
    return f"{color_for(urgency)}{text}{Style.RESET_ALL}"
