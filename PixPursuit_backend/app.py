"""
app.py

This is the main entry point for the PixPursuit application. It sets up the FastAPI application and includes all the necessary routes and middleware.

Modules:
- fastapi: The main framework used for building the API.
- config.celery_config: Contains the configuration for the Celery task queue.
- fastapi.middleware.cors: Middleware for handling Cross-Origin Resource Sharing (CORS).
- api.routes: Contains all the route modules for the application.
- api.middleware: Contains all the middleware modules for the application.

The application uses the FastAPI framework and sets up CORS middleware to allow requests from any origin. It also includes several routers for handling different types of requests, such as authentication, image handling, album management, content management, and downloads.

The application also sets up a Celery task queue and automatically discovers tasks in the 'services' and 'data' modules.

The LoggingMiddleware is added to the application to handle request and response logging.

If the script is run directly, it starts an Uvicorn server on host 0.0.0.0 and port 8000.

This file is part of the PixPursuit project and is responsible for setting up and running the main application.
"""

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
