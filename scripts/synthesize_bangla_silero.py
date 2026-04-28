from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import scipy.io.wavfile as wavfile
import torch
from aksharamukha import transliterate


DEFAULT_TEXT = "আমি বাংলায় কথা বলতে পারি।"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthesize Bangla speech with Silero Indic Bengali voices.")
    parser.add_argument("--text", default=DEFAULT_TEXT, help="Bangla text to synthesize.")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output WAV file path.",
    )
    parser.add_argument(
        "--speaker",
        default="bengali_male",
        choices=("bengali_male", "bengali_female"),
        help="Indic Bengali speaker.",
    )
    parser.add_argument(
        "--hub-dir",
        type=Path,
        default=Path("outputs") / "torchhub",
        help="Torch hub cache directory.",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=48000,
        help="Target output sample rate.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.hub_dir.mkdir(parents=True, exist_ok=True)

    torch.hub.set_dir(str(args.hub_dir.resolve()))
    model, _ = torch.hub.load(
        repo_or_dir="snakers4/silero-models",
        model="silero_tts",
        language="indic",
        speaker="v4_indic",
        trust_repo=True,
    )

    romanized = transliterate.process("Bengali", "ISO", args.text.strip())
    audio = model.apply_tts(romanized, speaker=args.speaker, sample_rate=args.sample_rate)
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    audio = np.asarray(audio)
    wavfile.write(str(args.output), args.sample_rate, audio)

    print(f"Speaker: {args.speaker}")
    print(f"Romanized (escaped): {romanized.encode('unicode_escape').decode('ascii')}")
    print(f"Saved synthesized audio to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
