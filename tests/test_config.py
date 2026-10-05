import pytest 
from src.config import EngineConfig



@pytest.fixture
def  engine_config():
    return EngineConfig()




def test_config_does_exist(engine_config):
    assert engine_config is not None

def test_cylinder_count(engine_config):
    assert engine_config.cylinder_count == 4

def test_bore(engine_config):
    assert engine_config.bore is not None and engine_config.bore > 0
    
def test_stroke(engine_config):
    assert engine_config.stroke is not None and engine_config.stroke > 0

def test_connecting_rod_length(engine_config):
    assert engine_config.connecting_rod_length is not None and engine_config.connecting_rod_length > 0 and engine_config.connecting_rod_length >= engine_config.stroke / 2 

def test_compression_ratio(engine_config):
    assert engine_config.compression_ratio is not None and engine_config.compression_ratio > 0 

def test_crankshaft(engine_config):
    assert engine_config.crankshaft_inertia > 0 

def test_defaults(engine_config):
    assert engine_config.cylinder_count == 4
    assert engine_config.bore > 0
    assert engine_config.stroke > 0
    assert engine_config.connecting_rod_length > engine_config.stroke / 2
    assert engine_config.compression_ratio > 1
    assert engine_config.crankshaft_inertia > 0

def test_invalid_bore():
    with pytest.raises(ValueError, match="Bore"):
        EngineConfig(bore=0)

def test_invalid_stroke():
    with pytest.raises(ValueError, match="Stroke"):
        EngineConfig(stroke=0)

def test_invalid_connecting_rod_length(engine_config):
    with pytest.raises(ValueError, match="Connecting rod length"):
        EngineConfig(connecting_rod_length= engine_config.stroke/2)

def test_invalid_compression_ratio():
    with pytest.raises(ValueError, match="Compression ratio"):
        EngineConfig(compression_ratio=1)
                     
def test_invalid_crankshaft_inertia():
    with pytest.raises(ValueError, match="Crankshaft inertia"):
        EngineConfig(crankshaft_inertia=0)
