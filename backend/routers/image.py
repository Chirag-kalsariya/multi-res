from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from helpers.image_converter import MIME_TO_SUFFIX, convert_image

router = APIRouter(prefix="/image", tags=["Image"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/convert",
    response_class=Response,
    responses={
        200: {"content": {"image/*": {}}, "description": "Converted image binary"},
        400: {"description": "Could not decode/encode image"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported input image type"},
        422: {"description": "Unsupported output type or missing fields"},
    },
)
async def convert_image_format(
    file: UploadFile = File(..., description="Input image (max 10 MB)"),
    output_type: str = Form("image/webp", description="Target MIME type, e.g. image/webp. Default: image/webp."),
    quality: int = Form(80, description="Compression quality 0 (smallest) to 100 (best). Default: 80."),
) -> Response:
    """
    Convert an uploaded image to the requested format.

    - Accepts any common image type up to **10 MB**.
    - Returns the converted image as a binary response with the correct Content-Type.
    - No compression is applied — only the format/container is changed.

    Supported input & output types:
    `image/jpeg`, `image/jpg`, `image/png`, `image/webp`,
    `image/tiff`, `image/tif`, `image/bmp`
    """
    # Validate content type
    if file.content_type not in MIME_TO_SUFFIX:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported input image type '{file.content_type}'. "
                   f"Supported types: {', '.join(MIME_TO_SUFFIX.keys())}",
        )

    # Validate output type
    if output_type.lower().strip() not in MIME_TO_SUFFIX:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported output type '{output_type}'. "
                   f"Supported types: {', '.join(MIME_TO_SUFFIX.keys())}",
        )

    # Validate quality
    if not (0 <= quality <= 100):
        raise HTTPException(
            status_code=422,
            detail="Quality must be an integer between 0 and 100.",
        )

    # Read and enforce size limit
    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is 10 MB, "
                   f"received {len(image_bytes) / (1024 * 1024):.2f} MB.",
        )

    try:
        converted_bytes, output_mime = convert_image(image_bytes, output_type, quality)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except (OSError, Exception) as e:
        raise HTTPException(status_code=400, detail=f"Could not process image: {str(e)}")

    # Derive a clean filename for the Content-Disposition header
    original_stem = (file.filename or "image").rsplit(".", 1)[0]
    ext = MIME_TO_SUFFIX[output_mime].lstrip(".")
    output_filename = f"{original_stem}.{ext}"

    return Response(
        content=converted_bytes,
        media_type=output_mime,
        headers={
            "Content-Disposition": f'attachment; filename="{output_filename}"',
            "Content-Length": str(len(converted_bytes)),
        },
    )
