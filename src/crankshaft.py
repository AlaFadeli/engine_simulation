from dataclasses import dataclass 

@dataclass 
class CrankshaftState:
    angle: float 
    angular_velocity: float 
    angular_acceleration: float 


class Crankshaft:
    def __init__(self, inertia:float, ):
        self.state = CrankshaftState
        self.intertia = inertia


