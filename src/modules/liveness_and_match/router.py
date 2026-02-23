from fastapi import UploadFile, File, APIRouter
import cv2
import numpy as np

from src.modules.liveness_and_match.model import KYCModels



liveness_router = APIRouter()


# Initialize models once at module level
engine = KYCModels()

async def read_img(file: UploadFile):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

@liveness_router.post("/verify")
async def verify_identity(selfie: UploadFile = File(...), id_card: UploadFile = File(...)):
    # 1. Read files into OpenCV format
    img_selfie = await read_img(selfie)
    img_id = await read_img(id_card)

    # 2. Liveness Check (The Gatekeeper)
    liveness_score = engine.check_liveness(img_selfie)
    if liveness_score < 0.90:
        raise HTTPException(status_code=403, detail="Liveness check failed (Spoof detected)")

    # 3. Face Matching
    match_score, error = engine.detect_and_match(img_selfie, img_id)
    if error:
        raise HTTPException(status_code=400, detail=error)

    return {
        "status": "success",
        "match_score": round(match_score, 4),
        "is_match": match_score > 0.45,
        "liveness_verified": True
    }
    img = cv2.imread(image_path)
    
    # Step 1: Detect
    face_data = detector.detect_main_face(img)
    if face_data["det_score"] < 0.6:
        return "No clear face detected. Please try again."

    # Step 2: Extract Bounding Box for Liveness
    # (Pass the crop to our previously built AntiSpoofPredict)
    
    # Step 3: Get Embedding for Matching
    # (The Matcher uses the same face_data to stay efficient)
    embedding = matcher.get_embedding(img)
    
    return "Face Processed Successfully"