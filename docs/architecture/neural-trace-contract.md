# Neural Trace Contract

**Author: Karthikeya**

The dashboard’s Neural Trace panel is backed by `POST /api/v1/neural/trace`. The request contains a bounded feature vector and an optional deterministic seed. The response contains the original features, standardized input values, ordered input/hidden/output layers, every linear layer’s weights and biases, and the final prediction. The TypeScript renderer uses the activation values from this response to set unit color, intensity, tooltip text, and animation timing.

This design separates visualization from model execution. A future registry-backed model can replace the deterministic demonstration fitter without changing the dashboard contract. The current response is intentionally inspectable: a reviewer can compare the displayed prediction with the output activation and inspect the exact matrix values used by each linear layer.

Example request:

```json
{"features": [3, 12, 0.8, 4], "seed": 42}
```

The trace is safe to expose as a public engineering diagnostic because it contains no tenant records and accepts only caller-supplied numeric features. Production model loading should still apply tenant authorization before replacing the demonstration fitter with stored model artifacts.
