from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Patch a downloaded Coqui TTS config so it can fine-tune on the prepared Bangla dataset."
    )
    parser.add_argument("--base-config", type=Path, required=True, help="Path to the downloaded model config.json.")
    parser.add_argument("--dataset-dir", type=Path, required=True, help="Prepared dataset directory.")
    parser.add_argument("--output-config", type=Path, required=True, help="Where to write the patched config.")
    parser.add_argument("--run-name", default="bangla_vits_male_finetune", help="Training run name.")
    parser.add_argument("--output-path", type=Path, default=Path("training_runs"), help="Training output directory.")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size for fine-tuning.")
    parser.add_argument("--eval-batch-size", type=int, default=8, help="Eval batch size for fine-tuning.")
    parser.add_argument("--epochs", type=int, default=300, help="Number of fine-tuning epochs.")
    parser.add_argument("--lr", type=float, default=1e-5, help="Learning rate for fine-tuning.")
    parser.add_argument(
        "--test-sentence",
        action="append",
        default=[
            "আমি বাংলায় কথা বলতে পারি।",
            "আজকের আবহাওয়া বেশ সুন্দর।",
            "এই মডেলটি বাংলা টেক্সট থেকে স্পিচ তৈরি করে।",
        ],
        help="Sentence to synthesize during evaluation. Can be repeated.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    dataset_dir = args.dataset_dir.resolve()
    output_config = args.output_config.resolve()
    output_config.parent.mkdir(parents=True, exist_ok=True)

    with args.base_config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    config["run_name"] = args.run_name
    config["output_path"] = str(args.output_path.resolve())
    config["batch_size"] = args.batch_size
    config["eval_batch_size"] = args.eval_batch_size
    config["epochs"] = args.epochs
    config["lr"] = args.lr
    config["test_sentences"] = args.test_sentence
    config["datasets"] = [
        {
            "formatter": "ljspeech",
            "path": str(dataset_dir),
            "meta_file_train": "metadata_train.csv",
            "meta_file_val": "metadata_eval.csv",
            "language": "bn",
        }
    ]

    audio_cfg = config.get("audio", {})
    if isinstance(audio_cfg, dict):
        audio_cfg["sample_rate"] = audio_cfg.get("sample_rate", 22050)
        if "output_sample_rate" in audio_cfg:
            audio_cfg["output_sample_rate"] = 22050
        config["audio"] = audio_cfg

    with output_config.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)

    print(f"Wrote fine-tuning config to: {output_config}")


if __name__ == "__main__":
    main()
