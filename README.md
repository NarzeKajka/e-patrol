# e-Patrol

**e-Patrol** is an application developed as part of a master's thesis focused on the use of object detection algorithms in systems for reporting irregularities in urban spaces.

The system allows users to report urban issues by submitting a photograph, location and description. An object detection model analyses the submitted photograph and suggests a report category, which the user confirms or corrects before the report is saved.

## Master's Thesis

**Title:**  
_Zastosowanie algorytmów detekcji obrazu w systemach zgłaszania nieprawidłowości w przestrzeni miejskiej z wykorzystaniem aplikacji mobilnej i miejskiego monitoringu_

**Title (English):**  
_Application of image detection algorithms in systems for reporting irregularities in urban space using a mobile application and city monitoring_

The project combines two areas:

- development of the e-Patrol reporting system,
- experimental comparison of selected object detection models.

## Main Idea

```text
User
  ↓
Photo + location + description
  ↓
e-Patrol backend
  ↓
Object detection (YOLOv8s)
  ↓
Suggested category + bounding boxes
  ↓
User confirmation or correction
  ↓
Report saved with both values
```

The model never decides on its own. The suggested category and the category finally chosen by the user are stored separately, so the agreement between them can be measured on real submissions.

## Features

- Registration and login with JWT, session restored on startup
- Creating a report: photograph, location, description
- Image validation and storage on the server
- Automatic category suggestion from the detection model, confirmed or corrected by the user
- Detections drawn over the analysed photograph
- Report history with details and photograph
- Access control — a user sees only their own reports

Report status is stored and displayed, but cannot be changed yet.

## Dataset

The application recognises three categories of urban issues:

| Class         | Source dataset                              |
| ------------- | ------------------------------------------- |
| `road_damage` | RDD2022 — Czech Republic and Norway subsets |
| `waste`       | Illegal Dumping dataset                     |
| `graffiti`    | STORM dataset                               |

Only European subsets of RDD2022 were used, because of comparable road construction standards and signage. The four original damage classes (`D00`, `D10`, `D20`, `D40`) were merged into a single `road_damage` class, and the seven waste classes into a single `waste` class — the application asks the user to choose a report category, not a damage subtype.

Preparation pipeline (`scripts/dataset/`):

1. selection of candidate images from each source,
2. near-duplicate detection using perceptual hashing (pHash),
3. conversion of annotations to YOLO format,
4. group-aware split into train / validation / test (70 / 15 / 15, seed 42), so that near-duplicate images never end up in different subsets,
5. visual audit of samples from each class.

The result is a dataset of roughly 3000 annotated images. Source datasets and the generated dataset are not stored in this repository.

## Experimental Comparison

Three architectures were trained and compared under identical conditions — 100 epochs, starting from COCO-pretrained weights, on the same data split:

- YOLOv5s,
- YOLOv8s,
- SSDLite320 with a MobileNetV3 backbone.

All three are PyTorch implementations, so the measured inference times compare architectures rather than frameworks.

Evaluation criteria:

- mAP@0.5 and mAP@0.5:0.95, precision and recall per class,
- inference time per image and model file size,
- **category accuracy** — how often the model suggested the category the user would choose. This is the application-level metric and it is computed with the same rule the backend uses (the most confident detection wins).

Additional experiments covered the influence of inference resolution, the confidence threshold, and a controlled retraining run at a higher input resolution.

Two findings shaped the implementation:

- **The confidence threshold is set to 0.05**, not the usual 0.25. Cross-class confusion turned out to be negligible; almost every error was "nothing detected". Lowering the threshold raises category suggestion accuracy from about 88% to about 96%, at the cost of precision that the user never sees, because the application shows one category rather than a list of boxes.
- **The optimal input resolution depends on the size of the source images.** The Czech subset (600×600) and the Norwegian subset (3643×2041) react to resolution changes in opposite directions, so a single global setting cannot serve a heterogeneous dataset.

