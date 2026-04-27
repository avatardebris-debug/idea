# Video Management Platform

A full-stack video management system built with FastAPI (backend) and React + TypeScript (frontend).

## 📋 Features

### Backend
- **FastAPI** REST API with automatic OpenAPI documentation
- **SQLAlchemy** ORM with SQLite database
- **Pydantic** data validation and serialization
- **CRUD operations** for Videos, Tables, and Fields
- **Async database** operations with aiosqlite

### Frontend
- **React 18** with TypeScript
- **React Router** for navigation
- **Custom API client** with TypeScript types
- **Responsive design** with CSS variables
- **Search and filter** functionality
- **Pagination** for large datasets

## 🏗️ Project Structure

```
workspace/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── fields.py
│   │       ├── tables.py
│   │       └── videos.py
│   ├── scripts/
│   │   └── seed.py
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_integration.py
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── package.json
    └── src/
        ├── App.tsx
        ├── api.ts
        ├── index.css
        ├── main.tsx
        └── components/
            ├── Fields.tsx
            ├── VideoForm.tsx
            └── VideoList.tsx
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` and the documentation at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📚 API Endpoints

### Videos
- `GET /api/videos` - List all videos (with pagination, search, and filter)
- `GET /api/videos/{id}` - Get a specific video
- `POST /api/videos` - Create a new video
- `PUT /api/videos/{id}` - Update a video
- `DELETE /api/videos/{id}` - Delete a video

### Tables
- `GET /api/tables` - List all tables
- `GET /api/tables/{id}` - Get a specific table
- `POST /api/tables` - Create a new table
- `PUT /api/tables/{id}` - Update a table
- `DELETE /api/tables/{id}` - Delete a table

### Fields
- `GET /api/fields?table_id={id}` - List fields for a table
- `POST /api/fields` - Create a new field
- `DELETE /api/fields/{id}` - Delete a field

## 🧪 Testing

Run the backend tests:
```bash
cd backend
pytest
```

Run the frontend tests:
```bash
cd frontend
npm test
```

## 📦 Data Models

### Video
- `id`: UUID (primary key)
- `title`: String (required)
- `description`: String (optional)
- `status`: Enum (draft, scheduled, publishing, published, failed)
- `tags`: List of strings
- `publish_date`: DateTime (optional)
- `thumbnail_url`: String (optional)
- `youtube_video_id`: String (optional)
- `custom_fields`: JSON object

### Table
- `id`: UUID (primary key)
- `name`: String (required)
- `description`: String (optional)
- `created_at`: DateTime

### Field
- `id`: UUID (primary key)
- `table_id`: UUID (foreign key)
- `name`: String (required)
- `field_type`: Enum (TEXT, NUMBER, DATE, URL, SELECT, TAGS)
- `is_required`: Boolean

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the backend directory:

```
DATABASE_URL=sqlite:///./video_management.db
SECRET_KEY=your-secret-key
```

## 📝 License

MIT License

## 👥 Credits

Built with FastAPI, React, and TypeScript.
