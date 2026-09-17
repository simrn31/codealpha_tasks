"""
Task 3: Music Generation with AI - Generation
--------------------------------------------------
Loads the trained model and vocabulary, seeds it with a random sequence
taken from the training data, then repeatedly predicts the next
note/chord and feeds each prediction back in to build a brand-new
sequence. Converts the result into a real MIDI file using music21.

Run:
    python generate.py

Output:
    data/generated_output.mid — open with Windows Media Player, VLC,
    or any DAW to listen to it.
"""

import pickle
from pathlib import Path

import numpy as np
from tensorflow.keras.models import load_model
from music21 import stream, note, chord, instrument

DATA_DIR = Path(__file__).parent / "data"
SEQUENCE_LENGTH = 50
GENERATE_LENGTH = 200  # number of notes/chords to generate


def build_input_sequences(tokens, vocab):
    token_to_int = {t: i for i, t in enumerate(vocab)}
    network_input = []
    for i in range(len(tokens) - SEQUENCE_LENGTH):
        seq_in = tokens[i:i + SEQUENCE_LENGTH]
        network_input.append([token_to_int[t] for t in seq_in])
    return network_input


def generate_tokens(model, network_input, vocab):
    int_to_token = {i: t for i, t in enumerate(vocab)}
    n_vocab = len(vocab)

    start = np.random.randint(0, len(network_input) - 1)
    pattern = list(network_input[start])

    output = []
    for _ in range(GENERATE_LENGTH):
        x = np.reshape(pattern, (1, len(pattern), 1)) / float(n_vocab)
        prediction = model.predict(x, verbose=0)
        index = int(np.argmax(prediction))
        output.append(int_to_token[index])
        pattern.append(index)
        pattern = pattern[1:]

    return output


def tokens_to_midi(tokens, out_path):
    offset = 0.0
    output_notes = []

    for token in tokens:
        if token == "REST":
            offset += 0.5
            continue

        if "." in token:  # a chord, stored as full pitch names e.g. "C4.E4.G4"
            pitch_names = token.split(".")
            chord_notes = [note.Note(p) for p in pitch_names]
            for n in chord_notes:
                n.storedInstrument = instrument.Piano()
            new_chord = chord.Chord(chord_notes)
            new_chord.offset = offset
            output_notes.append(new_chord)
        else:  # a single note, stored as a pitch name e.g. "C4"
            new_note = note.Note(token)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        offset += 0.5

    midi_stream = stream.Stream(output_notes)
    midi_stream.write("midi", fp=str(out_path))
    print(f"Saved generated music to {out_path}")


def main():
    with open(DATA_DIR / "notes.pkl", "rb") as f:
        tokens = pickle.load(f)
    with open(DATA_DIR / "vocab.pkl", "rb") as f:
        vocab = pickle.load(f)

    network_input = build_input_sequences(tokens, vocab)
    model = load_model(DATA_DIR / "model_final.keras")

    generated = generate_tokens(model, network_input, vocab)
    tokens_to_midi(generated, DATA_DIR / "generated_output.mid")


if __name__ == "__main__":
    main()
