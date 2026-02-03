from fastapi import FastAPI
from app.routes import admin, auth, course, enrollment, user

app = FastAPI(title="Course Enrollment Platform")


app.include_router(auth.router)
app.include_router(course.router)
app.include_router(enrollment.router)
app.include_router(admin.router)
app.include_router(user.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Course Enrollment Platform!"
    }
