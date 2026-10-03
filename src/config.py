from dataclasses import dataclass



@dataclass(frozen=True)
class EngineConfig:
    """Configuration for the engine."""
    cylinder_count: int = 4
    bore: float = 0.084
    stroke: float = 0.090
    connecting_rod_length: float = 0.150
    compression_ratio: float = 10.5
    crankshaft_inertia: float = 0.12
    
    def __post_init__(self) -> None:
        if (not isinstance(self.cylinder_count, int)
            or isinstance(self.cylinder_count, bool)
            or self.cylinder_count <= 0): 
            raise ValueError("Cylinder count must be a positive integer.")
            
        if self.bore <= 0:
            raise ValueError("Bore must be a positive float.")
        if self.stroke <= 0:
            raise ValueError("Stroke must be a positive float.")
        if self.connecting_rod_length <= self.stroke / 2:
            raise ValueError("Connecting rod length must be greater than half the stroke (geometric constraint).")
        if self.compression_ratio <= 1:
            raise ValueError("Compression ratio must be strictly greater than 1.")
        if self.crankshaft_inertia <= 0:
            raise ValueError("Crankshaft inertia must be strictly greater than 0.")


