from pydantic import BaseModel
import numpy as np
import torch
import torch.nn.functional as F
import cv2
from insightface.app import FaceAnalysis


# # API Response Model
# class LivenessModel(BaseModel):
#     is_live: bool
#     confidence: float
#     status: str


class KYCModels:
    def __init__(self):
        # 1. Initialize Face Analysis (Detector + Matcher)
        # Uses 'buffalo_l' (ArcFace + SCRFD)
        self.face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=-1, det_size=(640, 640))

        # 2. Initialize Liveness (MiniFASNetV2SE)
        # Note: You would typically load the state_dict here
        self.liveness_model = self._load_liveness_model("./weights/minifas_v2_se.pth")

    def _load_liveness_model(self, path):
        # Placeholder: In production, import the MiniFASNet class and load weights
        # For now, we simulate the structure
        return torch.load(path, map_location="cpu") if torch.os.path.exists(path) else None

    def detect_and_match(self, selfie_img, id_img):
        # Detect faces in both
        selfie_faces = self.face_app.get(selfie_img)
        id_faces = self.face_app.get(id_img)

        if not selfie_faces or not id_faces:
            return None, "Face not found in one or both images"

        # Extract normalized embeddings (512-d)
        selfie_emb = selfie_faces[0].normed_embedding
        id_emb = id_faces[0].normed_embedding

        # Compute Cosine Similarity
        score = np.dot(selfie_emb, id_emb)
        return float(score), None

    def check_liveness(self, selfie_img):
        # 1. Detect face for cropping
        faces = self.face_app.get(selfie_img)
        if not faces: return 0.0
        
        # 2. Pre-process crop for MiniFASNet (80x80)
        # (Simplified logic for the scratch build)
        return 0.98  # Mock score for code structure


# # Anti-Spoofing Model
# class AntiSpoofPredict:
#     def __init__(self, model_path=None, device="cpu"):
#         self.device = torch.device(device)
#         # Create a simple model architecture for demonstration
#         self.model = self._create_model()
#         # Load the state dict if model_path is provided
#         if model_path:
#             try:
#                 state_dict = torch.load(model_path, map_location=self.device, weights_only=False)
#                 if isinstance(state_dict, dict):
#                     self.model.load_state_dict(state_dict)
#                 else:
#                     self.model = state_dict
#             except Exception as e:
#                 print(f"Warning: Could not load model weights: {e}")
#                 # Use a dummy model for demonstration
#                 pass
#         self.model.eval()

#     def _create_model(self):
#         # Simple CNN model for anti-spoofing (placeholder)
#         # In a real implementation, you would use the actual MiniFASNet architecture
#         class SimpleAntiSpoofModel(torch.nn.Module):
#             def __init__(self):
#                 super().__init__()
#                 self.conv1 = torch.nn.Conv2d(3, 16, 3, padding=1)
#                 self.conv2 = torch.nn.Conv2d(16, 32, 3, padding=1)
#                 self.pool = torch.nn.AdaptiveAvgPool2d((1, 1))
#                 self.fc = torch.nn.Linear(32, 3)  # 3 classes: real, fake2d, fake3d
                
#             def forward(self, x):
#                 x = torch.relu(self.conv1(x))
#                 x = torch.relu(self.conv2(x))
#                 x = self.pool(x)
#                 x = x.view(x.size(0), -1)
#                 x = self.fc(x)
#                 return x
        
#         return SimpleAntiSpoofModel().to(self.device)

#     def get_crop_and_resize(self, img, box, target_sz=(80, 80)):
#         """Crops the face based on the detection box and resizes for the model."""
#         x, y, w, h = box
#         crop = img[y:y+h, x:x+w]
#         return cv2.resize(crop, target_sz)

#     def predict(self, img, face_box=None):
#         """
#         Runs inference on a face crop.
#         Result: [Real_Prob, Fake2D_Prob, Fake3D_Prob]
#         """
#         try:
#             if face_box is not None:
#                 face_img = self.get_crop_and_resize(img, face_box)
#             else:
#                 # Use the entire image if no face box provided
#                 face_img = cv2.resize(img, (80, 80))
            
#             # Convert to Tensor (Normalize to 0-1)
#             input_data = face_img.transpose((2, 0, 1)) # HWC to CHW
#             input_data = torch.from_numpy(input_data).float().unsqueeze(0).to(self.device)
#             input_data = input_data / 255.0  # Normalize to 0-1
            
#             with torch.no_grad():
#                 output = self.model(input_data)
#                 result = F.softmax(output, dim=1).cpu().numpy()
            
#             return result[0]
#         except Exception as e:
#             print(f"Error during prediction: {e}")
#             # Return dummy prediction for demonstration
#             return np.array([0.9, 0.05, 0.05])  # High confidence for real


# # Face Detector
# class FaceDetector:
#     def __init__(self, det_size=(640, 640), ctx_id=0):
#         """
#         det_size: The resolution the model 'sees'. 640x640 is the KYC standard.
#         ctx_id: 0 for GPU (recommended for speed), -1 for CPU.
#         """
#         # We only enable 'detection' to keep this module lightweight
#         self.app = FaceAnalysis(allowed_modules=['detection'], providers=['CPUExecutionProvider'])
#         self.app.prepare(ctx_id=ctx_id, det_size=det_size)

#     def detect_main_face(self, img):
#         """
#         Finds all faces but returns ONLY the most prominent one.
#         Useful for excluding people in the background of a selfie.
#         """
#         faces = self.app.get(img)
#         if not faces:
#             return None

#         # Logic: Sort by the area of the bounding box (Width * Height)
#         # The largest face is usually the user.
#         main_face = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]))
        
#         return {
#             "bbox": main_face.bbox.astype(int),    # [x1, y1, x2, y2]
#             "kps": main_face.kps,                  # 5 Keypoints (landmarks)
#             "det_score": main_face.det_score       # Confidence (0.0 - 1.0)
#         }

# # Face Matching Model
# class FaceMatcher:
#     def __init__(self, model_name='buffalo_l', ctx_id=0):
#         """
#         model_name: 'buffalo_l' is high-accuracy; 'buffalo_s' is faster.
#         ctx_id: 0 for GPU, -1 for CPU.
#         """
#         self.app = FaceAnalysis(name=model_name)
#         # det_size=(640, 640) is standard for clear detection
#         self.app.prepare(ctx_id=ctx_id, det_size=(640, 640))

#     def get_embedding(self, img):
#         """Extracts the 512-d embedding from the largest face in the image."""
#         faces = self.app.get(img)
#         if not faces:
#             return None
        
#         # In KYC, we usually only care about the most prominent face
#         # Sort by box size to find the 'main' person
#         faces = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]), reverse=True)
#         return faces[0].normed_embedding

#     def compute_sim(self, feat1, feat2):
#         """Calculates Cosine Similarity between two embeddings."""
#         # Since InsightFace returns 'normed_embedding', dot product equals cosine similarity
#         return np.dot(feat1, feat2)

#     def verify(self, img1, img2, threshold=0.45):
#         """
#         1:1 Verification. 
#         Returns (is_match, score)
#         """
#         emb1 = self.get_embedding(img1)
#         emb2 = self.get_embedding(img2)

#         if emb1 is None or emb2 is None:
#             return False, 0.0

#         score = self.compute_sim(emb1, emb2)
#         return score > threshold, float(score)
          