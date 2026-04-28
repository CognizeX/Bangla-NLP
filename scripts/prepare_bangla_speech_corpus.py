from __future__ import annotations

import argparse
import json
import os
import random
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from huggingface_hub import hf_hub_download
from scipy.signal import resample_poly


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare Suprio85/Bangla_Speech_Corpus for Bangla TTS fine-tuning."
    )
    parser.add_argument(
        "--dataset",
        default="Suprio85/Bangla_Speech_Corpus",
        help="Hugging Face dataset repo id.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where wavs and metadata files will be written.",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=22050,
        help="Target sample rate for VITS Bengali models.",
    )
    parser.add_argument(
        "--eval-fraction",
        type=float,
        default=0.02,
        help="Fraction of samples reserved for evaluation.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used for train/eval split.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of segment-level clips to export.",
    )
    parser.add_argument(
        "--sort-by",
        choices=("shortest", "manifest"),
        default="shortest",
        help="Choose shorter source videos first for faster preparation.",
    )
    parser.add_argument(
        "--min-duration-sec",
        type=float,
        default=0.8,
        help="Skip segments shorter than this threshold.",
    )
    parser.add_argument(
        "--max-duration-sec",
        type=float,
        default=15.0,
        help="Skip segments longer than this threshold.",
    )
    parser.add_argument(
        "--min-text-chars",
        type=int,
        default=2,
        help="Skip very short transcript fragments.",
    )
    return parser.parse_args()


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def to_mono_float32(audio_array: Any) -> np.ndarray:
    audio = np.asarray(audio_array, dtype=np.float32)

    if audio.ndim == 0:
        return audio.reshape(1)

    if audio.ndim == 1:
        return audio

    if audio.shape[0] <= 8:
        audio = audio.mean(axis=0)
    else:
        audio = audio.mean(axis=1)
    return audio.astype(np.float32, copy=False)


def resample_audio(audio: np.ndarray, original_sr: int, target_sr: int) -> np.ndarray:
    if original_sr == target_sr:
        return audio.astype(np.float32, copy=False)

    gcd = np.gcd(original_sr, target_sr)
    up = target_sr // gcd
    down = original_sr // gcd
    resampled = resample_poly(audio, up=up, down=down)
    return resampled.astype(np.float32, copy=False)


def load_manifest(repo_id: str, sort_by: str) -> list[dict[str, Any]]:
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    manifest_path = hf_hub_download(repo_id=repo_id, repo_type="dataset", filename="manifest.jsonl")

    rows: list[dict[str, Any]] = []
    with open(manifest_path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))

    if sort_by == "shortest":
        rows.sort(key=lambda row: float(row.get("duration_sec", 10**12)))

    return rows


def load_transcript(repo_id: str, transcript_file: str) -> dict[str, Any]:
    path = hf_hub_download(repo_id=repo_id, repo_type="dataset", filename=transcript_file)
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def download_audio_path(repo_id: str, audio_file: str) -> str:
    return hf_hub_download(repo_id=repo_id, repo_type="dataset", filename=audio_file)


def write_metadata(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def main() -> None:
    args = parse_args()
    random.seed(args.seed)

    output_dir = args.output_dir.resolve()
    wav_dir = output_dir / "wavs"
    wav_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows = load_manifest(args.dataset, args.sort_by)

    rows: list[str] = []
    exported = 0
    skipped = 0
    downloaded_videos = 0
    used_videos = 0

    for item in manifest_rows:
        if args.limit is not None and exported >= args.limit:
            break

        transcript = load_transcript(args.dataset, item["json_filepath"])
        segments = transcript.get("segments", [])

        usable_segments: list[tuple[int, int, int, str]] = []
        audio_path = ""
        original_sr = 0

        for segment_index, segment in enumerate(segments):
            text = normalize_text(str(segment.get("text", "")))
            start_sec = float(segment.get("start", 0.0))
            end_sec = float(segment.get("end", 0.0))
            duration_sec = end_sec - start_sec

            if end_sec <= start_sec:
                skipped += 1
                continue
            if duration_sec < args.min_duration_sec or duration_sec > args.max_duration_sec:
                skipped += 1
                continue
            if len(text) < args.min_text_chars:
                skipped += 1
                continue

            if not audio_path:
                audio_path = download_audio_path(args.dataset, item["audio_filepath"])
                downloaded_videos += 1
                with sf.SoundFile(audio_path) as audio_file:
                    original_sr = audio_file.samplerate

            start_frame = int(start_sec * original_sr)
            end_frame = int(end_sec * original_sr)
            if end_frame <= start_frame:
                skipped += 1
                continue

            usable_segments.append((segment_index, start_frame, end_frame, text))

            if args.limit is not None and exported + len(usable_segments) >= args.limit:
                break

        if not usable_segments:
            continue

        used_videos += 1
        with sf.SoundFile(audio_path) as audio_file:
            for segment_index, start_frame, end_frame, text in usable_segments:
                if args.limit is not None and exported >= args.limit:
                    break

                audio_file.seek(start_frame)
                clip = audio_file.read(end_frame - start_frame, dtype="float32", always_2d=False)
                audio = to_mono_float32(clip)

                if audio.size == 0:
                    skipped += 1
                    continue

                audio = resample_audio(audio, audio_file.samplerate, args.sample_rate)
                file_stem = f"{item['id']}_{segment_index:04d}"
                file_path = wav_dir / f"{file_stem}.wav"
                sf.write(file_path, audio, args.sample_rate)
                rows.append(f"{file_stem}|{text}|{text}")
                exported += 1

    if not rows:
        raise RuntimeError("No usable samples were exported from the manifest-based corpus.")

    shuffled_rows = rows[:]
    random.shuffle(shuffled_rows)
    eval_count = max(1, int(len(shuffled_rows) * args.eval_fraction)) if len(shuffled_rows) > 1 else 0
    eval_rows = shuffled_rows[:eval_count]
    train_rows = shuffled_rows[eval_count:] if eval_count else shuffled_rows

    write_metadata(output_dir / "metadata.csv", rows)
    write_metadata(output_dir / "metadata_train.csv", train_rows)
    write_metadata(output_dir / "metadata_eval.csv", eval_rows)

    stats = {
        "dataset": args.dataset,
        "sort_by": args.sort_by,
        "target_sample_rate": args.sample_rate,
        "exported_samples": exported,
        "skipped_segments": skipped,
        "downloaded_videos": downloaded_videos,
        "used_videos": used_videos,
        "train_samples": len(train_rows),
        "eval_samples": len(eval_rows),
        "output_dir": str(output_dir),
    }
    (output_dir / "dataset_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
