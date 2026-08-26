"""Minimal model registry interface with deterministic local storage."""
class ModelRegistry:
    def __init__(self): self._models = {}
    def register(self, name, model, metadata=None): self._models[name] = {'model': model, 'metadata': metadata or {}}
    def get(self, name): return self._models[name]['model']
    def names(self): return tuple(sorted(self._models))
