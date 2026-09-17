"""
Task 3: Music Generation with AI - Model training
-----------------------------------------------------
Loads the tokens created by preprocess.py, turns them into fixed-length
input sequences, and trains a stacked LSTM to predict the next note/chord
given the previous SEQUENCE_LENGTH tokens (classic next-token prediction,
the same idea as text generation but with musical tokens).

Run:
    python train.py

Note: training on CPU can take a while. EPOCHS is kept modest here for
a demo-sized run — raise it (and/or add more chorales in preprocess.py)
for noticeably better output quality if you have time before recording.
"""

import pickle
from pathlib import Path

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Activation, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.utils import to_categorical

DATA_DIR = Path(__file__).parent / "data"
SEQUENCE_LENGTH = 50
EPOCHS = 50
BATCH_SIZE = 64


def prepare_sequences(tokens, vocab):
    token_to_int = {t: i for i, t in enumerate(vocab)}
    n_vocab = len(vocab)

    network_input = []
    network_output = []
    for i in range(len(tokens) - SEQUENCE_LENGTH):
        seq_in = tokens[i:i + SEQUENCE_LENGTH]
        seq_out = tokens[i + SEQUENCE_LENGTH]
        network_input.append([token_to_int[t] for t in seq_in])
        network_output.append(token_to_int[seq_out])

    n_patterns = len(network_input)
    X = np.reshape(network_input, (n_patterns, SEQUENCE_LENGTH, 1))
    X = X / float(n_vocab)  # normalize inputs to 0-1
    y = to_categorical(network_output, num_classes=n_vocab)
    return X, y, n_vocab


def build_model(input_shape, n_vocab):
    model = Sequential([
        LSTM(256, input_shape=input_shape, return_sequences=True),
        Dropout(0.3),
        LSTM(256),
        BatchNormalization(),
        Dropout(0.3),
        Dense(128),
        Activation("relu"),
        Dense(n_vocab),
        Activation("softmax"),
    ])
    model.compile(loss="categorical_crossentropy", optimizer="adam")
    return model


def main():
    with open(DATA_DIR / "notes.pkl", "rb") as f:
        tokens = pickle.load(f)
    with open(DATA_DIR / "vocab.pkl", "rb") as f:
        vocab = pickle.load(f)

    X, y, n_vocab = prepare_sequences(tokens, vocab)
    print(f"Training on {X.shape[0]} sequences, vocabulary size {n_vocab}")

    model = build_model((X.shape[1], X.shape[2]), n_vocab)
    model.summary()

    checkpoint = ModelCheckpoint(
        str(DATA_DIR / "model_checkpoint.keras"),
        monitor="loss",
        save_best_only=True,
    )
    model.fit(X, y, epochs=EPOCHS, batch_size=BATCH_SIZE, callbacks=[checkpoint])

    model.save(DATA_DIR / "model_final.keras")
    print(f"\nModel saved to {DATA_DIR}/model_final.keras")


if __name__ == "__main__":
    main()
