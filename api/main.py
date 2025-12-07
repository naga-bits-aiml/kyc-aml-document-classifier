"""FastAPI inference API."""
import os
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from inference.inference_engine import InferenceEngine

app = FastAPI(title="KYC/AML Document Classifier")

# Change model_path if you save trained model elsewhere
engine = InferenceEngine(model_path="training/model/efficientnet_model.h5")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # accept image uploads and return predicted class label + confidence
    suffix = os.path.splitext(file.filename)[1].lower()
    if suffix not in [".png", ".jpg", ".jpeg", ".bmp"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        result = engine.predict(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return JSONResponse(content=result)