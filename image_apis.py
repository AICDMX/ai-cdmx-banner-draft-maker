"""
Image-generation provider layer for the AI banner generator.

Thin wrappers over OpenAI (gpt-image-2 via the Responses API) and Google Gemini
(gemini-3.x image models). Each function takes a prompt plus zero or more reference
images (speaker photo, logos), generates a banner, and writes it to ``out_path``.

SDKs are imported lazily so the rest of the project keeps working without them.
Install with:  pip install -e .[api]   (openai, google-genai, pillow)

API keys come from the environment (load them with direnv / a .env file):
    OPENAI_API_KEY
    GEMINI_API_KEY   (falls back to GOOGLE_API_KEY)
"""

import base64
import os
from pathlib import Path

# Default models (see docs/api-cli.md and the API packet).
OPENAI_MODEL = "gpt-5.5"          # orchestrates the gpt-image-2 image_generation tool
GEMINI_MODEL = "gemini-3.1-flash-image-preview"

# Provider-native generation sizes (16:9). Final output is cover-fit to BANNER_SIZE.
OPENAI_SIZE = "2048x1152"         # valid 16:9 size for gpt-image-2
GEMINI_ASPECT_RATIO = "16:9"
GEMINI_IMAGE_SIZE = "2K"

BANNER_SIZE = (1200, 675)         # final banner dimensions (16:9)


class ProviderError(RuntimeError):
    """Raised for missing SDKs, missing API keys, or empty API responses."""


def _require_key(*names: str) -> str:
    """Return the first set environment variable among ``names``."""
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    joined = " or ".join(names)
    raise ProviderError(
        f"No API key found. Set {joined} in your environment "
        f"(e.g. add it to .env and run `direnv allow`)."
    )


def _mime_for(path: str) -> str:
    ext = Path(path).suffix.lower().lstrip(".") or "png"
    return "jpeg" if ext in {"jpg", "jpeg"} else ext


def generate_openai(prompt, image_paths, out_path, *,
                    size=OPENAI_SIZE, quality="high", model=OPENAI_MODEL):
    """Generate a banner with OpenAI's Responses API + image_generation tool.

    Reference images are passed as base64 ``input_image`` items. The generated
    image is returned from an ``image_generation_call`` output item.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ProviderError(
            "The 'openai' package is not installed. Run: pip install -e .[api]"
        ) from exc

    client = OpenAI(api_key=_require_key("OPENAI_API_KEY"))

    content = [{"type": "input_text", "text": prompt}]
    for path in image_paths:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        content.append({
            "type": "input_image",
            "image_url": f"data:image/{_mime_for(path)};base64,{b64}",
        })

    response = client.responses.create(
        model=model,
        input=[{"role": "user", "content": content}],
        tools=[{
            "type": "image_generation",
            "quality": quality,
            "size": size,
        }],
    )

    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]
    if not image_data:
        raise ProviderError("OpenAI returned no image.")

    Path(out_path).write_bytes(base64.b64decode(image_data[0]))
    return out_path


def generate_gemini(prompt, image_paths, out_path, *,
                    aspect_ratio=GEMINI_ASPECT_RATIO,
                    image_size=GEMINI_IMAGE_SIZE, model=GEMINI_MODEL):
    """Generate a banner with Google Gemini image models.

    Prompt and PIL reference images are sent together in ``contents``; the first
    returned inline image part is saved.
    """
    try:
        from google import genai
        from google.genai import types
        from PIL import Image
    except ImportError as exc:
        raise ProviderError(
            "The 'google-genai' / 'pillow' packages are not installed. "
            "Run: pip install -e .[api]"
        ) from exc

    client = genai.Client(api_key=_require_key("GEMINI_API_KEY", "GOOGLE_API_KEY"))

    contents = [prompt] + [Image.open(p) for p in image_paths]

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            response_format={
                "image": {
                    "aspect_ratio": aspect_ratio,
                    "image_size": image_size,
                }
            },
        ),
    )

    for part in response.parts:
        if getattr(part, "inline_data", None) is not None:
            part.as_image().save(out_path)
            return out_path

    raise ProviderError("Gemini returned no image.")


def cover_fit(path, width=BANNER_SIZE[0], height=BANNER_SIZE[1]):
    """Resize/crop the image at ``path`` in place to exactly width x height (cover).

    Scales to cover the target box (no distortion), center-crops the overflow.
    """
    try:
        from PIL import Image
    except ImportError as exc:
        raise ProviderError(
            "The 'pillow' package is not installed. Run: pip install -e .[api]"
        ) from exc

    with Image.open(path) as img:
        img = img.convert("RGB")
        src_w, src_h = img.size
        scale = max(width / src_w, height / src_h)
        new_w, new_h = round(src_w * scale), round(src_h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        img = img.crop((left, top, left + width, top + height))
        img.save(path)
    return path


def generate(backend, prompt, image_paths, out_path, *, model=None, aspect="16:9"):
    """Dispatch to the chosen backend ('gemini' or 'openai'), then cover-fit.

    aspect: "16:9" (banner, 1200x675) or "1:1" (square, 1080x1080).
    """
    if aspect == "1:1":
        openai_size, gemini_ar, target = "1024x1024", "1:1", (1080, 1080)
    else:
        openai_size, gemini_ar, target = OPENAI_SIZE, GEMINI_ASPECT_RATIO, BANNER_SIZE

    if backend == "openai":
        generate_openai(prompt, image_paths, out_path, size=openai_size,
                        **({"model": model} if model else {}))
    elif backend == "gemini":
        generate_gemini(prompt, image_paths, out_path, aspect_ratio=gemini_ar,
                        **({"model": model} if model else {}))
    else:
        raise ProviderError(f"Unknown backend: {backend!r} (expected 'gemini' or 'openai')")
    cover_fit(out_path, target[0], target[1])
    return out_path
