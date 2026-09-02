# e-Patrol

**e-Patrol** is a web application developed as part of a master's thesis focused on the use of object detection algorithms in systems for reporting irregularities in urban spaces.

The system is designed to allow users to report urban issues by submitting a photograph, location and description. Image analysis methods are used to support the reporting process by automatically detecting selected types of objects and infrastructure damage.

## Master's Thesis

**Title:**  
_Zastosowanie algorytmów detekcji obrazu w systemach zgłaszania nieprawidłowości w przestrzeni miejskiej z wykorzystaniem aplikacji webowej_

**Title (English):**
_Application of image detection algorithms in systems for reporting irregularities in urban space using a mobile application and city monitoring_

The project combines two main areas:

- development of the e-Patrol reporting system,
- experimental comparison of selected object detection models.

The planned experimental evaluation compares:

- YOLOv5,
- YOLOv8,
- MobileNet SSD.

The models are evaluated using metrics such as detection accuracy, precision, recall and inference performance.

## Main Idea

The basic reporting workflow is:

```text
User
  ↓
Photo + location + description
  ↓
e-Patrol backend
  ↓
Image analysis
  ↓
Detected objects / urban issues
  ↓
AI suggestion
  ↓
User confirmation
  ↓
Report
```

The AI module automatically analyses submitted images to identify relevant urban issues and assist in validating reports. Detection results may be used to pre-fill the report category, flag potentially inconsistent submissions, and reduce low-quality or irrelevant reports. The user can confirm or correct the AI-generated result before final submission.

## Planned Features

### User

- [x] User registration
- [x] User authentication using JWT
- [x] Creating reports
- [x] Geographic coordinates for reports
- [x] Uploading report images
- [x] Image validation
- [x] Viewing user's reports
- [x] Report ownership and access control
- [ ] AI-assisted image analysis
- [ ] AI suggestion confirmation
- [ ] Report status tracking
- [ ] Flutter user interface

### AI

- [x] Database structure for storing analyses and detections
- [x] API support for storing detection results
- [ ] Dataset preparation
- [ ] YOLOv8 training and evaluation
- [ ] YOLOv5 training and evaluation
- [ ] MobileNet SSD training and evaluation
- [ ] Model comparison
- [ ] Integration of the selected model with the application

## Object Detection

The research part of the project investigates the suitability of different object detection architectures for analysing images of urban environments.

The main experimental dataset is planned to be **RDD2022 (Road Damage Dataset 2022)**, containing annotated examples of road damage.

The analysed road damage classes include:

- longitudinal cracks,
- transverse cracks,
- alligator cracks,
- potholes.

All compared models will be evaluated on a common dataset split to provide comparable experimental conditions.

Additional datasets and urban issue categories may be investigated as extensions of the system.

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
│ AI integration      │
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

The backend follows a modular structure separating API endpoints, database models, schemas, services and AI-related functionality.

## Data Model

The main image-analysis relationship is:

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

This structure allows multiple AI models to analyse the same image and makes it possible to store and compare their results.

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

Planned:

- YOLOv5
- YOLOv8
- MobileNet SSD
- OpenCV

## Project Structure

```text
e-patrol/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── ai/
│   ├── alembic/
│   └── tests/
│
├── frontend/
│
├── docs/
│
├── uploads/
│
├── docker-compose.yml
└── README.md
```

Local uploads, environment variables, datasets and other generated data are not stored in the Git repository.

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
```

### 4. Apply database migrations

```bash
alembic upgrade head
```

### 5. Run the backend

```bash
uvicorn app.main:app --reload
```

The development API is available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Run tests

A separate PostgreSQL database named `epatrol_test` is used by the automated test suite.

```bash
pytest -v
```

## Current Status

The backend foundation is operational, including authentication, report management, image upload and storage of AI analysis results.

Current development is focused on preparing the computer vision experiment and training the first object detection model.

The Flutter user interface and final AI integration are under development.

## Future Development

Potential extensions include:

- analysis of additional types of urban irregularities,
- contextual detection of improper parking,
- administrative report management,
- object storage for production image handling,
- anonymisation of faces and vehicle licence plates,
- processing video streams from urban monitoring systems or municipal vehicles.

Integration with real urban monitoring infrastructure is outside the current implementation scope and is considered a potential direction for further development.

## License

This repository contains software developed for academic purposes as part of a master's thesis.

Licensing terms for external datasets and pretrained models are governed by their respective authors and sources.
