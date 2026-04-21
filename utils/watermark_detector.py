import os
import cv2
from ultralytics import YOLO
from typing import Dict, Any, List

class WatermarkDetector:
    def __init__(self, model_path: str = "yolo_detector/models/detector.pt"):
        """
        Initialize the YOLO model for watermark detection.
        """
        self.model_path = model_path
        if not os.path.exists(model_path):
            print(f"  [WARN] YOLO model not found at {model_path}. Watermark detection will be skipped.")
            self.model = None
        else:
            try:
                self.model = YOLO(model_path)
            except Exception as e:
                print(f"  [ERROR] Failed to load YOLO model: {e}")
                self.model = None

        # Class Mapping as provided by user
        # 0 -> aadhaar_logo, 1 -> ashoka_emblem, 2 -> signature
        self.class_map = {
            0: "aadhaar_logo",
            1: "ashoka_emblem",
            2: "signature"
        }

    def detect(self, image_path: str, output_dir: str = "output/annotated") -> Dict[str, bool]:
        """
        Perform detection on the image and save annotated result.
        Returns a dictionary of detected components.
        """
        if self.model is None:
            return {}

        results = self.model(image_path, verbose=False)
        if not results:
            return {}

        result = results[0]
        detected_classes = set()
        
        # Extract detected class indices and map them to names
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                if cls_id in self.class_map:
                    detected_classes.add(self.class_map[cls_id])

        # Prepare watermark_detection dict (boolean flags for presence)
        detection_flags = {
            "aadhaar_logo": "aadhaar_logo" in detected_classes,
            "ashoka_emblem": "ashoka_emblem" in detected_classes,
            "signature": "signature" in detected_classes
        }

        # Save annotated image
        os.makedirs(output_dir, exist_ok=True)
        img_name = os.path.basename(image_path)
        annotated_path = os.path.join(output_dir, img_name)
        
        # result.plot() returns a BGR numpy array
        try:
            annotated_img = result.plot()
            cv2.imwrite(annotated_path, annotated_img)
        except Exception as e:
            print(f"  [WARN] Could not save annotated image: {e}")

        return detection_flags
