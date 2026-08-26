from datetime import UTC, timedelta

from src.simulation.models import SimulationConfig, TimeWindow
from src.simulation.simulator import LogisticsSimulator


def test_simulator_is_reproducible():
    config = SimulationConfig(
        seed=7, zones=3, vehicles=4, orders_per_hour=3, duration=timedelta(hours=1)
    )
    first = LogisticsSimulator(config).run()
    second = LogisticsSimulator(config).run()
    assert first.to_summary() == second.to_summary()
    assert [o.status for o in first.orders] == [o.status for o in second.orders]


def test_domain_validation_rejects_invalid_time_window():
    from datetime import datetime

    now = datetime.now(UTC)
    try:
        TimeWindow(now, now)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid time window was accepted")
