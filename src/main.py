"""Main detection loop for real-time object detection and hardware alert dispatch."""

import logging
import sys
import time
from typing import Optional

import cv2
import serial
from config import AppConfig
from ultralytics import YOLO

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


class FocusGuardEngine:

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.model: Optional[YOLO] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self.serial_conn: Optional[serial.Serial] = None
        self.last_trigger_time: float = 0.0

    def initialize_hardware(self) -> None:
        """Establishes serial communication with the microcontroller."""
        try:
            logging.info(f"Connecting to microcontroller on {self.config.SERIAL_PORT}...")
            self.serial_conn = serial.Serial(
                port=self.config.SERIAL_PORT,
                baudrate=self.config.BAUD_RATE,
                timeout=self.config.SERIAL_TIMEOUT,
            )
            time.sleep(2.0)  # Allow microcontroller reboot cycle to complete
            logging.info("Serial connection established successfully.")
        except serial.SerialException as e:
            logging.warning(
                f"Could not open serial port {self.config.SERIAL_PORT}: {e}. Running in dry-run mode."
            )
            self.serial_conn = None

    def initialize_vision(self) -> None:
        """Loads YOLO model and configures video capture stream."""
        logging.info(f"Loading YOLO model weights: {self.config.MODEL_PATH}")
        self.model = YOLO(self.config.MODEL_PATH)

        logging.info(f"Opening camera index {self.config.CAMERA_INDEX}...")
        self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.FRAME_HEIGHT)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Failed to open video capture device at index {self.config.CAMERA_INDEX}"
            )

    def dispatch_alert(self) -> None:
        """Sends a high-priority trigger payload over serial if cooldown has elapsed"""
        current_time = time.time()
        if (
            current_time - self.last_trigger_time
        ) >= self.config.TRIGGER_COOLDOWN_SEC:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.write(b"H")
                logging.info("Target object detected. Alert command 'H' sent.")
            else:
                logging.info("[Dry Run] Target detected. Alarm trigger suppressed.")
            self.last_trigger_time = current_time

    def run(self) -> None:
        """Runs the main inference and signal processing loop."""
        self.initialize_hardware()
        self.initialize_vision()

        logging.info("Starting visual processing pipeline. Press 'q' to exit.")

        try:
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    logging.error("Failed to read frame from camera stream.")
                    break

                results = self.model(
                    frame, conf=self.config.CONFIDENCE_THRESHOLD, verbose=False
                )
                target_detected = False

                for result in results:
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        if class_id == self.config.TARGET_CLASS_ID:
                            target_detected = True
                            break

                    annotated_frame = result.plot()

                if target_detected:
                    self.dispatch_alert()

                cv2.imshow("FocusGuard Pipeline", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logging.info("Quit key detected. Shutting down...")
                    break

        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Gracefully closes vision streams and hardware interfaces."""
        logging.info("Cleaning up resources...")
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        cv2.destroyAllWindows()
        logging.info("Shutdown complete.")


if __name__ == "__main__":
    config = AppConfig()
    engine = FocusGuardEngine(config)
    engine.run()
