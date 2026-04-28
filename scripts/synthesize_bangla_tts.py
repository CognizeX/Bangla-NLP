from __future__ import annotations

import argparse
import os
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Any

DEFAULT_MODEL_NAME = "tts_models/bn/custom/vits-male"
_SYNTHESIS_LOCK = Lock()
RUNTIME_TMP_DIR = Path(__file__).resolve().parents[1] / "runtime_tmp"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthesize Bangla speech with the best model from the paper.")
    parser.add_argument(
        "--text",
        required=True,
        help="Bangla text to synthesize.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output WAV file path.",
    )
    parser.add_argument(
        "--model-name",
        default=DEFAULT_MODEL_NAME,
        help="Coqui model name. Defaults to the best Bengali VITS male model.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Optional torch device, for example cpu or cuda.",
    )
    return parser.parse_args()


def _prepare_runtime_dirs() -> Path:
    RUNTIME_TMP_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = str(RUNTIME_TMP_DIR)

    # Coqui imports eventually reach librosa/numba, which can stall if temp
    # paths are inconsistent on Windows. Keep them pinned to a local folder.
    os.environ["TEMP"] = temp_path
    os.environ["TMP"] = temp_path
    os.environ["TMPDIR"] = temp_path
    os.environ.setdefault("NUMBA_CACHE_DIR", temp_path)
    return RUNTIME_TMP_DIR


def _patch_transformers_compat() -> None:
    try:
        import transformers.pytorch_utils as pytorch_utils
    except Exception:
        return

    if hasattr(pytorch_utils, "isin_mps_friendly"):
        return

    def isin_mps_friendly(elements: Any, test_elements: Any) -> Any:
        import torch

        return torch.isin(elements, test_elements)

    pytorch_utils.isin_mps_friendly = isin_mps_friendly


def _import_tts_class() -> type[Any]:
    _prepare_runtime_dirs()
    _patch_transformers_compat()

    from TTS.api import TTS

    return TTS


@lru_cache(maxsize=8)
def load_tts_model(model_name: str = DEFAULT_MODEL_NAME, device: str | None = None) -> Any:
    TTS = _import_tts_class()
    tts = TTS(model_name=model_name, progress_bar=False)
    if device:
        tts = tts.to(device)
    return tts


def synthesize_to_file(
    *,
    text: str,
    output_path: Path,
    model_name: str = DEFAULT_MODEL_NAME,
    device: str | None = None,
) -> Path:
    normalized_text = text.strip()
    if not normalized_text:
        raise ValueError("Text must not be empty.")

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tts = load_tts_model(model_name=model_name, device=device)
    with _SYNTHESIS_LOCK:
        tts.tts_to_file(text=normalized_text, file_path=str(output_path))
    return output_path


def main() -> None:
    args = parse_args()
    output_path = synthesize_to_file(
        text=args.text,
        output_path=args.output,
        model_name=args.model_name,
        device=args.device,
    )
    print(f"Saved synthesized audio to: {output_path}")


if __name__ == "__main__":
    main()
