import argparse
from pathlib import Path


def valid_config_file(value:str) -> Path:
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
        help="Run the simulator in interactive mode."
    )
    mode.add_argument(
        "--headless",
        action="store_const",
        const="headless",
        dest="mode",
        help="Run the simulator in headless mode."
    )
    parser.set_defaults(mode="headless")

    return parser 

def run() -> None:
    parser = build_parser()
    args = parser.parse_args()
        
    startup_message = "Automotive Engine Simulator \n===========================\nInitializing simulation..."
        


    print(startup_message)
    if args.config is not None:
        print(f"Config File used: {args.config}")
    print(f"Mode: {args.mode}")
