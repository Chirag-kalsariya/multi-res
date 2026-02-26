import io

from PIL import Image, ImageCms

# Maps MIME types to Pillow format identifiers.
MIME_TO_SUFFIX: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/jpg":  ".jpg",
    "image/png":  ".png",
    "image/webp": ".webp",
    "image/tiff": ".tiff",
    "image/tif":  ".tiff",
    "image/bmp":  ".bmp",
}

_SUFFIX_TO_PILLOW_FORMAT: dict[str, str] = {
    ".jpg":  "JPEG",
    ".png":  "PNG",
    ".webp": "WEBP",
    ".tiff": "TIFF",
    ".bmp":  "BMP",
}

# Formats that do not support an alpha channel.
_NO_ALPHA_FORMATS = {".jpg", ".bmp"}

_SRGB_PROFILE = ImageCms.createProfile("sRGB")


def _to_srgb(img: Image.Image) -> tuple[Image.Image, bytes | None]:
    """
    If the image has an embedded ICC profile, convert its color space to sRGB.
    Returns the (possibly converted) image and the sRGB ICC profile bytes to embed.
    """
    raw_profile = img.info.get("icc_profile")

    if not raw_profile:
        # No profile embedded — assume sRGB, embed the profile so output is tagged.
        srgb_bytes = ImageCms.ImageCmsProfile(_SRGB_PROFILE).tobytes()
        return img, srgb_bytes

    try:
        input_profile = ImageCms.ImageCmsProfile(io.BytesIO(raw_profile))
        input_desc = ImageCms.getProfileDescription(input_profile).strip()

        # If already sRGB, no conversion needed — just re-embed.
        if "srgb" in input_desc.lower():
            return img, raw_profile

        # Ensure mode is compatible with ImageCms transform.
        if img.mode not in ("RGB", "RGBA", "L", "LA"):
            img = img.convert("RGBA" if "A" in img.mode else "RGB")

        converted = ImageCms.profileToProfile(
            img,
            inputProfile=input_profile,
            outputProfile=_SRGB_PROFILE,
            renderingIntent=ImageCms.Intent.PERCEPTUAL,
            outputMode=img.mode,
        )
        if converted is None:
            srgb_bytes = ImageCms.ImageCmsProfile(_SRGB_PROFILE).tobytes()
            return img, srgb_bytes
        srgb_bytes = ImageCms.ImageCmsProfile(_SRGB_PROFILE).tobytes()
        return converted, srgb_bytes
    except (ImageCms.PyCMSError, OSError):
        # Malformed profile — proceed without conversion, embed sRGB tag.
        srgb_bytes = ImageCms.ImageCmsProfile(_SRGB_PROFILE).tobytes()
        return img, srgb_bytes


def convert_image(
    image_bytes: bytes,
    output_mime: str,
    quality: int = 80,
) -> tuple[bytes, str]:
    """
    Convert image bytes to the requested output MIME type.

    Performs ICC color profile conversion to sRGB so colors are preserved
    accurately across all target formats, matching the output of sharp/libvips.

    Args:
        image_bytes: Raw bytes of the input image.
        output_mime: Target MIME type (e.g. "image/webp").
        quality: Compression quality from 0 (smallest) to 100 (best). Default 80.
                 For lossless formats (PNG, TIFF) this controls compression
                 effort/level rather than lossy quality.

    Returns:
        Tuple of (converted image bytes, output MIME type string).

    Raises:
        ValueError: If the output MIME type is not supported or quality is out of range.
        OSError: If Pillow cannot decode the input image.
    """
    output_mime = output_mime.lower().strip()

    if output_mime not in MIME_TO_SUFFIX:
        raise ValueError(
            f"Unsupported output type '{output_mime}'. "
            f"Supported types: {', '.join(MIME_TO_SUFFIX.keys())}"
        )

    if not (0 <= quality <= 100):
        raise ValueError("Quality must be between 0 and 100.")

    suffix = MIME_TO_SUFFIX[output_mime]
    fmt    = _SUFFIX_TO_PILLOW_FORMAT[suffix]

    with Image.open(io.BytesIO(image_bytes)) as img:
        # Convert color profile to sRGB for accurate, consistent colors.
        img, icc_bytes = _to_srgb(img)

        # Flatten alpha for formats that don't support transparency.
        if suffix in _NO_ALPHA_FORMATS and img.mode in ("RGBA", "LA", "PA"):
            img = img.convert("RGBA") if img.mode != "RGBA" else img
            background = Image.new("RGBA", img.size, (255, 255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background.convert("RGB")
        elif fmt not in ("JPEG", "BMP") and img.mode == "P":
            img = img.convert("RGBA")

        output_buffer = io.BytesIO()

        if fmt == "JPEG":
            # subsampling=0 keeps full chroma resolution (4:4:4).
            img.save(output_buffer, format="JPEG",
                     quality=quality, subsampling=0, optimize=True,
                     icc_profile=icc_bytes)
        elif fmt == "PNG":
            # PNG is lossless — compress_level controls deflate effort (0=none, 9=max).
            # Must be saved separately from icc_profile to ensure compress_level takes effect.
            # Map quality 0-100 → compress_level 9-0
            # (quality 0 = max compression/smallest, quality 100 = no compression/largest).
            compress_level = round((100 - quality) / 100 * 9)
            img.save(output_buffer, format="PNG",
                     compress_level=compress_level, optimize=True,
                     icc_profile=icc_bytes)
        elif fmt == "WEBP":
            # method=6 uses the best (slowest) compression effort.
            img.save(output_buffer, format="WEBP",
                     quality=quality, method=6,
                     icc_profile=icc_bytes)
        elif fmt == "TIFF":
            # JPEG-in-TIFF applies lossy compression and respects quality.
            img.save(output_buffer, format="TIFF",
                     compression="jpeg", quality=quality,
                     icc_profile=icc_bytes)
        else:
            # BMP — no compression options, always stores raw pixels.
            img.save(output_buffer, format=fmt, icc_profile=icc_bytes)
        output_buffer.seek(0)

    return output_buffer.read(), output_mime
