# kyc-aml-document-classifier

ML model to detect Aadhaar/PAN/VoterID/DL/Passport and wrapped in microservice

See the repository README for intended project structure. This branch adds a scaffold (dataset generator stub, training/inference stubs, FastAPI microservice, Dockerfile, and .gitignore).

How to run locally (quickstart):
1. Create & activate a venv:
   python -m venv .venv
   source .venv/bin/activate
2. Install dependencies:
   pip install -r requirements.txt
3. Generate a small synthetic dataset:
   python dataset_generator/generate_synthetic_data.py -n 5
4. (Optional) Train a tiny model:
   python training/train_classifier.py --data dataset_generator/output_dataset --epochs 1
5. Run API:
   uvicorn api.main:app --reload --port 8000
