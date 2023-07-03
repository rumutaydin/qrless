from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schema, database
from ..utils import token_decode as tok
from array import array
import os
from PIL import Image
import sys
import time
import base64
import io
from dotenv import load_dotenv


router = APIRouter()

load_dotenv()


subscription_key = os.getenv("VISION_KEY")
endpoint = os.getenv("VISION_ENDPOINT")

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


@router.post("/detect-brand", response_model=schema.Brand)
def detect_brand(img: schema.ImageData, db: Session = Depends(database.get_db), current_user: schema.User = Depends(tok.get_current_user)):
    image = img.image_base64
    image_bytes = base64.b64decode(image)
    image_features = [VisualFeatureTypes.brands]
    image_stream = io.BytesIO(image_bytes)

    result = computervision_client.analyze_image_in_stream(image_stream, image_features)

    if len(result.brands) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No brands detected."
        )
    else:
        brand = result.brands[0]
        print(brand)
        brand_db = crud.check_matching_brand(db, brand.name)
        if not brand_db:
            raise HTTPException(status_code=400, detail="Detected brand is not present in database")
        added_scan = crud.update_scanhistory(db, current_user.id, brand_db.id)
        print("***************************")
        print(added_scan.id)
        print(added_scan.user_id)
        print(added_scan.brand_id)
        print(added_scan.scan_time)



        return brand_db





