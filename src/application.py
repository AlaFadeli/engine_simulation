from pathlib import Path

class Application:
    VALID_MODES = {"interactive", "headless"}


    def __init__(self, mode: str, config_path:Path | None):
        if mode not in self.VALID_MODES:
            raise ValueError(
                f"Invalid application mode : {mode!r}."
                f"Expected one of: {', '.join(self.VALID_MODES)}"
            )
        self.mode = mode     
        self.config_path = config_path
        self.running = False
        self.paused = False
        self.simulation_time = 0.0
        self.step_count = 0

    def status(self):
        return {
            "Current effective mode": self.mode,
            "Config file used": str(self.config_path),
            "running": self.running,
            "paused": self.paused,
            "Simulation time": self.simulation_time,    
            "Step count": self.step_count
        }

