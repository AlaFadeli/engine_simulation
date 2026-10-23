from dataclasses import dataclass 
import math


@dataclass 
class CrankshaftState:
    angle: float 
    angular_velocity: float 
    angular_acceleration: float 


class Crankshaft:
    def __init__(self, inertia:float):
        
        self.state = CrankshaftState(
            angle=0.0,
            angular_velocity=0.0,
            angular_acceleration=0.0
        )
        self.inertia = inertia
        if not math.isfinite(self.inertia) or self.inertia <= 0:
            raise ValueError("Inertia cannot be less or equal to zero and must be finite")


    def update(self, dt:float, applied_torque:float) -> None:
        if not math.isfinite(applied_torque):
            raise ValueError("Applied torque must be finite")
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError(" dt must be positive and finite ")
        
        self.state.angular_acceleration = applied_torque / self.inertia
        self.state.angular_velocity += self.state.angular_acceleration * dt
        self.state.angle = (self.state.angle + self.state.angular_velocity * dt) % (2 * math.pi)

            
    def reset(self) -> None:
        self.state = CrankshaftState(0.0, 0.0, 0.0)


    def report(self):
        rpm = self.state.angular_velocity * 60 / (2 *  math.pi)
        return {
            "angle": self.state.angle,
            "angular_velocity": self.state.angular_velocity,
            "angular_acceleration": self.state.angular_acceleration,
            "rpm": rpm
        }



