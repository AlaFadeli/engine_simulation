from pathlib import Path
from enum import Enum, auto
import time 
import threading

class ApplicationState(Enum):
    CREATED = auto()
    RUNNING = auto()
    PAUSED = auto()
class SimulationMode(Enum):
    DISCRETE = auto()
    CONTINUOUS = auto()



class Application:
    VALID_APPLICATION_MODES = {"interactive", "headless"}
    FIXED_DT = 1/120 
    MAX_FRAME_DT = 0.25

    def __init__(self, mode: str, config_path:Path | None):
        if mode not in self.VALID_APPLICATION_MODES:
            raise ValueError(
                f"Invalid application mode : {mode!r}."
                f"Expected one of: {', '.join(self.VALID_APPLICATION_MODES)}"
            )
        self.application_mode = mode     
        self.config_path = config_path
        self.simulation_time = 0.0
        self.step_count = 0
        self.state = ApplicationState.CREATED
        self.simulation_mode = SimulationMode.CONTINUOUS 
        self.start_time = 0.0
        self.accumulator = 0.0
        self.simulation_thread = None
        self.stop_event = threading.Event()
        
    def report(self) -> dict :
        return {
            "Current effective mode": self.application_mode,
            "Config file used": str(self.config_path),
            "Simulation time": self.simulation_time,    
            "Step count": self.step_count,
            "state": self.state.name
        }

    def start(self) -> None:
        if self.state is not ApplicationState.CREATED:
            raise RuntimeError("Application cannot be started")   
        self.start_time = time.monotonic()
        self.state = ApplicationState.RUNNING
        if self.simulation_mode is not SimulationMode.CONTINUOUS:
            return
        self.stop_event.clear()
        self.simulation_thread = threading.Thread(
            target=self.run_continuous_loop
        )
        self.simulation_thread.start()

    def pause(self) -> None:
        if self.state is not ApplicationState.RUNNING:
            raise RuntimeError("Application cannot be paused")
        self.state = ApplicationState.PAUSED 
        if self.simulation_thread is not None and self.simulation_thread is not threading.current_thread():
            self.stop_event.set() 
            self.simulation_thread.join()
        self.simulation_thread = None 
        self.stop_event.clear()
    def resume(self) -> None:
        if self.state is not ApplicationState.PAUSED:
            raise RuntimeError("Application is not paused")
        self.state = ApplicationState.RUNNING     
        if self.simulation_mode is not SimulationMode.CONTINUOUS:
            return 
        self.start_time = time.monotonic()
        self.accumulator = 0.0
        self.stop_event.clear()
        self.simulation_thread = threading.Thread(
            target=self.run_continuous_loop
        )
        self.simulation_thread.start()
    def step(self) -> None:
        if self.state is not ApplicationState.RUNNING:
            raise RuntimeError("Cannot step simulation: application is not running")
        self.simulation_time += self.FIXED_DT
        self.step_count += 1 
    def reset(self) -> None:
        self.stop_event.set()
        self.state = ApplicationState.CREATED
        if self.simulation_thread is not None and self.simulation_thread is not threading.current_thread():
            self.simulation_thread.join()
        self.simulation_thread = None 
        self.stop_event.clear()

        self.simulation_time = 0.0
        self.step_count = 0
        self.accumulator = 0.0

    def run_continuous_loop(self) -> None:
        if self.simulation_mode == SimulationMode.DISCRETE:
            return

        previous_time = self.start_time

        while self.state == ApplicationState.RUNNING and not self.stop_event.is_set():
            current_time = time.monotonic()
            dt = current_time - previous_time

            if dt > self.MAX_FRAME_DT:
                dt = self.MAX_FRAME_DT
            
            self.accumulator += dt
            previous_time = current_time
            while self.accumulator >= self.FIXED_DT:
                self.step()
                self.accumulator -= self.FIXED_DT
