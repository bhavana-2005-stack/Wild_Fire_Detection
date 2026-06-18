import os
import numpy as np
from PIL import Image

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'wildfire_model.h5')

class FireDetector:
    def __init__(self):
        self.model = None
        self.use_heuristic = True
        
        try:
            from tensorflow.keras.applications import MobileNetV2
            if os.path.exists(MODEL_PATH):
                from tensorflow.keras.models import load_model
                self.model = load_model(MODEL_PATH)
                self.use_heuristic = False
            else:
                self.model = MobileNetV2(weights='imagenet')
                self.use_heuristic = True
        except Exception as e:
            print(f"TensorFlow not available, using heuristic method: {e}")
            self.use_heuristic = True
    
    def predict(self, img_path):
        if self.use_heuristic:
            return self._heuristic_predict(img_path)
        else:
            return self._model_predict(img_path)
    
    def _model_predict(self, img_path):
        from tensorflow.keras.preprocessing import image
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        
        img = Image.open(img_path).convert('RGB')
        img = img.resize((224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        
        preds = self.model.predict(x, verbose=0)
        fire_prob = preds[0][0] if preds.shape[1] == 1 else 0.5
        
        confidence = float(fire_prob * 100)
        prediction = "Fire" if fire_prob >= 0.5 else "Non-Fire"
        
        return prediction, confidence
    
    def _heuristic_predict(self, img_path):
        img = Image.open(img_path).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img)
        
        red_channel = img_array[:, :, 0]
        green_channel = img_array[:, :, 1]
        blue_channel = img_array[:, :, 2]
        
        fire_mask = (
            (red_channel > 150) &
            (green_channel > 50) &
            (blue_channel < 100)
        )
        
        fire_pixels = np.sum(fire_mask)
        total_pixels = fire_mask.size
        fire_ratio = fire_pixels / total_pixels
        
        confidence = min(100, fire_ratio * 200)
        prediction = "Fire" if fire_ratio >= 0.08 else "Non-Fire"
        
        return prediction, confidence
