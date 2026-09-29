from pathlib import Path
from enum import Enum, auto


class ApplicationState(Enum):
    CREATED = auto()
    RUNNING = auto()
    PAUSED = auto()



class Application:
    VALID_MODES = {"interactive", "headless"}
    FIXED_DT = 1/120 


    def __init__(self, mode: str, config_path:Path | None):
        if mode not in self.VALID_MODES:
            raise ValueError(
                f"Invalid application mode : {mode!r}."
                f"Expected one of: {', '.join(self.VALID_MODES)}"
            )
        self.mode = mode     
        self.config_path = config_path
        self.simulation_time = 0.0
        self.step_count = 0
        self.state = ApplicationState.CREATED
    def report(self) -> dict | None:
        return {
            "Current effective mode": self.mode,
            "Config file used": str(self.config_path),
            "Simulation time": self.simulation_time,    
            "Step count": self.step_count,
            "state": self.state.name
        }

    def start(self) -> None:
        if self.state is not ApplicationState.CREATED:
            raise RuntimeError("Application cannot be started")
        self.state = ApplicationState.RUNNING
    def pause(self) -> None:
        if self.state is not ApplicationState.RUNNING:
            raise RuntimeError("Application cannot be paused")
        self.state = ApplicationState.PAUSED 
    def resume(self) -> None:
        if self.state is not ApplicationState.PAUSED:
            raise RuntimeError("Application is not paused")
        self.state = ApplicationState.RUNNING     
    def step(self) -> None:
        if self.state is not ApplicationState.RUNNING:
            raise RuntimeError("Cannot step simulation: application is not running")
        self.simulation_time += self.FIXED_DT
        self.step_count += 1 
    def reset(self) -> None:
        self.state = ApplicationState.CREATED
        self.simulation_time = 0.0
        self.step_count = 0
        
            

        
