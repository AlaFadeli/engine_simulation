from src.config import EngineConfig
import math



class Engine:
    def __init__(self, config: EngineConfig):
        self.config = config 
        
        self.simulation_time = 0.0
        self.step_count = 0
        self.crank_angle = 0.0
        self.angular_velocity = 0.0
        self.torque = 0.0
        self.power = 0.0

    def update(self, dt:float) -> None:
        if dt <= 0:
            raise ValueError("Time step must be positive.")   
        self.simulation_time += dt 
        self.step_count += 1 
        self.crank_angle = (self.crank_angle + self.angular_velocity * dt) % (2 * math.pi) # θ(t) = θ + ωt
        
    def reset(self) -> None:
        self.simulation_time = 0.0
        self.step_count = 0
        self.crank_angle = 0.0
        self.angular_velocity = 0.0
        self.torque = 0.0
        self.power = 0.0
    
    def report(self) -> dict:
        return {
    "simulation_time": self.simulation_time,
    "step_count": self.step_count,
    "crank_angle": self.crank_angle,
    "angular_velocity": self.angular_velocity,
    "rpm": self.angular_velocity * 60 / (2 * math.pi),
    "torque": self.torque,
    "power": self.power,
}
