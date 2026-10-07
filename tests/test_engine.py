import pytest
from src.config import EngineConfig
from src.engine import Engine


@pytest.fixture
def engine():
    return Engine(EngineConfig())

def test_engine_init(engine):
    assert engine.simulation_time == 0.0
    assert engine.step_count == 0
    assert engine.crank_angle == 0.0
    assert engine.angular_velocity == 0.0
    assert engine.torque == 0.0
    assert engine.power == 0.0

def test_engine_step(engine):
    engine.update(0.01)

    assert engine.simulation_time == pytest.approx(0.01)
    assert engine.step_count == 1
    assert engine.crank_angle == pytest.approx(0.0)

def test_engine_rejects_invalid_timestep(engine):
    with pytest.raises(ValueError):
        engine.update(0)

    with pytest.raises(ValueError):
        engine.update(-0.01)

def test_engine_reset(engine):
    engine.update(0.01)
    engine.reset()

    assert engine.simulation_time == 0.0
    assert engine.step_count == 0
    assert engine.crank_angle == 0.0
    assert engine.angular_velocity == 0.0
    assert engine.torque == 0.0
    assert engine.power == 0.0
