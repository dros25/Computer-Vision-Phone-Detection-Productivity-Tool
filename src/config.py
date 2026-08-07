"""Configuration module for the FocusGuard computer vision pipeline."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    # Computer Vision Settings
    MODEL_PATH: str = "yolov8n.pt"
    TARGET_CLASS_ID: int = 67  # COCO Class ID 67 = 'cell phone'
    CONFIDENCE_THRESHOLD: float = 0.50
    CAMERA_INDEX: int = 0
    FRAME_WIDTH: int = 1280
    FRAME_HEIGHT: int = 720

    # Hardware & Serial Settings
    SERIAL_PORT: str = "COM3"  # Adjust for target OS 
    BAUD_RATE: int = 9600
    SERIAL_TIMEOUT: float = 1.0

    # Rate Limiting & Cooldown
    TRIGGER_COOLDOWN_SEC: float = 1.0  # Minimum time between serial triggers
