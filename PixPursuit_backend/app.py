from fastapi import FastAPI
from config.celery_config import celery
from fastapi.middleware.cors import CORSMiddleware
from routes import albums, content, download, images, auth, sharepoint
import os

app = FastAPI()

current_file_path = os.path.abspath(__file__)
generated_files_dir = os.path.join(os.path.dirname(current_file_path), 'generated')
if not os.path.exists(generated_files_dir):
    os.makedirs(generated_files_dir)

celery.autodiscover_tasks(['tag_prediction.tag_prediction_tools', 'databases.face_operations',
                           'data_extraction.object_detection', 'data_extraction.face_detection', 'data_extraction.feature_extraction'])

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
