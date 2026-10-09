import pytest

from src.application import Application, ApplicationState

@pytest.fixture
def application():
    return Application(
        mode="interactive",
        config_path=None,
    )

def test_application_initial_state(application):
    assert application.state is ApplicationState.CREATED
    assert application.application_mode == "interactive"
    assert application.config_path is None
    assert application.simulation_time == 0.0
    assert application.step_count == 0
    assert application.accumulator == 0.0

def test_application_start(application):
    application.start()

    assert application.state is ApplicationState.RUNNING

def test_application_pause(application):
    application.start()
    application.pause()

    assert application.state is ApplicationState.PAUSED

def test_application_resume(application):
    application.start()
    application.pause()
    application.resume()

    assert application.state is ApplicationState.RUNNING

def test_application_reset(application):
    application.start()
    application.step()
    application.reset()
    assert application.state is ApplicationState.CREATED
    assert application.simulation_time == 0.0
    assert application.step_count == 0
    assert application.accumulator == 0.0

def test_application_invalid_transitions(application):
    with pytest.raises(RuntimeError):
        application.pause()
    application.start()
    with pytest.raises(RuntimeError):
        application.resume()

def test_application_step_updates_engine(application):
    application.start()
    application.step()
    assert application.simulation_time == pytest.approx(application.FIXED_DT)
    assert application.step_count == 1
    assert application.engine.simulation_time == pytest.approx(application.FIXED_DT)
    assert application.engine.step_count == 1
