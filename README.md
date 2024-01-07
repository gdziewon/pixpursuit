# PixPursuit Project Documentation

## Frontend

Built with Next.js.

## Project Structure

#### `app`

- **albums:** Directory containing pages related to albums.
  - **[albumid]:**
    - **page.js:** Page for a specific album.
  - **add/[parentid]:**
    - **page.js:** Page for adding images to a specific album.
  - **page.js:** Default album page.
- **components:** Reusable React components used throughout the app.
  - **Navbar.jsx:** Navbar component displayed on every page.
  - **NextAuthProvider.jsx:** Authentication provider.
  - **Searcher.jsx:** Search input component for the app.
- **gallery:** Directory containing pages related to the image gallery.
  - **[id]:**
    - **page.js:** Page for a specific image.
  - **upload:**
    - **[albumid]:**
      - **page.js:** Page for adding images to a specific folder.
    - **page.js:** Page for uploading images.
  - **page.js:** Page for the image gallery.
- **favicon.ico:** App favicon.
- **globals.css:** Imports TailwindCSS styles.
- **layout.js:** Defines the layout for the web app.
- **loading.js:** Template for when a component is fetching data.
- **page.js:** Default home page for the website.

#### `pages`

- **API:** Contains API routes for MongoDB connection and authentication.
  - **auth:**
    - **[...nextauth].js:** Authentication route.
  - **addUserTag.js** - Adds a tag from a user to an image.
  - **connectMongo.js** - Connects to MongoDB.
  - **getSingleImage.js** - Gets a single image from MongoDB.
  - **s3.js**
  - **searchSuggestions.js** - Gets search suggestions from MongoDB.

### `public`

- **.img:** Directory containing static images for the website.

### `styles`

- **album_layout_styles.css:** Styles for the album page.

### `utils` - Contains utility functions for the app.

- **getAlbums.js** - Gets all albums from MongoDB.
- **getImages.js** - Gets all images from MongoDB.
- **getSingleImage.js** - Gets a single image from MongoDB.
- **isRootId.js:** - Checks if an album is the root album.

### `.env`

- Contains environment variables.

### Config Files

- Various configuration files for the project. like:
    - 'jsconfig.json',
    - 'tailwind.config.js',
    - 'next.config.js',
    - 'postcss.config.js',
    - 'package.json'

## Installation

To set up the PixPursuit locally, you need to:

    1. Clone the repository.
    2. Navigate to the `frontend` directory.
    3. Run `npm install` to install dependencies.
    4. Create a `.env` file with the required environment variables.

## Running the App

