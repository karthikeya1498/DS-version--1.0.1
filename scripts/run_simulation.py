from datetime import timedelta
from src.simulation.models import SimulationConfig
from src.simulation.simulator import LogisticsSimulator
if __name__ == '__main__': print(LogisticsSimulator(SimulationConfig(duration=timedelta(hours=2))).run().to_summary())
