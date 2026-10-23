import pytest
import math
from src.crankshaft import Crankshaft, CrankshaftState


@pytest.fixture
def crankshaft():
    return Crankshaft(inertia=0.1)


class TestCrankshaftInitialization:
    def test_init_with_valid_inertia(self, crankshaft):
        assert crankshaft.inertia == 0.1
        assert crankshaft.state.angle == 0.0
        assert crankshaft.state.angular_velocity == 0.0
        assert crankshaft.state.angular_acceleration == 0.0

    def test_init_rejects_zero_inertia(self):
        with pytest.raises(ValueError, match="Inertia"):
            Crankshaft(inertia=0.0)

    def test_init_rejects_negative_inertia(self):
        with pytest.raises(ValueError, match="Inertia"):
            Crankshaft(inertia=-0.1)

    def test_init_rejects_nan_inertia(self):
        with pytest.raises(ValueError, match="Inertia"):
            Crankshaft(inertia=float("nan"))

    def test_init_rejects_infinite_inertia(self):
        with pytest.raises(ValueError, match="Inertia"):
            Crankshaft(inertia=float("inf"))


class TestCrankshaftUpdate:
    def test_zero_torque_keeps_velocity_zero(self, crankshaft):
        crankshaft.update(dt=0.01, applied_torque=0.0)
        assert crankshaft.state.angular_velocity == 0.0
        assert crankshaft.state.angular_acceleration == 0.0
        assert crankshaft.state.angle == 0.0

    def test_positive_torque_increases_angular_velocity(self, crankshaft):
        crankshaft.update(dt=0.01, applied_torque=10.0)
        expected_acceleration = 10.0 / 0.1
        assert crankshaft.state.angular_acceleration == pytest.approx(expected_acceleration)
        assert crankshaft.state.angular_velocity == pytest.approx(expected_acceleration * 0.01)

    def test_negative_torque_decreases_angular_velocity(self, crankshaft):
        crankshaft.update(dt=0.01, applied_torque=10.0)  # spin up first
        v1 = crankshaft.state.angular_velocity
        crankshaft.update(dt=0.01, applied_torque=-10.0)
        v2 = crankshaft.state.angular_velocity
        assert v2 < v1

    def test_angle_wraps_at_2pi(self, crankshaft):
        # spin fast enough to exceed 2π in one step
        crankshaft.update(dt=1.0, applied_torque=100.0)
        assert 0.0 <= crankshaft.state.angle < 2 * math.pi

    def test_update_rejects_zero_dt(self, crankshaft):
        with pytest.raises(ValueError, match="dt"):
            crankshaft.update(dt=0.0, applied_torque=1.0)

    def test_update_rejects_negative_dt(self, crankshaft):
        with pytest.raises(ValueError, match="dt"):
            crankshaft.update(dt=-0.01, applied_torque=1.0)

    def test_update_rejects_nan_dt(self, crankshaft):
        with pytest.raises(ValueError, match="dt"):
            crankshaft.update(dt=float("nan"), applied_torque=1.0)

    def test_update_rejects_infinite_dt(self, crankshaft):
        with pytest.raises(ValueError, match="dt"):
            crankshaft.update(dt=float("inf"), applied_torque=1.0)

    def test_update_rejects_nan_torque(self, crankshaft):
        with pytest.raises(ValueError, match="torque"):
            crankshaft.update(dt=0.01, applied_torque=float("nan"))

    def test_update_rejects_infinite_torque(self, crankshaft):
        with pytest.raises(ValueError, match="torque"):
            crankshaft.update(dt=0.01, applied_torque=float("inf"))


class TestCrankshaftReset:
    def test_reset_restores_state_to_zero(self, crankshaft):
        crankshaft.update(dt=0.01, applied_torque=10.0)
        crankshaft.reset()
        assert crankshaft.state.angle == 0.0
        assert crankshaft.state.angular_velocity == 0.0
        assert crankshaft.state.angular_acceleration == 0.0

    def test_reset_preserves_inertia(self, crankshaft):
        crankshaft.reset()
        assert crankshaft.inertia == 0.1


class TestCrankshaftReport:
    def test_report_returns_correct_fields(self, crankshaft):
        crankshaft.update(dt=0.01, applied_torque=10.0)
        report = crankshaft.report()
        assert "angle" in report
        assert "angular_velocity" in report
        assert "angular_acceleration" in report
        assert "rpm" in report

    def test_rpm_matches_angular_velocity(self, crankshaft):
        crankshaft.update(dt=0.01, applied_torque=10.0)
        report = crankshaft.report()
        expected_rpm = crankshaft.state.angular_velocity * 60 / (2 * math.pi)
        assert report["rpm"] == pytest.approx(expected_rpm)