"""In-memory repository used by the local modular-monolith mode."""
class ExperimentRepository:
    def __init__(self): self._records = {}
    def save(self, record): self._records[record.experiment_id] = record; return record
    def get(self, experiment_id): return self._records.get(experiment_id)
    def list(self): return list(self._records.values())
