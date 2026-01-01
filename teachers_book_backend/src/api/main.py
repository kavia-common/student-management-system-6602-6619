from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router as api_router

app = FastAPI(
    title="Teacher's Book API",
    description="Backend API for managing students and customizable fields.",
    version="1.0.0",
    openapi_tags=[
        {"name": "students", "description": "Operations on students"},
        {"name": "custom_fields", "description": "Manage custom fields/attributes"},
        {"name": "student_field_values", "description": "Assign/update field values for students"}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/", tags=["system"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}
