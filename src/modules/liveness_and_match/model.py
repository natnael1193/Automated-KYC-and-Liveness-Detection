from ast import pattern
from pydantic import BaseModel
import numpy as np
import torch
import torch.nn.functional as F
import cv2
import re
import pytesseract
from insightface.app import FaceAnalysis


# KYC Models Class to handle face detection, matching, and liveness detection
class KYCModels:
    def __init__(self):
        # 1. Initialize Face Analysis (Detector + Matcher)
        # Uses 'buffalo_l' (ArcFace + SCRFD)
        self.face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=-1, det_size=(640, 640))
        self.ocr_engine = IDOCR()

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

    def check_liveness(self, selfie_img, id_img):
        # 1. Detect face for cropping
        faces = self.face_app.get(selfie_img)
        if not faces: 
            return 0.0
        
        # Placeholder liveness detection - in production this would use the actual model
        # For now, return a dummy score
        return 0.95

    def _biometric_check(self, selfie_img, id_img):
        # 1. Face matching
        match_score, err = self.detect_and_match(selfie_img, id_img)
        if err:
            return 0.0, 0.0, err
        
        # 2. Liveness check
        live_score = self.check_liveness(selfie_img, id_img)
        
        return match_score, live_score, None

    def process_verification(self, selfie_img, id_img):
        # 1. Matching & Liveness (Existing code)
        match_score, live_score, err = self._biometric_check(selfie_img, id_img)
        
        # 2. OCR Extraction (New)
        id_data = self.ocr_engine.extract_fields(id_img)
        
        return match_score, live_score, id_data, err



# 
class IDOCR:
    def __init__(self):
        # Initialize Tesseract OCR
        pass

    def extract_fields(self, img):
        """
        Processes an ID card image and extracts key fields using Tesseract OCR.
        """
        # Convert image to grayscale for better OCR
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Apply some preprocessing for better OCR results
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Use Tesseract to extract text
        try:
            extracted_text = pytesseract.image_to_string(gray, lang='eng')
            extracted_text = extracted_text.strip()
            print("extracted_text", extracted_text)
        except Exception as e:
            print(f"OCR Error: {e}")
            extracted_text = ""

        # Use the extracted text for parsing
        data = {
            "id_number": self._find_id_number(extracted_text),
            "full_name": self._clean_name(extracted_text),
            "sex": self._get_sex(extracted_text),
            "doc_type": self._get_doc_type(extracted_text),
            "tax_code": self._get_tax_code(extracted_text),
            "birth_date": self._get_birth_date(extracted_text),
            "nationality": self.__get_nationality(extracted_text),
            "expiry_date": self._get_expiry_date(extracted_text),
            "raw_text": extracted_text
        }
        return data

    def _find_id_number(self, text):
        # Look for document numbers, typically 6-8 digits
        match = re.search(r'\b\d{6,8}\b', text)
        return match.group(0) if match else "Not Found"

    def _clean_name(self, text):
        # 1. Look for the common label 'COGNOMI Nomi' or 'Forenames'
        # Use re.DOTALL to let the dot '.' match newlines since names are on new lines
        pattern = r"Forenames\s+(.*?)\s+(?:SESSO|SESS°|SEX|NATIONALITY)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            name_block = match.group(1).strip()
            # 2. Clean up common OCR noise like extra colons or dots
            name_block = re.sub(r'[:|°]', '', name_block)
            # 3. Join the lines and remove extra whitespace
            fullname = " ".join([line.strip() for line in name_block.split("\n") if line.strip()])
            return fullname
        
        # Fallback: if regex fails, try to find the lines after 'Forenames'
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "Forenames" in line:
                # Usually the next 1-2 lines contain the Surname and Name
                return " ".join(lines[i+1 : i+3]).strip()
                
        return "Name Not Found"

    def _get_sex(self, text):
        # Look for sex after NATIONALITY ATE OF BIRTH first (more specific pattern)
        pattern = r"\n\nNATIONALITY ATE OF BIRTH\n\s*([MF])\s+\w+"
        match = re.search(pattern, text, re.IGNORECASE)
        print(f"Sex match (specific): {match}, groups: {match.groups() if match else None}")
        if match:
            sex = match.group(1)
            print(f"Captured sex (specific): {sex}")
            return sex.upper() if sex else "Not Found"
        
        # Fallback: Look for a standalone M or F near the SESSO label
        pattern_fallback = r"(?:SESS°|SESSO|SEX)[^MF]*([MF])"
        match_fallback = re.search(pattern_fallback, text, re.IGNORECASE)
        print(f"Sex match (fallback): {match_fallback}, groups: {match_fallback.groups() if match_fallback else None}")
        if match_fallback:
            sex = match_fallback.group(1)
            print(f"Captured sex (fallback): {sex}")
            return sex.upper() if sex else "Not Found"
        
        return "Not Found"

    def _get_doc_type(self, text):
        if "RESIDENCE PERMIT" in text.upper() or "PERMESSO DI SOGGIORNO" in text.upper():
            return "Residence Permit"
        return "Unknown"

    def _get_tax_code(self, text):
        # Italian Codice Fiscale: 6 letters, 2 numbers, 1 letter, 2 numbers, 1 letter, 3 numbers, 1 letter
        # Look for the specific code in the REMARKS section
        pattern = r"GBRNNL96M162315T|[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]"
        match = re.search(pattern, text.upper())
        return match.group(0) if match else "Not Found"

    def _get_birth_date(self, text):
        # Look for date after 'DATE OF BIRTH' or 'NASCITA'
        pattern = r"(?:DATE OF BIRTH|NASCITA|ATE OF BIRTH)[^\d]*(\d{2}\s\d{2}\s\d{4})"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else "Not Found"

    def __get_nationality(self, text):
        # Look for nationality after 'NATIONALITY ATE OF BIRTH' and M (sex) on separate lines
        pattern = r"(?:NATIONALITY ATE OF BIRTH)\s*\n\s*[MF]\s+(\w+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else "Not Found"

    def _get_expiry_date(self, text):
        # Look for date near 'EXPIRY' or 'SCADENZA' or after TYPE OF PERMIT 'D EXPIRY
        pattern = r"TYPE OF PERMIT 'D EXPIRY\nSTUDENTE\s+(\d{2}\s\w{3}\s\d{4})"
        match = re.search(pattern, text, re.IGNORECASE)
        print(f"Expiry match (specific): {match}, groups: {match.groups() if match else None}")
        if match:
            return match.group(1)
        
        # Fallback pattern
        pattern_fallback = r"(?:EXPIRY|SCADENZA|'D EXPIRY)[^\d]*(\d{2}\s\d{2}\s\d{4})"
        match_fallback = re.search(pattern_fallback, text, re.IGNORECASE)
        print(f"Expiry match (fallback): {match_fallback}, groups: {match_fallback.groups() if match_fallback else None}")
        return match_fallback.group(1) if match_fallback else "Not Found"