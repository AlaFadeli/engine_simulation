import argparse
import json
from pathlib import Path
from src.application import Application

def valid_config_file(value: str) -> Path:
    path = Path(value)

    if not path.is_file():
        raise argparse.ArgumentTypeError(
            f"config file does not exist: {path}"
        )
    return path

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Automotive engine simulator"
    )

    parser.add_argument(
        "--config",
        type=valid_config_file,
        help="Path to the engine configuration file",
    )

    mode = parser.add_mutually_exclusive_group()

    mode.add_argument(
        "--interactive",
        action="store_const",
        const="interactive",
        dest="mode",
        help="Run the simulator in interactive mode.",
    )
    mode.add_argument(
        "--headless",
        action="store_const",
        const="headless",
        dest="mode",
        help="Run the simulator in headless mode.",
    )
    parser.set_defaults(mode="headless")

    return parser

def parse_command(user_input: str) -> tuple[str, list[str]] | None:
    parts = user_input.split()
    if not parts:
        return None

    command = parts[0].lower()
    arguments = parts[1:]
    return command, arguments

def handle_help(application: Application, arguments: list[str]) -> bool:
    print(
        "Available commands:\n"
        "  help              Show this help message\n"
        "  start             Start the simulation\n"
        "  pause             Pause the simulation\n"
        "  resume            Resume the simulation\n"
        "  step              Advance one fixed simulation step\n"
        "  report            Show current application state\n"
        "  reset             Reset simulation runtime state\n"
        "  exit              Exit the simulator\n"
        "  quit              Exit the simulator\n"
        "\n"
        "Commands accept no arguments."
    )
    return False

def handle_start(application: Application, arguments: list[str]) -> bool:
    application.start()
    return False

def handle_pause(application: Application, arguments: list[str]) -> bool:
    application.pause()
    return False

def handle_resume(application: Application, arguments: list[str]) -> bool:
    application.resume()
    return False

def handle_step(application: Application, arguments: list[str]) -> bool:
    application.step()
    return False

def handle_report(application: Application, arguments: list[str]) -> bool:
    print(json.dumps(application.report(), indent=4))
    return False

def handle_reset(application: Application, arguments: list[str]) -> bool:
    application.reset()
    return False

def handle_exit(application: Application, arguments: list[str]) -> bool:
    return True

COMMAND_HANDLERS = {
    "help": handle_help,
    "start": handle_start,
    "pause": handle_pause,
    "resume": handle_resume,
    "step": handle_step,
    "report": handle_report,
    "reset": handle_reset,
    "exit": handle_exit,
    "quit": handle_exit,
}


def dispatch_command(
    command: str,
    arguments: list[str],
    application: Application,
) -> bool:
    handler = COMMAND_HANDLERS.get(command)
    if handler is None:
        print(f"Unknown command: {command}")
        return False

    return handler(application, arguments)

def run_interactive_loop(application: Application) -> None:
    while True:
        try:
            user_input = input("> ")
        except EOFError:
            break

        parsed = parse_command(user_input)
        if parsed is None:
            continue

        command, arguments = parsed
        try:
            should_exit = dispatch_command(command, arguments, application)
        except RuntimeError as error:
            print(f"Error: {error}")
            continue

        if should_exit:
            break

def run() -> None:
    parser = build_parser()
    args = parser.parse_args()

    application = Application(
        mode=args.mode,
        config_path=args.config,
    )

    startup_message = (
        "Automotive Engine Simulator\n"
        "===========================\n"
        "Initializing simulation..."
    )

    print(startup_message)
    if args.mode == "interactive":
        run_interactive_loop(application)
