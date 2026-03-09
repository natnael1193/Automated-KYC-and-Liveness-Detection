import re

raw_text = """: COGNOMI Nomi aaranes Forenames
GEBREMIC
Natnael Solomon

SESS° t CITTADINANZA / DATA DINASCITA /

NATIONALITY ATE OF BIRTH
M ETH 16 08 1996
TIPO DI PERMESSO / SCADENZA DOCUMENTO |
TYPE OF PERMIT 'D EXPIRY
STUDENTE 06 it 2025

ANNOTAZIONI / REMARKS
GBRNNL96M162315T

505718

RESIDENCE PERMIT"""

def _find_id_number(text):
    excluded_keywords = ["FORENAMES", "SURNAME", "NATIONALITY", "RESIDENCE", "PERMIT", "DOCUMENT", "REMARKS", "ANNOTAZIONI"]
    matches = re.findall(r'\b[A-Z0-9]{8,15}\b', text.upper())
    for m in matches:
        if m not in excluded_keywords and any(char.isdigit() for char in m):
            return m
    return "Not Found"

def _clean_name(text):
    pattern = r"(?:Forenames|Nomi)\s+(.*?)\s+(?:SESSO|SESS°|SEX|NATIONALITY|CITTADINANZA)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        name_block = match.group(1).strip()
        name_block = re.sub(r'[:|°]', '', name_block)
        lines = [line.strip() for line in name_block.split("\n") if line.strip()]
        lines = [l for l in lines if not any(k in l.upper() for k in ["COGNOMI", "SURNAMES"])]
        fullname = " ".join(lines)
        return fullname
    
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "Forenames" in line or "Nomi" in line:
            return " ".join(lines[i+1 : i+3]).strip()
            
    return "Name Not Found"

def _get_sex(text):
    pattern = r"(?:SESSO|SEX).*?\b([MF])\b"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1).upper() if match else "Not Found"

def _get_birth_date(text):
    pattern = r"(?:DATE|NASCITA).*?(\d{2}[\s/-]\d{2}[\s/-]\d{4})"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return match.group(1) if match else "Not Found"

def _get_expiry_date(text):
    pattern = r"(?:EXPIRY|SCADENZA).*?(\d{2}[\s/-][a-zA-Z0-9]{2}[\s/-]\d{4})"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        date_str = match.group(1)
        date_str = date_str.replace("it", "11").replace("IT", "11").replace("ll", "11")
        return date_str
    return "Not Found"

def _get_tax_code(text):
    # Italian Codice Fiscale: 16 chars.
    # Often it appears near 'REMARKS' or 'ANNOTAZIONI'
    pattern = r"\b[A-Z0-9]{16}\b"
    matches = re.findall(pattern, text.upper())
    for m in matches:
        if any(char.isdigit() for char in m) and any(char.isalpha() for char in m):
            return m
    return "Not Found"

print(f"ID Number: {_find_id_number(raw_text)}")
print(f"Full Name: {_clean_name(raw_text)}")
print(f"Sex: {_get_sex(raw_text)}")
print(f"Birth Date: {_get_birth_date(raw_text)}")
print(f"Expiry Date: {_get_expiry_date(raw_text)}")
print(f"Tax Code: {_get_tax_code(raw_text)}")
