# Music Generation with AI (AI Internship - Task 3)

An LSTM neural network that learns musical patterns from Bach chorales
and generates a brand-new note/chord sequence, saved as a playable MIDI
file.

## ⚠️ Before you run this
This project needs `music21` and `tensorflow`, and training an LSTM
takes real time (minutes to an hour+ depending on your laptop's CPU and
how many chorales/epochs you use). Unlike Task 1 and Task 2, **this
code hasn't been run and tested end-to-end for you** — it's written
following the standard, well-established approach for this kind of
project, but you'll be doing the first real test run. Start with
`preprocess.py` alone first to confirm music21 and its corpus work on
your machine before committing to a full training run.

## How it fulfills the task requirements

| Requirement | Where it's done |
|---|---|
| Collect MIDI music data (classical, jazz etc.) | `preprocess.py` — uses `music21`'s **built-in** Bach chorale corpus, so no external MIDI download is needed |
| Preprocess into note sequences (e.g. `music21`) | `preprocess.py` — extracts every note/chord as a token using `music21` |
| Build a deep learning model (RNN/LSTM) | `train.py` — a stacked LSTM (2 layers, 256 units each) built with Keras/TensorFlow |
| Train the model to generate new sequences | `train.py` — trains on next-token prediction over sliding windows of 50 tokens |
| Convert generated sequences to MIDI and play/save as audio | `generate.py` — samples a new sequence from the trained model and writes `generated_output.mid` |

## Project structure
```
music_generator/
├── preprocess.py     # Extract notes/chords from music21's Bach corpus
├── train.py            # Build & train the LSTM, save the trained model
├── generate.py          # Generate a new sequence, save as MIDI
├── requirements.txt
├── .gitignore
├── README.md
└── data/                # Created automatically — holds .pkl/.keras files + output
```

## Setup & run

```bash
pip install -r requirements.txt

# Step 1: extract notes/chords from the built-in Bach corpus
python preprocess.py

# Step 2: train the LSTM (this is the slow part — grab a coffee)
python train.py

# Step 3: generate a new piece and save it as MIDI
python generate.py
```

The final output is `data/generated_output.mid` — open it with **Windows
Media Player**, **VLC**, or import it into any DAW (e.g. GarageBand,
FL Studio, MuseScore) to actually hear it.

## Tuning for your situation
- **Training too slow?** Lower `EPOCHS` in `train.py` (try 10–15 for a
  quick demo run) — the output will be less musically coherent but
  still clearly showing the model learned *something*, which is enough
  to demonstrate the task.
- **Want better quality and have time?** Add more chorale names to
  `CHORALE_NAMES` in `preprocess.py` (music21 ships `bach/bwv1.6`
  through roughly `bach/bwv438`) and raise `EPOCHS`.
- **No GPU and it's painfully slow?** Consider running `train.py` in
  **Google Colab** (free GPU) instead of locally — just upload
  `preprocess.py`'s output (`data/notes.pkl`, `data/vocab.pkl`) or rerun
  preprocessing there, train, then download `model_final.keras` back to
  your machine for `generate.py`.

## How it works, in short
1. Every note becomes a token like `"C4"`; every chord becomes a token
   like `"C4.E4.G4"` (pitch names joined by dots); rests become
   `"REST"`.
2. The model looks at the previous 50 tokens and learns to predict
   token 51 — repeated across the whole Bach corpus, this teaches it
   the statistical patterns of the music (which notes tend to follow
   which).
3. To generate new music, we seed it with a real 50-token snippet from
   the training data, ask it to predict the next token, append that
   prediction, drop the oldest token, and repeat — building an entirely
   new sequence one token at a time.
4. `music21` converts that token sequence back into real `Note`/`Chord`
   objects and writes a standard `.mid` file.


