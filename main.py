import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document
from schemas import Lead

app = FastAPI(title="Video Editing Courses API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Video Editing Courses Backend Running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

# Models for content (can be static for landing page)
class Course(BaseModel):
    id: str
    title: str
    subtitle: str
    price: float
    features: List[str]
    level: str
    duration_weeks: int
    image: Optional[str] = None

# Sample courses to display on landing page
COURSES: List[Course] = [
    Course(
        id="starter",
        title="Базовый монтаж",
        subtitle="Освойте основы монтажа и создавайте ролики за 2 недели",
        price=49.0,
        features=["Интерфейс Premiere Pro", "Работа с таймлайном", "С переходами и музыкой", "Экспорт роликов"],
        level="Новичок",
        duration_weeks=2,
        image=None,
    ),
    Course(
        id="pro",
        title="Профи монтаж",
        subtitle="Полный цикл монтажа: от сырья до готового видео",
        price=149.0,
        features=["Цветокоррекция", "Работа со звуком", "Motion-графика основы", "Скорость работы"],
        level="Средний",
        duration_weeks=6,
        image=None,
    ),
    Course(
        id="master",
        title="Мастер монтаж",
        subtitle="Креативные приемы и коммерческие проекты",
        price=299.0,
        features=["Сторителлинг", "Кейсы клиентов", "Motion Advanced", "Портфолио и клиенты"],
        level="Продвинутый",
        duration_weeks=10,
        image=None,
    ),
]

@app.get("/api/courses", response_model=List[Course])
def get_courses():
    return COURSES

class LeadIn(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    course_id: Optional[str] = None
    message: Optional[str] = None

@app.post("/api/lead")
def create_lead(lead: LeadIn):
    try:
        lead_doc = Lead(
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            course_id=lead.course_id,
            message=lead.message,
        )
        inserted_id = create_document("lead", lead_doc)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
