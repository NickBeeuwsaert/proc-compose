from dataclasses import dataclass


@dataclass
class ProcComposeConfig:
    commands: dict[str, str]
    colorize: bool
