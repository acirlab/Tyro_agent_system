from __future__ import annotations

import os

from voice_agent.config import ModelLoadingConfig


def fix_unsupported_socks_proxy() -> None:
    has_http_proxy = any(
        os.environ.get(key)
        for key in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy")
    )
    if not has_http_proxy:
        return

    for key in ("ALL_PROXY", "all_proxy"):
        value = os.environ.get(key, "")
        if value.lower().startswith("socks://"):
            os.environ.pop(key, None)


def configure_local_model_loading(config: ModelLoadingConfig) -> None:
    if config.local_files_only:
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


def is_cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def resolve_device(device: str) -> str:
    normalized = str(device or "auto").strip().lower()
    if normalized == "auto":
        return "cuda" if is_cuda_available() else "cpu"
    if normalized.startswith("cuda") and not is_cuda_available():
        raise RuntimeError(f"Device '{device}' was requested, but CUDA is not available.")
    return normalized


def resolve_modelscope_model_path(model_name: str, config: ModelLoadingConfig) -> str:
    if not config.prefer_local_cache or os.path.exists(model_name):
        return model_name

    from modelscope.hub.snapshot_download import snapshot_download

    try:
        return snapshot_download(
            model_name,
            cache_dir=config.modelscope_cache_dir,
            local_files_only=True,
        )
    except Exception as exc:
        if config.local_files_only:
            raise RuntimeError(
                f"ASR model '{model_name}' was not found in the local ModelScope cache."
            ) from exc
        return model_name


def resolve_hf_file(
    repo_id: str,
    filename: str,
    config: ModelLoadingConfig,
    label: str,
) -> str | None:
    if not config.prefer_local_cache:
        return None

    from huggingface_hub import hf_hub_download

    try:
        return hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            cache_dir=config.huggingface_cache_dir,
            local_files_only=True,
        )
    except Exception as exc:
        if config.local_files_only:
            raise RuntimeError(f"{label} '{repo_id}/{filename}' was not found locally.") from exc
        return None

