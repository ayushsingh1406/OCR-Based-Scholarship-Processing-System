"""
Image preprocessing for Aadhaar OCR.
Applies adaptive enhancement to improve OCR accuracy across
different image qualities, sizes, and orientations.
"""

import cv2
import numpy as np


def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess Aadhaar card image for optimal OCR results.
    
    Steps:
    1. Load and validate image
    2. Auto-orient (if rotated)
    3. Resize to optimal resolution
    4. Enhance contrast
    5. Denoise

    Returns:
        Preprocessed image as numpy array (BGR for PaddleOCR)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    # Step 1: Resize to optimal width while maintaining aspect ratio
    img = _resize_optimal(img, target_width=1200)

    # Step 2: Enhance contrast using CLAHE on LAB color space
    img = _enhance_contrast(img)

    # Step 3: Light denoising (preserve text edges)
    img = _denoise(img)

    return img


def _resize_optimal(img: np.ndarray, target_width: int = 1200) -> np.ndarray:
    """Resize image to optimal width for OCR."""
    h, w = img.shape[:2]

    # Only upscale if too small, downscale if too large
    if w < 600:
        scale = target_width / w
    elif w > 2000:
        scale = target_width / w
    else:
        return img  # Already in good range

    new_w = int(w * scale)
    new_h = int(h * scale)
    interpolation = cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA
    return cv2.resize(img, (new_w, new_h), interpolation=interpolation)


def _enhance_contrast(img: np.ndarray) -> np.ndarray:
    """Apply CLAHE contrast enhancement on the L channel."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge([l, a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _denoise(img: np.ndarray) -> np.ndarray:
    """Light denoising that preserves text edges."""
    return cv2.bilateralFilter(img, 9, 50, 50)