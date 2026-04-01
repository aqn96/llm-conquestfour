import os
import platform
import subprocess
from typing import Tuple

from ai.ollama.llama_bot import LLMBot


def _cpu_brand_string() -> str:
    """Return macOS CPU brand string when available."""
    if platform.system() != "Darwin":
        return ""
    try:
        out = subprocess.check_output(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            text=True,
            timeout=2,
        )
        return out.strip()
    except Exception:
        return ""


def detect_hardware_profile() -> str:
    """
    Detect a coarse hardware profile for backend routing.

    Returns:
        - "apple_m3": Apple Silicon M3 family
        - "apple_silicon": Apple Silicon non-M3
        - "other": everything else
    """
    if platform.system() != "Darwin":
        return "other"

    if platform.machine().lower() != "arm64":
        return "other"

    brand = _cpu_brand_string().lower()
    if "m3" in brand:
        return "apple_m3"
    return "apple_silicon"


def _build_ollama_bot(
    model_name: str,
    bot_name: str,
    player_name: str,
    personality_key: str,
    setting_key: str,
):
    return LLMBot(
        model_name,
        bot_name,
        player_name,
        personality_key=personality_key,
        occupation_key="Teacher",
        setting_key=setting_key,
    )


def _build_experimental_onnx_bot(
    bot_name: str,
    player_name: str,
    personality_key: str,
    setting_key: str,
):
    # Late import so default path doesn't require onnx deps.
    from ai.onnx_runtime.onnx_bot import ONNXBot

    model_path = os.getenv("CONQUEST4_ONNX_MODEL_PATH", "models/mistral-onnx")
    use_neural_engine = os.getenv("CONQUEST4_USE_NEURAL_ENGINE", "1") != "0"
    return ONNXBot(
        model_path=model_path,
        name=bot_name,
        opponent_name=player_name,
        personality_key=personality_key,
        occupation_key="Teacher",
        setting_key=setting_key,
        use_neural_engine=use_neural_engine,
    )


def build_bot(
    *,
    backend_choice: str,
    model_name: str,
    bot_name: str,
    player_name: str,
    personality_key: str,
    setting_key: str,
):
    """
    Build the bot backend with safe fallback behavior.

    backend_choice:
        - "auto"
        - "ollama"
        - "npu_experimental"
    """
    profile = detect_hardware_profile()

    if backend_choice == "ollama":
        bot = _build_ollama_bot(model_name, bot_name, player_name, personality_key, setting_key)
        return bot, "ollama", profile

    if backend_choice == "npu_experimental":
        if profile != "apple_m3":
            bot = _build_ollama_bot(model_name, bot_name, player_name, personality_key, setting_key)
            return bot, "ollama_fallback_non_m3", profile
        try:
            bot = _build_experimental_onnx_bot(bot_name, player_name, personality_key, setting_key)
            return bot, "onnx_coreml_experimental", profile
        except Exception:
            bot = _build_ollama_bot(model_name, bot_name, player_name, personality_key, setting_key)
            return bot, "ollama_fallback_onnx_error", profile

    # auto: stable default for all platforms, including Apple M3.
    bot = _build_ollama_bot(model_name, bot_name, player_name, personality_key, setting_key)
    return bot, "ollama_auto", profile


def backend_notice(resolved_backend: str, hardware_profile: str) -> Tuple[str, str]:
    """Return (title, message) for UI notice."""
    if resolved_backend == "onnx_coreml_experimental":
        return (
            "Experimental NPU Backend Enabled",
            (
                "Using ONNX/CoreML experimental backend on Apple M3.\n"
                "This path is for research and may be slower or less stable than Ollama/Metal."
            ),
        )

    if resolved_backend == "ollama_fallback_non_m3":
        return (
            "Fallback to Stable Backend",
            (
                "Experimental NPU backend requires Apple M3 detection.\n"
                "Using stable Ollama + llama.cpp + Metal backend instead."
            ),
        )

    if resolved_backend == "ollama_fallback_onnx_error":
        return (
            "Fallback to Stable Backend",
            (
                "ONNX/CoreML backend initialization failed.\n"
                "Using stable Ollama + llama.cpp + Metal backend instead."
            ),
        )

    if resolved_backend == "ollama_auto" and hardware_profile == "apple_m3":
        return (
            "Apple Silicon Optimization",
            "Detected Apple M3. Using stable Ollama + llama.cpp + Metal optimized path.",
        )

    return ("Inference Backend", "Using stable Ollama + llama.cpp + Metal backend.")
