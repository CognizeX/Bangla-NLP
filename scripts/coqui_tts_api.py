from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

try:
    from synthesize_bangla_tts import DEFAULT_MODEL_NAME, load_tts_model, synthesize_to_file
except ImportError:
    from scripts.synthesize_bangla_tts import DEFAULT_MODEL_NAME, load_tts_model, synthesize_to_file


TEMP_OUTPUT_DIR = Path(tempfile.gettempdir()) / "coqui_tts_api"
TEMP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Bangla text to synthesize.")
    model_name: str = Field(
        default=DEFAULT_MODEL_NAME,
        description="Coqui model name to load.",
    )
    device: str | None = Field(
        default=None,
        description="Optional torch device, for example cpu or cuda.",
    )
    filename: str = Field(
        default="speech.wav",
        description="Download filename for the generated WAV file.",
    )


class HealthResponse(BaseModel):
    status: str
    default_model_name: str


app = FastAPI(
    title="Coqui Bangla TTS API",
    description="FastAPI wrapper around the Coqui Bangla TTS synthesis script.",
    version="1.0.0",
)


def _cleanup_file(path: Path) -> None:
    path.unlink(missing_ok=True)


def _normalize_filename(filename: str) -> str:
    cleaned = filename.strip() or "speech.wav"
    if not cleaned.lower().endswith(".wav"):
        cleaned = f"{cleaned}.wav"
    return Path(cleaned).name


@app.get("/", response_model=HealthResponse)
def root() -> HealthResponse:
    return HealthResponse(status="ok", default_model_name=DEFAULT_MODEL_NAME)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", default_model_name=DEFAULT_MODEL_NAME)


@app.post("/tts", response_class=FileResponse, responses={200: {"content": {"audio/wav": {}}}})
def tts(request: TTSRequest) -> FileResponse:
    output_path = TEMP_OUTPUT_DIR / f"{uuid4().hex}.wav"

    try:
        synthesize_to_file(
            text=request.text,
            output_path=output_path,
            model_name=request.model_name,
            device=request.device,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        output_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {exc}") from exc

    return FileResponse(
        path=output_path,
        media_type="audio/wav",
        filename=_normalize_filename(request.filename),
        background=BackgroundTask(_cleanup_file, output_path),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a FastAPI server for Coqui Bangla TTS.")
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for local development.",
    )
    parser.add_argument(
        "--preload-model",
        action="store_true",
        help="Load the default model during startup instead of waiting for the first request.",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Optional torch device for default model preloading, for example cpu or cuda.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.preload_model:
        load_tts_model(model_name=DEFAULT_MODEL_NAME, device=args.device)

    if args.reload:
        uvicorn.run("coqui_tts_api:app", host=args.host, port=args.port, reload=True)
    else:
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
