from minio import Minio
from minio.error import S3Error
from fastapi import FastAPI
from datetime import datetime
import logging
import os
import io

app = FastAPI(title="NEXUS Consent API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "audit.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    force=True
)

consents = {}

minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False
)

BUCKET_NAME = "medical-data"

@app.on_event("startup")
def init_minio():
    try:
        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
            logging.info(f"BUCKET_CREATED name={BUCKET_NAME}")
    except Exception as e:
        logging.error(f"MINIO_INIT_ERROR {e}")

@app.post("/consent/grant")
def grant_consent(patient_id: str):
    consents[patient_id] = {
        "granted": True,
        "timestamp": datetime.utcnow().isoformat()
    }
    logging.info(f"CONSENT_GRANTED patient_id={patient_id}")
    return {"status": "granted", "patient_id": patient_id}

@app.post("/consent/revoke")
def revoke_consent(patient_id: str):
    consents[patient_id] = {
        "granted": False,
        "timestamp": datetime.utcnow().isoformat()
    }
    logging.info(f"CONSENT_REVOKED patient_id={patient_id}")
    return {"status": "revoked", "patient_id": patient_id}

@app.get("/consent/{patient_id}")
def check_consent(patient_id: str):
    logging.info(f"CONSENT_CHECK patient_id={patient_id}")
    return consents.get(patient_id, {"granted": False})

@app.get("/data/access/{patient_id}")
def access_data(patient_id: str):
    consent = consents.get(patient_id)

    if not consent or not consent["granted"]:
        logging.warning(f"ACCESS_DENIED patient_id={patient_id}")
        return {
            "access": "denied",
            "reason": "No valid consent"
        }

    logging.info(f"ACCESS_GRANTED patient_id={patient_id}")
    return {
        "access": "granted",
        "message": "Simulated access to encrypted medical data"
    }

@app.post("/data/upload/{patient_id}")
def upload_data(patient_id: str):
    consent = consents.get(patient_id)

    if not consent or not consent["granted"]:
        logging.warning(f"UPLOAD_DENIED patient_id={patient_id}")
        return {"status": "denied", "reason": "No consent"}

    data = b"Encrypted medical imaging data (simulated)"
    object_name = f"{patient_id}/scan.txt"

    try:
        minio_client.put_object(
            BUCKET_NAME,
            object_name,
            data=io.BytesIO(data),
            length=len(data),
            content_type="text/plain"
        )
    except Exception as e:
        logging.error(f"UPLOAD_ERROR patient_id={patient_id} error={e}")
        return {"status": "error", "detail": str(e)}

    logging.info(f"UPLOAD_OK patient_id={patient_id} object={object_name}")
    return {"status": "uploaded", "object": object_name}
