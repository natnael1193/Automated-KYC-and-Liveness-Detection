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

@liveness_router.post("/verify-with-ocr")
async def verify_identity_with_ocr(selfie: UploadFile = File(...), id_card: UploadFile = File(...)):
    # 1. Read files into OpenCV format
    img_selfie = await read_img(selfie)
    img_id = await read_img(id_card)
    
    match_score, live_score, id_data, error = engine.process_verification(img_selfie, img_id)
    
    # Logic: It's only a full success if biometric matches AND ID is readable
    is_success = (live_score > 0.85) and (match_score > 0.45) and (id_data['id_number'] != "Not Found")

    return {
        "verified": is_success,
        "identity": id_data,
        "scores": {
            "biometric_match": round(match_score, 4),
            "liveness": round(live_score, 4)
        }
    }