To run the app locally, use the following command in the console:
    ```bash

    npm run dev

## Introduction

This documentation covers PixPursuit, an advanced platform for managing and analyzing images using machine learning technologies.

## Backend

Built with FastAPI, Celery and MongoDB.

## Database Schema Description

### Images Collection (`images`)
- **_id**: Automatically generated unique identifier by MongoDB.
- **image_url**: URL of the image stored in DigitalOcean Spaces.
- **thumbnail_url**: URL of the image thumbnail, also stored in DigitalOcean Spaces.
- **filename**: Unique filename for each image, generated using the uuid library and timestamp.
- **embeddings**: Array of face embeddings (512 double elements), extracted using the Facenet model.
- **embeddings_box**: Rectangular face embedding boxes, extracted using mtcnn.
- **detected_objects**: Array of detected objects on the image by YOLOv8.
- **metadata**: EXIF metadata of the image, such as width, height, and creation date, obtained using the Pillow library.
- **features**: Array of image features (1000 double elements), obtained using the ResNet model.
- **user_tags**: Tags added by the user.
- **user_faces**: Faces added by the user.
- **auto_tags**: Tags added automatically by the TagPredictor model.
- **auto_faces**: Faces added automatically based on embeddings.
- **feedback**: Feedback history for auto_tags.
- **feedback_history**: User's feedback history regarding specific tags.
- **description**: Description of the image added by the user.
- **added_by**: The user who added the image.
- **album_id**: ID of the album to which the image is assigned.

### Tags Collection (`tags`)
- **_id**: Automatically generated unique identifier by MongoDB.
- **name**: Tag name.
- **count**: Number of occurrences of the tag among images.

### Users Collection (`users`)
- **_id**: Automatically generated unique identifier.
- **username**: User's name.
- **password**: User's password, secured with the Argon2 hashing algorithm.

### Faces Collection (`faces`)
- **_id**: Automatically generated unique identifier.
- **group**: The group to which the face has been assigned based on embeddings.

### Albums Collection (`albums`)
- **_id**: Automatically generated unique identifier of the album.
- **name**: Name of the album.
- **parent**: ID of the parent album.
- **sons**: List of IDs of child albums.
- **images**: List of IDs of images contained in the album.

## Integration of Database Schema with the Application

The data stored in the MongoDB database is an integral part of PixPursuit's functionality. This section explains how different database fields are used within the application.

### Using Image Data
- **_id, image_url, thumbnail_url, filename**: Essential for image management.
- **embeddings, embeddings_box**: Used for face recognition and grouping.
- **detected_objects**: Basis for automatic tagging and searching.
- **metadata**: Provides additional information about the image.
- **features**: Used for advanced analysis and classification of images.
- **user_tags, auto_tags, user_faces, auto_faces**: Manage tags and faces.
- **feedback, feedback_history**: Influences the machine learning process.
- **description, added_by, album_id**: Supports organization and sharing features.

### Using Other Collections
- **Tags**: Track popularity and manage tags.
- **Users**: Authentication and account management.
- **Faces**: Face recognition and analysis.
- **Albums**: Organize images into collections.

## Machine Learning Models and Their Role

### TagPredictor Model
- **Functionality**: Automatically generates tags for images.
- **Architecture**: Neural network with linear and normalizing layers.
- **Training**: Based on tagged image data and user feedback.
- **Integration**: Updated with each image tagging.

### Other Models
- **Facial Detection Model (Facenet)**
- **Object Detection Model (YOLOv8)**
- **Features Extraction Model (ResNet50)**

## API Endpoints Documentation for PixPursuit

### 1. POST `/token`

**Functionality**: Authenticates a user and provides an access token.

**Input**:
- `username`: String (from form data).
- `password`: String (from form data).

**Response**:
- `access_token`: String (JWT token).
- `token_type`: String (typically "bearer").
- `name`: String (username of the authenticated user).

**Error Handling**: Returns HTTP 401 if authentication fails.

### 2. POST `/process-images`

**Functionality**: Processes a batch of uploaded images.

**Input**:
- `images`: List of UploadFile objects.
- `album_id`: String (optional, ID of the album to add images to).
- `current_user`: User object from authentication context.

**Response**:
- `message`: String (confirmation message).
- `inserted_ids`: List of String (IDs of inserted images).

**Error Handling**: Returns HTTP 400 if no images are provided.

### 3. POST `/add-user-tag`

**Functionality**: Adds user-defined tags to an image.

**Input**:
- `inserted_id`: String (ID of the image).
- `tags`: List of String (tags to add).

**Response**:
- `message`: String (confirmation message).

**Error Handling**: Returns HTTP 500 if adding tags fails.

### 4. POST `/feedback-on-tags`

**Functionality**: Adds user feedback on automatically generated tags.

**Input**:
- `inserted_id`: String (ID of the image).
- `feedback`: Dictionary (tag as key, boolean as value indicating correctness).

**Response**:
- `message`: String (confirmation message).

**Error Handling**: Returns HTTP 500 if adding feedback fails.

### 5. POST `/add-description`

**Functionality**: Adds a description to an image.

**Input**:
- `inserted_id`: String (ID of the image).
- `description`: String (description text).

**Response**:
- `message`: String (confirmation message).

**Error Handling**: Returns HTTP 500 if adding description fails.

### 6. POST `/create-album`

**Functionality**: Creates a new album.

**Input**:
- `album_name`: String (name of the new album).
- `parent_id`: String (optional, ID of the parent album).
- `image_ids`: List of String (optional, IDs of images to add to the album).

**Response**:
- `message`: String (confirmation message).
- `album_id`: String (ID of the created album).

**Error Handling**: Returns HTTP 500 if album creation fails.

### 7. POST `/add-images-to-album`

**Functionality**: Adds images to an album.

**Input**:
- `album_id`: String (ID of the album).
- `image_ids`: List of String (IDs of images to add).

**Response**:
- `message`: String (confirmation message).

**Error Handling**: Returns HTTP 400 if no image IDs are provided, or HTTP 404 if the album is not found, or HTTP 500 if adding images fails.

### 8. POST `/remove-tags`

**Functionality**: Removes tags from an image.

**Input**:
- `image_id`: String (ID of the image).
- `tags`: List of String (tags to remove).

**Response**:
- `message`: String (confirmation message).

**Error Handling**: Returns HTTP 400 if no image ID is provided, or HTTP 500 if tag removal fails.

### 9. DELETE `/delete-images`

**Functionality**: Deletes images.

**Input**:
- `image_ids`: List of String (IDs of images to delete).

**Response**:
- `message`: String (confirmation message).

**Error Handling**: Returns HTTP 400 if no image IDs are provided, or HTTP 500 if deletion fails.

### 10. DELETE `/delete-album`

**Functionality**: Deletes an album.

**Input**:
- `album_id`: String (ID of the album to delete).

**Response**:
- `message`: String (confirmation message).

**Error Handling**: Returns HTTP 404 if the album is not found, or HTTP 500 if deletion fails.

### 11. POST `/add-user-face`

**Functionality**: Adds a name to a detected face in an image.

**Input**:
- `inserted_id`: String (ID of the image).
- `anonymous_index`: Integer (index of the face in the image).
- `name`: String (name to associate with the face).

**Response**:
- `message`: String (confirmation message).

**Error Handling**: Returns HTTP 500 if adding the name fails.

### 12. POST `/relocate-images`

**Functionality**: Relocates images from one album to another.

**Input**:
- `image_ids`: List of String (optional, IDs of images to relocate).
- `prev_album_id`: String (ID of the current album).
- `new_album_id`: String (optional, ID of the new album).

**Response**:
- `message`: String (confirmation message).

**Error Handling**: Returns HTTP 404 if the album is not found, or HTTP 500 if relocation fails.

## How to Run PixPursuit

This section covers the steps required to set up and run the PixPursuit application on your local machine. Ensure you have Python 3.9 installed before proceeding.

### Setting Up the Virtual Environment

1. **Install Virtual Environment**
   ```bash
   python3.9 -m pip install virtualenv

2. **Create Virtual Environment**
    ```bash
    python3.9 -m virtualenv venv

3. **Activate Virtual Environment**

- On Windows:
    ```bash
    .\venv\Scripts\activate

- On Unix or MacOS:
    ```bash
    source venv/bin/activate

### Installing Dependencies

1. **Install Required Packages**
    ```bash
    pip install -r requirements.txt

### Running Redis Server

1. **Install Redis** (if not already installed):
   - Follow the instructions specific to your operating system from the [official Redis website](https://redis.io/download).

2. **Start the Redis Server**
   ```bash
   redis-server

### Running Celery Worker and Beat

1. **Start Celery Worker**
   ```bash
   celery -A app worker -l info -P solo

2. **Start Celery Beat (in a separate terminal)**
    Ensure the virtual environment is activated in this terminal as well.

    ```bash
    celery -A app beat -l info.

### Running the Application

1. **Start the PixPursuit Application**
    ```bash
    uvicorn app:app --reload

---

## Credits

Made with ❤️ by [Eryk](https://github.com/gdziewon) and [Michał](https://github.com/MistarzM).

## Acknowledgements

Special thanks to all contributors and the open-source community for making this project possible.

---