**YOLOv8s at 640 px** is the model integrated with the application. Full results, tables and charts are part of the thesis.

## Known Limitations

- Each class comes from a different source dataset, and each source annotates only its own class. A photograph of a road with a bag of rubbish on the shoulder has that bag as background, not as an object. The model may therefore learn to recognise which dataset an image comes from rather than what it shows. The test set shares this weakness, so the metrics alone will not reveal it.
- The dataset contains no images without any problem, so the models were never trained to answer "there is nothing here".
- Verifying the models under real conditions would require a few hundred photographs taken with a phone, annotated with all three classes at once, and used exclusively as an additional test set.
- The backend stores bounding boxes in pixel coordinates, but not the dimensions of the analysed image, so boxes can be drawn during analysis but not re-drawn for an already saved report.
- The Flutter client points at `http://127.0.0.1:8000`, which works on a simulator running on the same machine as the backend.

## Architecture

```text
┌─────────────────────┐
│       Flutter       │
│      Frontend       │
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│       FastAPI       │
│       Backend       │
├─────────────────────┤
│ Authentication      │
│ Reports             │
│ Image handling      │
│ Object detection    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     SQLAlchemy      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     PostgreSQL      │
│      (Docker)       │
└─────────────────────┘
```

The model runs on the server, not on the device. The weights are loaded once, on the first request, and stay in memory.

## Data Model

```text
User
  │
  └── Report
        │
        └── ReportImage
              │
              └── Analysis
                    │
                    ├── model name
                    ├── model version
                    ├── inference time
                    │
                    └── Detection
                          ├── class
                          ├── confidence
                          └── bounding box
```

This structure allows multiple models to analyse the same image and makes it possible to store and compare their results.

## Technology Stack

### Frontend

- Flutter
- Dart

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database

- PostgreSQL
- Docker

### Authentication

- JWT
- Argon2 password hashing

### Computer Vision

- Ultralytics (YOLOv5, YOLOv8)
- PyTorch and torchvision (MobileNet SSD)
- Pillow
- Training carried out in Google Colab

## Local Development

### Requirements

- Python 3.10+
- Docker
- Flutter
- Git

### 1. Clone the repository

```bash
git clone https://github.com/NarzeKajka/e-patrol.git
cd e-patrol
```

### 2. Start PostgreSQL

```bash
docker compose up -d
```

### 3. Configure the backend

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://epatrol:epatrol_dev@localhost:5432/epatrol
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DETECTION_CONFIDENCE_THRESHOLD=0.05
```

### 4. Add the model weights

The trained weights are not stored in the repository. Copy the `best.pt` file produced by training into:

```text
models/best.pt
```

A different location can be set with `DETECTION_MODEL_PATH` in `.env`. Without the weights file the whole application works, but `POST /analysis/predict` answers with `503`.

### 5. Apply database migrations

```bash
alembic upgrade head
```

### 6. Run the backend

```bash
uvicorn app.main:app --reload
```

The development API is available at `http://127.0.0.1:8000`, and the interactive documentation at `http://127.0.0.1:8000/docs`.

### 7. Run the application

```bash
cd frontend
flutter pub get
flutter run
```

### 8. Run tests

Backend — a separate PostgreSQL database named `epatrol_test` is used by the test suite:

```bash
cd backend
pytest -v
```

Frontend:

```bash
cd frontend
flutter test
```

## Future Development

- administrative report management and status changes,
- analysis of additional types of urban irregularities,
- contextual detection of improper parking,
- object storage for production image handling,
- anonymisation of faces and vehicle licence plates,
- processing video streams from urban monitoring systems or municipal vehicles.

Integration with real urban monitoring infrastructure is outside the current implementation scope and is considered a direction for further development.

## License

This repository contains software developed for academic purposes as part of a master's thesis.

Licensing terms for external datasets and pretrained models are governed by their respective authors and sources.
