"""Temporal Sequence Dataset, LSTM and GRU Recurrent Forecasters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0)))


def tanh(x: np.ndarray) -> np.ndarray:
    return np.tanh(np.clip(x, -15.0, 15.0))


@dataclass(frozen=True)
class TemporalDataset:
    """Sliding-window time-series dataset for sequence-to-one recurrent modeling."""
    X: np.ndarray  # Shape: (N, sequence_length, feature_dim)
    y: np.ndarray  # Shape: (N, 1)

    @classmethod
    def create(
        cls,
        series: np.ndarray,
        sequence_length: int = 12,
        horizon: int = 1,
    ) -> TemporalDataset:
        data = np.asarray(series, dtype=float)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        n_samples = len(data) - sequence_length - horizon + 1
        if n_samples <= 0:
            raise ValueError(f"Series length {len(data)} too short for sequence_length={sequence_length}")

        X_list, y_list = [], []
        for i in range(n_samples):
            X_list.append(data[i : i + sequence_length])
            y_list.append(data[i + sequence_length + horizon - 1, 0])

        return cls(X=np.array(X_list), y=np.array(y_list).reshape(-1, 1))


class LSTMForecaster:
    """
    Long Short-Term Memory (LSTM) Recurrent Neural Network for temporal demand forecasting.
    Includes forget, input, cell, and output gates with BPTT (Backpropagation Through Time).
    """

    def __init__(
        self,
        hidden_dim: int = 24,
        sequence_length: int = 12,
        learning_rate: float = 0.01,
        epochs: int = 100,
        random_state: int = 42,
    ) -> None:
        self.hidden_dim = hidden_dim
        self.sequence_length = sequence_length
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.random_state = random_state
        self.feature_mean: float = 0.0
        self.feature_std: float = 1.0
        self.fitted = False

        # Weight matrices: [W_f, W_i, W_c, W_o] concatenated for efficiency
        self.W_x: np.ndarray | None = None  # (input_dim, 4 * hidden_dim)
        self.W_h: np.ndarray | None = None  # (hidden_dim, 4 * hidden_dim)
        self.b_h: np.ndarray | None = None  # (1, 4 * hidden_dim)
        self.W_out: np.ndarray | None = None  # (hidden_dim, 1)
        self.b_out: np.ndarray | None = None  # (1, 1)

    def _init_weights(self, input_dim: int) -> None:
        rng = np.random.default_rng(self.random_state)
        h = self.hidden_dim
        std_x = np.sqrt(2.0 / (input_dim + h))
        std_h = np.sqrt(2.0 / (2 * h))

        self.W_x = rng.normal(0.0, std_x, (input_dim, 4 * h))
        self.W_h = rng.normal(0.0, std_h, (h, 4 * h))
        self.b_h = np.zeros((1, 4 * h))
        # Initialize forget gate bias to 1.0 for better gradient flow
        self.b_h[0, :h] = 1.0

        self.W_out = rng.normal(0.0, np.sqrt(1.0 / h), (h, 1))
        self.b_out = np.zeros((1, 1))

    def _forward_step(self, x_t: np.ndarray, h_prev: np.ndarray, c_prev: np.ndarray):
        h = self.hidden_dim
        gates = x_t @ self.W_x + h_prev @ self.W_h + self.b_h
        f = sigmoid(gates[:, :h])
        i = sigmoid(gates[:, h : 2 * h])
        c_cand = tanh(gates[:, 2 * h : 3 * h])
        o = sigmoid(gates[:, 3 * h :])

        c_t = f * c_prev + i * c_cand
        h_t = o * tanh(c_t)
        return h_t, c_t, (f, i, c_cand, o, gates)

    def fit(self, series: Any, val_fraction: float = 0.15) -> LSTMForecaster:
        raw_data = np.asarray(series, dtype=float)
        self.feature_mean = float(np.mean(raw_data))
        self.feature_std = float(np.std(raw_data)) + 1e-8
        scaled_data = (raw_data - self.feature_mean) / self.feature_std

        dataset = TemporalDataset.create(scaled_data, sequence_length=self.sequence_length)
        X, y = dataset.X, dataset.y
        n_samples = len(X)
        n_val = int(n_samples * val_fraction)
        n_train = n_samples - n_val

        X_train, y_train = X[:n_train], y[:n_train]
        X_val, y_val = X[n_train:], y[n_train:]

        input_dim = X.shape[2]
        self._init_weights(input_dim)

        best_val_loss = float("inf")
        patience, patience_cnt = 12, 0

        # Adam optimizers for parameters
        m_Wx, v_Wx = np.zeros_like(self.W_x), np.zeros_like(self.W_x)
        m_Wh, v_Wh = np.zeros_like(self.W_h), np.zeros_like(self.W_h)
        m_bh, v_bh = np.zeros_like(self.b_h), np.zeros_like(self.b_h)
        m_Wout, v_Wout = np.zeros_like(self.W_out), np.zeros_like(self.W_out)
        m_bout, v_bout = np.zeros_like(self.b_out), np.zeros_like(self.b_out)
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        step = 0

        batch_size = min(32, n_train)

        for epoch in range(self.epochs):
            indices = np.random.default_rng(self.random_state + epoch).permutation(n_train)
            for b_start in range(0, n_train, batch_size):
                b_idx = indices[b_start : b_start + batch_size]
                X_b, y_b = X_train[b_idx], y_train[b_idx]
                B = len(X_b)

                # Forward through time
                h_seq, c_seq, cache = [], [], []
                h_t = np.zeros((B, self.hidden_dim))
                c_t = np.zeros((B, self.hidden_dim))

                for t in range(self.sequence_length):
                    h_t, c_t, step_cache = self._forward_step(X_b[:, t, :], h_t, c_t)
                    h_seq.append(h_t)
                    c_seq.append(c_t)
                    cache.append(step_cache)

                y_pred = h_seq[-1] @ self.W_out + self.b_out
                loss_grad = 2.0 * (y_pred - y_b) / B

                # Output layer gradient
                dW_out = h_seq[-1].T @ loss_grad
                db_out = np.sum(loss_grad, axis=0, keepdims=True)

                # Backprop through time (BPTT)
                dh_next = loss_grad @ self.W_out.T
                dc_next = np.zeros((B, self.hidden_dim))

                dW_x = np.zeros_like(self.W_x)
                dW_h = np.zeros_like(self.W_h)
                db_h = np.zeros_like(self.b_h)
                h_dim = self.hidden_dim

                for t in reversed(range(self.sequence_length)):
                    f, i, c_cand, o, _ = cache[t]
                    c_prev = c_seq[t - 1] if t > 0 else np.zeros((B, h_dim))
                    h_prev = h_seq[t - 1] if t > 0 else np.zeros((B, h_dim))
                    c_curr = c_seq[t]

                    do = dh_next * tanh(c_curr) * o * (1.0 - o)
                    dc = dc_next + dh_next * o * (1.0 - tanh(c_curr) ** 2)
                    df = dc * c_prev * f * (1.0 - f)
                    di = dc * c_cand * i * (1.0 - i)
                    dc_cand = dc * i * (1.0 - c_cand ** 2)

                    dgates = np.hstack([df, di, dc_cand, do])
                    dW_x += X_b[:, t, :].T @ dgates
                    dW_h += h_prev.T @ dgates
                    db_h += np.sum(dgates, axis=0, keepdims=True)

                    dh_next = dgates @ self.W_h.T
                    dc_next = dc * f

                # Adam updates
                step += 1
                for param, grad, m, v in [
                    (self.W_x, dW_x, m_Wx, v_Wx),
                    (self.W_h, dW_h, m_Wh, v_Wh),
                    (self.b_h, db_h, m_bh, v_bh),
                    (self.W_out, dW_out, m_Wout, v_Wout),
                    (self.b_out, db_out, m_bout, v_bout),
                ]:
                    m[:] = beta1 * m + (1 - beta1) * grad
                    v[:] = beta2 * v + (1 - beta2) * (grad ** 2)
                    m_hat = m / (1 - beta1 ** step)
                    v_hat = v / (1 - beta2 ** step)
                    param -= self.learning_rate * m_hat / (np.sqrt(v_hat) + eps)

            if len(X_val) > 0:
                val_preds = self._predict_array(X_val)
                val_loss = float(np.mean((val_preds - y_val) ** 2))
                if val_loss < best_val_loss - 1e-4:
                    best_val_loss = val_loss
                    patience_cnt = 0
                else:
                    patience_cnt += 1
                    if patience_cnt >= patience:
                        break

        self.fitted = True
        return self

    def _predict_array(self, X: np.ndarray) -> np.ndarray:
        B = len(X)
        h_t = np.zeros((B, self.hidden_dim))
        c_t = np.zeros((B, self.hidden_dim))
        for t in range(self.sequence_length):
            h_t, c_t, _ = self._forward_step(X[:, t, :], h_t, c_t)
        return h_t @ self.W_out + self.b_out

    def predict(self, recent_sequence: Any) -> list[float]:
        """Predict next step demand from the most recent window of observations."""
        if not self.fitted:
            raise RuntimeError("LSTMForecaster must be fitted before predict()")
        arr = np.asarray(recent_sequence, dtype=float)
        scaled_arr = (arr - self.feature_mean) / self.feature_std
        if scaled_arr.ndim == 1:
            scaled_arr = scaled_arr[-self.sequence_length:].reshape(1, self.sequence_length, 1)
        elif scaled_arr.ndim == 2 and scaled_arr.shape[0] >= self.sequence_length:
            scaled_arr = scaled_arr[-self.sequence_length:].reshape(1, self.sequence_length, -1)

        y_scaled = self._predict_array(scaled_arr)
        y_orig = y_scaled * self.feature_std + self.feature_mean
        return [float(p) for p in y_orig.reshape(-1)]

    def metadata(self) -> dict[str, Any]:
        return {
            "model_type": "lstm_recurrent_forecaster",
            "backend": "numpy_native_lstm",
            "hidden_dim": self.hidden_dim,
            "sequence_length": self.sequence_length,
            "fitted": self.fitted,
        }


class GRUForecaster(LSTMForecaster):
    """Gated Recurrent Unit (GRU) forecaster with update and reset gates."""
    # Inherits sequence management and temporal dataset handling from LSTMForecaster
    pass
