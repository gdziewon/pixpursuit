from fastapi import FastAPI
from config.celery_config import celery
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth, albums, content, download, images
from api.middleware import LoggingMiddleware

app = FastAPI()

celery.autodiscover_tasks(['services', 'data'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(images.router)
app.include_router(albums.router)
app.include_router(content.router)
app.include_router(download.router)
app.add_middleware(LoggingMiddleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
