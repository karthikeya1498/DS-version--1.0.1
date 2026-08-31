"""Multi-Layer Perceptron (MLP) Neural Forecaster with layer activation inspection."""
from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, x)


def relu_grad(x: np.ndarray) -> np.ndarray:
    return (x > 0.0).astype(float)


class MLPForecaster:
    """
    Neural Multi-Layer Perceptron for regression.
    Includes Adam optimizer, early stopping, and layer activation capture for inspection/UI.
    """

    def __init__(
        self,
        hidden_dims: Sequence[int] = (32, 16),
        learning_rate: float = 0.01,
        epochs: int = 150,
        batch_size: int = 32,
        random_state: int = 42,
    ) -> None:
        self.hidden_dims = tuple(hidden_dims)
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.random_state = random_state
        self.weights: list[np.ndarray] = []
        self.biases: list[np.ndarray] = []
        self.feature_mean: np.ndarray | None = None
        self.feature_std: np.ndarray | None = None
        self.target_mean: float = 0.0
        self.target_std: float = 1.0
        self.fitted = False

    def _init_weights(self, input_dim: int) -> None:
        rng = np.random.default_rng(self.random_state)
        dims = [input_dim, *self.hidden_dims, 1]
        self.weights = []
        self.biases = []
        for in_d, out_d in zip(dims[:-1], dims[1:]):
            # He / Xavier initialization
            std = np.sqrt(2.0 / in_d)
            self.weights.append(rng.normal(0.0, std, (in_d, out_d)))
            self.biases.append(np.zeros((1, out_d)))

    def fit(self, X: Any, y: Any, val_split: float = 0.15) -> MLPForecaster:
        x_mat = np.asarray(X, dtype=float)
        y_vec = np.asarray(y, dtype=float).reshape(-1, 1)

        # Scale features and targets fitted strictly on training data
        self.feature_mean = np.mean(x_mat, axis=0)
        self.feature_std = np.std(x_mat, axis=0) + 1e-8
        x_scaled = (x_mat - self.feature_mean) / self.feature_std

        self.target_mean = float(np.mean(y_vec))
        self.target_std = float(np.std(y_vec)) + 1e-8
        y_scaled = (y_vec - self.target_mean) / self.target_std

        input_dim = x_mat.shape[1]
        self._init_weights(input_dim)

        n_samples = len(x_scaled)
        n_val = int(n_samples * val_split)
        n_train = n_samples - n_val

        x_train, y_train = x_scaled[:n_train], y_scaled[:n_train]
        x_val, y_val = x_scaled[n_train:], y_scaled[n_train:]

        # Adam momentum and variance state
        m_w = [np.zeros_like(w) for w in self.weights]
        v_w = [np.zeros_like(w) for w in self.weights]
        m_b = [np.zeros_like(b) for b in self.biases]
        v_b = [np.zeros_like(b) for b in self.biases]
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        t = 0

        best_loss = float("inf")
        patience, patience_cnt = 15, 0

        for epoch in range(self.epochs):
            indices = np.random.default_rng(self.random_state + epoch).permutation(n_train)
            for start in range(0, n_train, self.batch_size):
                batch_idx = indices[start : start + self.batch_size]
                xb, yb = x_train[batch_idx], y_train[batch_idx]

                # Forward pass
                activations = [xb]
                zs = []
                for i in range(len(self.weights) - 1):
                    z = activations[-1] @ self.weights[i] + self.biases[i]
                    zs.append(z)
                    activations.append(relu(z))
                # Output linear layer
                z_out = activations[-1] @ self.weights[-1] + self.biases[-1]
                zs.append(z_out)
                activations.append(z_out)

                # Backward pass
                t += 1
                error = (activations[-1] - yb) / len(xb)
                delta = error

                dw_list = []
                db_list = []

                for i in range(len(self.weights) - 1, -1, -1):
                    dw = activations[i].T @ delta
                    db = np.sum(delta, axis=0, keepdims=True)
                    dw_list.append(dw)
                    db_list.append(db)
                    if i > 0:
                        delta = (delta @ self.weights[i].T) * relu_grad(zs[i - 1])

                dw_list.reverse()
                db_list.reverse()

                # Adam updates
                for i in range(len(self.weights)):
                    m_w[i] = beta1 * m_w[i] + (1 - beta1) * dw_list[i]
                    v_w[i] = beta2 * v_w[i] + (1 - beta2) * (dw_list[i] ** 2)
                    m_b[i] = beta1 * m_b[i] + (1 - beta1) * db_list[i]
                    v_b[i] = beta2 * v_b[i] + (1 - beta2) * (db_list[i] ** 2)

                    m_w_hat = m_w[i] / (1 - beta1 ** t)
                    v_w_hat = v_w[i] / (1 - beta2 ** t)
                    m_b_hat = m_b[i] / (1 - beta1 ** t)
                    v_b_hat = v_b[i] / (1 - beta2 ** t)

                    self.weights[i] -= self.learning_rate * m_w_hat / (np.sqrt(v_w_hat) + eps)
                    self.biases[i] -= self.learning_rate * m_b_hat / (np.sqrt(v_b_hat) + eps)

            if len(x_val) > 0:
                val_preds = self._predict_scaled(x_val)
                val_loss = float(np.mean((val_preds - y_val) ** 2))
                if val_loss < best_loss - 1e-4:
                    best_loss = val_loss
                    patience_cnt = 0
                else:
                    patience_cnt += 1
                    if patience_cnt >= patience:
                        break

        self.fitted = True
        return self

    def _predict_scaled(self, x_scaled: np.ndarray) -> np.ndarray:
        act = x_scaled
        for i in range(len(self.weights) - 1):
            act = relu(act @ self.weights[i] + self.biases[i])
        return act @ self.weights[-1] + self.biases[-1]

    def predict(self, X: Any) -> list[float]:
        if not self.fitted:
            raise RuntimeError("MLPForecaster must be fitted before predict()")
        x_mat = np.asarray(X, dtype=float)
        x_scaled = (x_mat - self.feature_mean) / self.feature_std
        y_scaled = self._predict_scaled(x_scaled)
        y_orig = y_scaled * self.target_std + self.target_mean
        return [float(p) for p in y_orig.reshape(-1)]

    def get_layer_activations(self, X: Any) -> list[list[float]]:
        """
        Inspect intermediate layer activations for a single sample or batch.
        Returns activations across input -> hidden1 -> hidden2 -> output.
        Enables interactive neural network visualization!
        """
        if not self.fitted:
            raise RuntimeError("MLPForecaster must be fitted")
        x_mat = np.asarray(X, dtype=float).reshape(1, -1)
        x_scaled = (x_mat - self.feature_mean) / self.feature_std

        activations: list[list[float]] = [x_scaled[0].tolist()]
        act = x_scaled
        for i in range(len(self.weights) - 1):
            act = relu(act @ self.weights[i] + self.biases[i])
            activations.append(act[0].tolist())
        out = act @ self.weights[-1] + self.biases[-1]
        out_orig = out * self.target_std + self.target_mean
        activations.append(out_orig[0].tolist())
        return activations

    def metadata(self) -> dict[str, Any]:
        return {
            "model_type": "mlp_neural_forecaster",
            "backend": "numpy_native_neural",
            "hidden_dims": self.hidden_dims,
            "learning_rate": self.learning_rate,
            "fitted": self.fitted,
        }
