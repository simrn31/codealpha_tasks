import pickle
from pathlib import Path

from music21 import corpus, note, chord

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# A curated slice of Bach chorales bundled with music21's corpus.
# Using ~20 pieces (instead of the full ~370) keeps preprocessing and
# training time reasonable for an internship demo. Add more entries
# (music21 numbers chorales bwv1.6 through bwv438) for a richer model.
CHORALE_NAMES = [f"bach/bwv{n}" for n in [
    "1.6", "2.6", "3.6", "4.8", "5.7", "6.6", "7.7", "8.6", "9.7", "10.7",
    "11.6", "12.7", "13.6", "14.5", "15.5", "16.6", "17.7", "18.5", "19.7", "20.7",
]]


def extract_tokens():
    all_tokens = []
    for name in CHORALE_NAMES:
        try:
            score = corpus.parse(name)
        except Exception as exc:
            print(f"Skipping {name}: {exc}")
            continue

        piece_tokens = 0
        for element in score.flatten().notesAndRests:
            if isinstance(element, note.Note):
                all_tokens.append(str(element.pitch))
                piece_tokens += 1
            elif isinstance(element, chord.Chord):
                # Store as full pitch names (e.g. "C4.E4.G4"), not pitch
                # classes, so the exact octave is preserved for later
                # reconstruction into a real MIDI chord.
                all_tokens.append(".".join(str(p) for p in element.pitches))
                piece_tokens += 1
            elif isinstance(element, note.Rest):
                all_tokens.append("REST")
                piece_tokens += 1
        print(f"Parsed {name}: {piece_tokens} tokens")

    return all_tokens


def main():
    tokens = extract_tokens()
    if not tokens:
        raise RuntimeError(
            "No tokens extracted — check that music21 is installed "
            "correctly and its corpus data is available."
        )

    vocab = sorted(set(tokens))

    with open(DATA_DIR / "notes.pkl", "wb") as f:
        pickle.dump(tokens, f)
    with open(DATA_DIR / "vocab.pkl", "wb") as f:
        pickle.dump(vocab, f)

    print(f"\nDone. {len(tokens)} total tokens, {len(vocab)} unique tokens.")
    print(f"Saved to {DATA_DIR}/notes.pkl and {DATA_DIR}/vocab.pkl")


if __name__ == "__main__":
    main()
