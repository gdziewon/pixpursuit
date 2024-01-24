from fastapi import FastAPI
from databases.sharepoint_client import SharePointClient
from config.logging_config import setup_logging
from config.celery_config import celery
from fastapi.middleware.cors import CORSMiddleware
from routes import albums, content, download, images, auth, sharepoint

app = FastAPI()
celery.autodiscover_tasks(['tag_prediction_tools', 'database_tools', 'object_detection', 'face_detection', 'feature_extraction'])
logger = setup_logging(__name__)
sharepoint_client = SharePointClient()

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
app.include_router(sharepoint.router)
app.include_router(content.router)
app.include_router(download.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
