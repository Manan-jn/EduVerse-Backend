# AI Grading Assistant 
EduVerse's AI grading assistant provides scores and feedback for handwritten exams and essays, streamlining the assessment process.

## 📦 Setup 

Clone the repository

```bash
https://github.com/Manan-jn/EduVerse-Backend.git
```

```bash
cd grading-ocr 
```

##### Generate ```OPEN_API_KEY``` and replace it in ```main.py``` file

Install the dependencies and start the server
```bash
  pip install -r requirements.txt
  uvicorn --app-dir=./app main:app --host 0.0.0.0 --port 10000
```

## Architecture
![ai-grading](https://github.com/Manan-jn/EduVerse/assets/72336990/45186572-e99f-4c0c-9b0c-6d0832458a19)

