import asyncio
import enum
import subprocess
from argparse import ArgumentParser
from functools import cached_property
from pathlib import Path
from typing import AsyncGenerator, Iterable

import colorama
import toml
from colorama import Fore

from .merge import merge
from .schema import PyProjectSchema

colorama.init()

schema = PyProjectSchema()


class OutputType(enum.Enum):
    STDOUT = enum.auto()
    STDERR = enum.auto()
    TERMINATE = enum.auto()


def parse_config(config_path):
    with Path(config_path).open("r") as fp:
        return schema.deserialize(toml.load(fp))


parser = ArgumentParser()
parser.add_argument("--config", "-c", default="pyproject.toml", type=parse_config)


async def monitor_process(name, process):
    async for output_type, message in merge(
        ((OutputType.STDOUT, line) async for line in process.stdout),
        ((OutputType.STDERR, line) async for line in process.stderr),
    ):
        yield (output_type, name, message.decode("utf-8"))
    # Make sure process is closed, and didn't just close it's STDOUT and STDERR
    await process.wait()
    yield (OutputType.TERMINATE, name, f"Exited: {process.returncode}")


def output_color(output_type):
    if output_type == OutputType.TERMINATE:
        return Fore.YELLOW
    if output_type is OutputType.STDERR:
        return Fore.RED
    return Fore.GREEN


async def _main(config):
    max_name_len = max(map(len, config.commands.keys()))
    processes = [
        monitor_process(
            name,
            await asyncio.create_subprocess_shell(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ),
        )
        for name, command in config.commands.items()
    ]

    fmt_str = "{name} | {line}"

    if config.colorize:
        fmt_str = f"{Fore.CYAN}{{name}} | {{color}}{{line}}{Fore.RESET}"

    async for output_type, process_name, output in merge(*processes):
        for line in output.splitlines():
            print(
                fmt_str.format(
                    name=process_name.ljust(max_name_len),
                    line=line,
                    color=output_color(output_type),
                )
            )


def main():
    args = parser.parse_args()

    asyncio.run(_main(args.config))
