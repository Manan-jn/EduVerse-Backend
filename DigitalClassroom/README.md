# Digital Classroom
Generate simplified slides from text with images and Marp conversion.

## 📦 Setup 

Clone the repository

```bash
https://github.com/Manan-jn/EduVerse-Backend.git
```

```bash
cd DigitalClassroom 
```

Setup New firebase project and generate API Credentials and replace 
```
FIREBASE_API_KEY
FIREBASE_AUTH_DOMAIN
FIREBASE_PROJECT_ID
FIREBASE_STORAGE_BUCKET
FIREBASE_MESSAGE_SENDER_ID
FIREBASE_APP_ID
```
Generate service account under firebase and replace the following credentials
```
FIREBASE_TYPE
FIREBASE_PROJECT_ID
FIREBASE_PRIVATE_KEY_ID
FIREBASE_PRIVATE_KEY
FIREBASE_CLIENT_EMAIL
FIREBASE_CLIENT_ID
FIREBASE_AUTH_URI
FIREBASE_TOKEN_URI
FIREBASE_AUTH_PROVIDER_X509_CERT_URL
FIREBASE_CLIENT_X509_CERT_URL
FIREBASE_UNIVERSE_DOMAIN
```

##### Generate ```OPEN_API_KEY``` and replace it in ```app/main.py``` file
##### Generate  ```SEARCH_ENGINE_ID``` from  ```https://developers.google.com/custom-search/v1/overview``` and replace it in ```app/main.py``` file

Install the dependencies and start the server
```bash
  pip install -r requirements.txt
  uvicorn --app-dir=./app main:app --host 0.0.0.0 --port 10000
```

## Architecture Diagram
![digital classroom](https://github.com/Manan-jn/EduVerse/assets/72336990/dca4b4c3-b66e-4368-b46f-627c6a982529)
