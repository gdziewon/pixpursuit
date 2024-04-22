# PixPursuit Project Documentation

Backend and fronted of application from image management and processing with AI usage.
Made for [competition at Cracow University of Technology](https://konkursit.pk.edu.pl/)
## Frontend

Built with Next.js and TailwindCSS.

## Project Structure

#### `app`

- **albums:** Directory containing pages related to albums.
  - **[albumid]:**
    - **page.js:** Page for a specific album.
  - **add/[parentid]:**
    - **page.js:** Page for adding images to a specific album.
  - **liked:**
    - **page.js:** Page for showing liked by user images.
  - **unassagined:**
    - **page.js:** Page for showing images not assigned to any folder.
  - **page.js:** Default album page.
- **components:** Reusable React components used throughout the app.
  - **Navbar.jsx:** Navbar component displayed on every page.
  - **NextAuthProvider.jsx:** Authentication provider.
  - **RandomImage.js:** Component for displaying a carousel of random images.
  - **Searcher.jsx:** Component for searching within the app.
- **gallery:** Directory containing pages related to the image gallery.
  - **[id]:**
    - **page.js:** Page for a specific image.
  - **upload:**
    - **[albumid]:**
      - **page.js:** Page for adding images to a specific album.
    - **galeria_pk:**
      - **[albumid]:**
      - **page.js:** Page for adding images to a specific album.
      - **page.js:** Page for adding images to a specific album.
    - **sharepoint/[albumid]:**
      - **page.js:** Page for adding images to a specific album.
    - **zip:**
      - **[albumid]**
        - **page.js:** Page for adding images to a specific album.
      - **page.js:** Page for adding images to a specific album.
    - **page.js:** Page for uploading images.
    - **page.js:** Page for the image gallery.
- **register:**
  - **page.js:** Page for registering new user.
- **favicon.ico:** App favicon.
- **globals.css:** Imports TailwindCSS styles.
- **layout.js:** Defines the layout for the web app.
- **loading.js:** Template for when a component is fetching data.
- **page.js:** Default home page for the website.

#### `pages`

- **API:** Contains API routes for MongoDB connection and authentication.
  - **albums:**
    - **[albumid].js:** Handles requests related to a specific album.
  - **auth:**
    - **[...nextauth].js:** Authentication route.
  - **liked:**
    - **[user].js:** Handles requests related to a specific user.
  - **addUserTag.js** - Adds a tag from a user to an image.
  - **connectMongo.js** - Connects to MongoDB.
  - **getImages.js** - Retrieves all images from MongoDB.
  - **getSingleImage.js** - Retrieves a single image from MongoDB.
  - **randomImages.js** - Retrieves a random selection of images from MongoDB.
  - **searchSuggestions.js** - Gets search suggestions from MongoDB.
  - **verify-email:**
    - **index.js:** Handles requests related to the verification of user emails.

### `public`

- **.img:** Directory containing static images for the website.

### `styles`

- **album_layout_styles.css:** Styles for the album page.
- **design_style.css:** Styles for the design of the website.

### `utils` - Contains utility functions for the app.

- **AlbumButtons.js** - Implements buttons for interacting with albums in the application.
- **ConfirmDialog.js** - Displays a dialog box for confirming an action.
- **DropdownMenu.js** - Displays a dropdown menu with various options for interacting with the app.
- **DropdownMenuUpload.js** - Implements a dropdown menu for uploading images in the application.
- **ErrorWindow.js** - Handles error messages in the application.
- **faceBoxes.js** - Responsible for handling face bounding boxes in the application.
- **getImages.js** - Retrieves all images from MongoDB.
- **getRootId.js** - Retrieves the root ID of the application.
- **getSingleImage.js** - Gets a single image from MongoDB.
- **ImageSelection.js** - Handles image selection in the application.
- **RenameModal.js** - Handles renaming of images in the application.
- **SelectedItemsContext.js** - Manages the context for selected items in the application.
- **SuccessWindow.js** - Displays a success message in the application.
- **TagModal.js** - Handles tagging of images in the application.

### `.env`

- Contains environment variables.

### Config Files

- Various configuration files for the project. like:
    - `jsconfig.json`,
    - `tailwind.config.js`,
    - `next.config.js`,
    - `postcss.config.js`,
    - `package.json`,
    - `package-lock.json`

- **middleware.js** - File containing middleware functions for handling requests and responses in the application.

## Installation

To set up the PixPursuit locally, you need to:

    1. Clone the repository.
    2. Navigate to the `frontend` directory.
    3. Run `npm install` to install dependencies.
    4. Create a `.env` file with the required environment variables.

## Running the App

To run the app locally, use the following command in the console:
    ```npm run dev```

## Backend

Built with FastAPI, Celery and MongoDB.

## Project Structure

## Top-Level Files

- **Dockerfile**: Contains Docker build instructions.
- **app.py**: Main entry point for the application.
- **docker-compose.yml**: Defines Docker services, networks, and volumes.
- **nginx.conf**: Configures Nginx for handling HTTP(S) traffic.
- **pytest.ini**: Configures pytest settings for testing.
- **requirements.txt**: Lists Python dependencies.

## Directories

### `api/`
Contains FastAPI routes and schemas essential for request handling and data serialization.
- **middleware.py**: Defines middleware for the FastAPI application.
- **routes/**: Contains route handlers.
- **schemas/**: Contains Pydantic models for request validation and serialization.

### `config/`
Contains configuration files for various aspects of the application.
- **celery_config.py**: Configures Celery for task queue management.
- **database_config.py**: Sets up database connections.
- **logging_config.py**: Establishes logging configuration.
- **models_config.py**: Configures application ML models.

### `data/`
Hosts data extraction scripts and database operations.
- **data_extraction/**: Includes scripts for extracting data from images.
- **databases/**: Contains scripts for database interactions.

### `generated/`
Stores generated files such as logs, Celery beat schedules, and model states.

### `services/`
Comprises scripts that provide various backend services.
- **authentication/**: Handles user authentication processes.
- **image_scraper.py**: Script for scraping images from GaleriaPK.
- **image_similarity.py**: Computes image similarity metrics.
- **images_zip.py**: Scripts for handling ZIP files.
- **sharepoint/**: Scripts for interacting with SharePoint services.
- **tag_prediction/**: Contains tools for predicting image tags.

### `tests/`
Contains all test scripts and test data necessary for testing the application.
- **albums/**, **auth/**, **content/**, **download/**, **images/**: Test directories for respective modules.

### `utils/`
Houses utility scripts and constants that support various functions across the application.
- **constants.py**: Defines constant values used throughout the application.
- **dirs.py**: Manages directory paths used in the application.
- **exceptions.py**: Custom exception classes for error handling.
- **function_utils.py**: Utility functions to aid in common tasks.

## Database Schema Description

### Images Collection (`images`)
- **_id**: Automatically generated unique identifier by MongoDB.
- **image_url**: URL of the image stored in DigitalOcean Spaces.
- **thumbnail_url**: URL of the image thumbnail, also stored in DigitalOcean Spaces.
- **filename**: Unique filename for each image, generated using the uuid library and timestamp.
- **embeddings**: Array of face embeddings (512 double elements), extracted using the Facenet model.
- **embeddings_box**: Rectangular face embedding boxes, extracted using mtcnn.
- **metadata**: EXIF metadata of the image, such as width, height, and creation date, obtained using the Pillow library.
- **features**: Array of image features (1000 double elements), obtained using the ResNet model.
- **user_tags**: Tags added by the user.
- **auto_tags**: Tags added automatically by the TagPredictor model.
- **user_faces**: Faces added by the user.
- **auto_faces**: Faces added automatically based on embeddings and whether the face is recognized.
- **backlog_faces**: Faces added by user, which can't get assigned to any group yet.
- **unknown_faces**: The number of differences between user_faces and backlog_faces.
- **feedback**: Feedback history for auto_tags.
- **feedback_history**: User's feedback history regarding specific tags.
- **description**: Description of the image added by the user.
- **likes**: The number of likes an image has received.
- **liked_by**: List of users who have liked the image.
- **views**: The number of times the image has been viewed.
- **added_by**: The user who added the image.
- **album_id**: ID of the album to which the image is assigned.
- **album_name**: Name of the album to which the image is assigned.

### Tags Collection (`tags`)
- **_id**: Automatically generated unique identifier by MongoDB.
- **name**: Tag name.
- **count**: Number of occurrences of the tag among images.

### Users Collection (`users`)
- **_id**: Automatically generated unique identifier.
- **username**: User's name.
- **email**: User's address email.
- **password**: User's password, secured with the Argon2 hashing algorithm.

### Faces Collection (`faces`)
- **_id**: Automatically generated unique identifier.
- **face_emb**: Embeddings of the face.
- **group**: The group to which the face has been assigned based on embeddings.

### Albums Collection (`albums`)
- **_id**: Automatically generated unique identifier of the album.
- **name**: Name of the album.
- **parent**: ID of the parent album.
- **sons**: List of IDs of child albums.
- **images**: List of IDs of images contained in the album.

## Integration of Database Schema with the Application

The MongoDB database is central to the functionality of PixPursuit, acting as a repository for all data pertaining to images, users, tags, faces, and albums. Below is a detailed overview of how the various fields in the database collections are utilized within the application.

### Using Image Data
- **_id, image_url, thumbnail_url, filename**: These fields are critical for image retrieval and management within the app. The `_id` serves as a unique identifier for each image, while the URLs provide direct access to the images and their thumbnails stored in DigitalOcean Spaces.
- **embeddings, embeddings_box**: These are utilized in facial recognition features, helping to identify and group faces found in images. The embeddings represent facial features in a numerical form, and the boxes delineate the facial area within the image.
- **metadata**: Used to display image properties such as width, height, and creation date, enhancing the user's understanding and management of their image collection.
- **features**: This array, generated by the ResNet model, supports advanced image analysis tasks, including classification and similarity comparison.
- **user_tags, auto_tags**: User-added tags and system-generated tags (from the TagPredictor model) facilitate efficient image categorization and retrieval.
- **user_faces, auto_faces, backlog_faces, unknown_faces**: These fields support the facial recognition system by managing manually tagged faces, automatically detected faces, faces awaiting categorization, and discrepancies in face tagging.
- **feedback, feedback_history**: These elements are crucial for refining the machine learning models used in the app, as they provide user reactions and interactions with the automated tagging system.
- **description, likes, liked_by, views**: Enhance user engagement by allowing descriptions, tracking image popularity through likes and views, and listing users who have liked an image.
- **added_by, album_id, album_name**: Facilitate image management and organization, linking images to their uploader and the albums they belong to.

### Using Other Collections
- **Tags Collection**: Manages and tracks the use and popularity of tags within the platform, with each tag's occurrence documented.
- **Users Collection**: Handles user authentication and profile management, utilizing fields like username, email, and password.
- **Faces Collection**: Supports detailed face recognition tasks with fields like face embeddings and group assignments based on visual similarity.
- **Albums Collection**: Organizes images into hierarchical collections, making use of fields like album name, parent-child album relationships, and image associations.

## Machine Learning Models and Their Role

### TagPredictor Model
- **Functionality**: Automatically assigns relevant tags to images based on visual content.
- **Architecture**: Utilizes a deep learning framework, incorporating neural networks to analyze image data and predict tags.
- **Training**: Continuously learns from new image data and adjusts based on user feedback to improve tag accuracy.
- **Integration**: Tags are updated in the database under `auto_tags` for each image upon processing.

### Facial Detection Model (Facenet)
- **Functionality**: Identifies and extracts faces from images, storing embeddings and their spatial locations.
- **Integration**: Facilitates grouping of similar faces and aids in building a robust face-based indexing system.

### Features Extraction Model (ResNet50)
- **Functionality**: Analyzes the overall content of images to extract distinctive features.
- **Integration**: These features play a crucial role in image similarity assessments and advanced search functionalities.

## API Endpoints Documentation for PixPursuit

### Authentication and User Management

1. **POST `/token`**
   - **Functionality**: Authenticates a user and provides an access token.
   - **Input**: Username and password from form data.
   - **Response**: Access token, token type, and username.
   - **Error Handling**: HTTP 401 if authentication fails.

2. **POST `/register`**
   - **Functionality**: Registers a new user and sends a confirmation email.
   - **Input**: Email and password.
   - **Response**: Success message and confirmation that registration email has been sent.
   - **Error Handling**: HTTP 500 if registration fails.

3. **GET `/verify-email`**
   - **Functionality**: Verifies a user's email address using a token.
   - **Input**: Verification token.
   - **Response**: Success message upon email verification.
   - **Error Handling**: HTTP 500 if verification fails.

4. **POST `/refresh`**
   - **Functionality**: Refreshes an access token using a refresh token.
   - **Input**: Refresh token.
   - **Response**: New access and refresh tokens.
   - **Error Handling**: HTTP 401 if token is invalid.

### Album Management

5. **POST `/create-album`**
   - **Functionality**: Creates a new album.
   - **Input**: Album name, optional parent ID, and optional image IDs.
   - **Response**: Success message and new album ID.
   - **Error Handling**: HTTP 500 if album creation fails.

6. **POST `/add-images-to-album`**
   - **Functionality**: Adds images to an album.
   - **Input**: Album ID and list of image IDs.
   - **Response**: Success message.
   - **Error Handling**: HTTP 400 if no image IDs are provided, or HTTP 404 if the album is not found.

7. **DELETE `/delete-albums`**
   - **Functionality**: Deletes multiple albums.
   - **Input**: List of album IDs.
   - **Response**: Success message.
   - **Error Handling**: HTTP 500 if deletion fails.

8. **PUT `/rename-album`**
   - **Functionality**: Renames an existing album.
   - **Input**: Album ID and new name.
   - **Response**: Success message.
   - **Error Handling**: HTTP 404 if the album is not found.

9. **POST `/upload-zip`**
   - **Functionality**: Processes and uploads a ZIP file containing images to an album.
   - **Input**: ZIP file and optional parent album ID.
   - **Response**: Success message and new album ID.
   - **Error Handling**: HTTP 500 if ZIP processing fails.

10. **POST `/sharepoint-upload`**
    - **Functionality**: Initiates the upload of images from a SharePoint site.
    - **Input**: SharePoint URL, credentials, optional parent ID for the uploaded content, and optional size for image processing.
    - **Response**: Message indicating that the image upload process has been initiated.
    - **Error Handling**: Should handle errors related to SharePoint access or image processing issues.

### Content Management

11. **POST `/add-user-tag`**
    - **Functionality**: Adds user-defined tags to an image.
    - **Input**: Image ID and list of tags.
    - **Response**: Success message.
    - **Error Handling**: HTTP 500 if adding tags fails.

12. **POST `/feedback-on-tags`**
    - **Functionality**: Adds user feedback on tags.
    - **Input**: Image ID, tag, and feedback.
    - **Response**: Success message.
    - **Error Handling**: HTTP 500 if feedback submission fails.

13. **POST `/add-description`**
    - **Functionality**: Adds a description to an image.
    - **Input**: Image ID and description text.
    - **Response**: Success message.
    - **Error Handling**: HTTP 500 if adding description fails.

14. **POST `/add-like`**
    - **Functionality**: Adds a like to an image.
    - **Input**: Image ID and like status.
    - **Response**: Success message.
    - **Error Handling**: HTTP 500 if adding like fails.

15. **POST `/add-view`**
    - **Functionality**: Records a view of an image.
    - **Input**: Image ID.
    - **Response**: Success message.
    - **Error Handling**: HTTP 500 if adding view fails.

16. **POST `/remove-tags`**
    - **Functionality**: Removes tags from an image.
    - **Input**: Image ID and list of tags to remove.
    - **Response**: Success message.
    - **Error Handling**: HTTP 500 if removing tags fails.

17. **POST `/add-tags-to-selected`**
    - **Functionality**: Adds tags to selected images and albums.
    - **Input**: Lists of image and album IDs, and tags.
    - **Response**: Success message.
    - **Error Handling**: HTTP 400 if no IDs provided, or HTTP 500 if adding tags fails.

18. **POST `/add-user-face`**
    - **Functionality**: Adds a name to a detected face in an image.
    - **Input**: Image ID, index of the face in the image, and name to associate with the face.
    - **Response**: Success message confirming the name was added.
    - **Error Handling**: HTTP 500 if adding the name fails.

### Image and Album Downloads

19. **GET `/download-image/`**
    - **Functionality**: Downloads an image from a specified URL.
    - **Input**: Image URL.
    - **Response**: Streamed image file.
    - **Error Handling**: HTTP 400 if the URL is invalid.

20. **POST `/download-zip`**
    - **Functionality**: Creates and downloads a ZIP file containing specified images and albums.
    - **Input**: Optional lists of image and album IDs.
    - **Response**: Streamed ZIP file.
    - **Error Handling**: HTTP 404 if any content not found, or HTTP 500 if ZIP creation fails.
  
### Image Management

21. **POST `/process-images`**
    - **Functionality**: Processes and saves uploaded images.
    - **Input**: List of UploadFile objects, optional album ID.
    - **Response**: Success message confirming the processing and saving of images.
    - **Error Handling**: HTTP 400 if no images are provided.

22. **DELETE `/delete-images`**
    - **Functionality**: Deletes specified images.
    - **Input**: List of image IDs to be deleted.
    - **Response**: Success message confirming the deletion of images.
    - **Error Handling**: HTTP 400 if no image IDs are provided, or HTTP 500 if deletion fails.

23. **POST `/relocate-images`**
    - **Functionality**: Relocates images from one album to another.
    - **Input**: Previous and new album IDs, list of image IDs to relocate.
    - **Response**: Success message confirming the relocation of images.
    - **Error Handling**: HTTP 404 if the album is not found, or HTTP 500 if relocation fails.

24. **POST `/find-similar-images`**
    - **Functionality**: Finds images similar to a given image.
    - **Input**: Image ID, optional limit on the number of similar images to return.
    - **Response**: List of similar image IDs.
    - **Error Handling**: HTTP 400 if the limit is less than 1, or HTTP 500 if the search fails.

25. **POST `/scrape-images`**
    - **Functionality**: Scrapes images from a specified URL and saves them to an album.
    - **Input**: URL from which images will be scraped, optional album ID where the images will be saved.
    - **Response**: Success message and album ID where the images are saved.
    - **Error Handling**: HTTP 400 if the URL is invalid, or HTTP 500 if scraping fails.

## How to Run PixPursuit

This section provides the steps to set up and run PixPursuit using Docker.

### Prerequisites
- Ensure Docker and Docker Compose are installed on your machine.
- Python 3.9 should be installed if any local development or testing is needed.
- An `.env` file with necessary environment variables should be available at the project's root.

### Running the Application with Docker

1. **Build and Run with Docker Compose**
   - Navigate to your project directory where the `docker-compose.yml` is located.
   - Run the following command to build and start all services:
     ```bash
     docker-compose up --build
     ```
   - To run the containers in the background, use:
     ```bash
     docker-compose up -d
     ```

2. **Accessing the Application**
   - Once all containers are up, access the application through `http://localhost:8000` or the configured domain in your `nginx.conf`.

### Stopping the Application

- To stop and remove all containers, use the following command:
  ```bash
  docker-compose down
  ```

---

## Credits

Made with ❤️ by [Eryk](https://github.com/gdziewon) and [Michał](https://github.com/MistarzM).

## Acknowledgements

Special thanks to all contributors and the open-source community for making this project possible.

---
