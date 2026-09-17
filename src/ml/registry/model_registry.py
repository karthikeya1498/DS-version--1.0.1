"""Small model registry for reproducible Phase 2 artifacts."""
from __future__ import annotations

import json
from pathlib import Path


class ModelRegistry:
    def __init__(self, root: str | Path = 'models'):
        self.root = Path(root); self._models = {}
    def register(self, name, model, metadata=None):
        record = {'model': model, 'metadata': metadata or {}}; self._models[name] = record
        artifact = self.root / name; artifact.parent.mkdir(parents=True, exist_ok=True); (artifact.with_suffix('.json')).write_text(json.dumps(record['metadata'], indent=2, default=str), encoding='utf-8')
        return record['metadata']
    def get(self, name): return self._models[name]['model']
    def metadata(self, name): return self._models[name]['metadata']
    def names(self): return tuple(sorted(self._models))
