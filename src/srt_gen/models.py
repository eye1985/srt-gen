from .utils import is_apple

mlx_default_model = "mlx-community/whisper-large-v3-mlx"

# Canonical fp16 MLX conversions hosted by the mlx-community org, one per
# official Whisper size. Values are the HF repo ids passed as `path_or_hf_repo`.
# (Quantized -4bit/-8bit/-fp32 variants and language-specific fine-tunes are
# omitted; add them here if needed.)
# Ordered smallest-to-largest so the UI can list them as-is.
mlx_models = (
    "mlx-community/whisper-tiny-mlx",
    "mlx-community/whisper-tiny.en-mlx",
    "mlx-community/whisper-base-mlx",
    "mlx-community/whisper-base.en-mlx",
    "mlx-community/whisper-small-mlx",
    "mlx-community/whisper-small.en-mlx",
    "mlx-community/whisper-medium-mlx",
    "mlx-community/whisper-medium.en-mlx",
    "mlx-community/whisper-large-mlx",
    "mlx-community/whisper-large-v1-mlx",
    "mlx-community/whisper-large-v2-mlx",
    mlx_default_model,
    "mlx-community/whisper-large-v3-turbo",
    "mlx-community/distil-whisper-large-v3",
    "mlx-community/distil-whisper-medium.en",
)

fw_default_model = "large-v3"
# Model names accepted by faster-whisper (faster_whisper.utils._MODELS). These
# are downloaded from the Systran HF repos on first use.
fw_models = (
    "tiny",
    "tiny.en",
    "base",
    "base.en",
    "small",
    "small.en",
    "medium",
    "medium.en",
    "large",
    "large-v1",
    "large-v2",
    fw_default_model,
    "large-v3-turbo",
    "turbo",
    "distil-small.en",
    "distil-medium.en",
    "distil-large-v2",
    "distil-large-v3",
    "distil-large-v3.5",
)


def models_for_platform() -> tuple[str, ...]:
    # Which backend runs is decided by hardware (see main.main), so the model
    # list a caller may pick from follows the same split.
    return mlx_models if is_apple() else fw_models


def default_model_for_platform() -> str:
    return mlx_default_model if is_apple() else fw_default_model
