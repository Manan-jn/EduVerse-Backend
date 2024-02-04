from flask import Flask, jsonify, request, send_file
from firebase_admin import credentials, storage, initialize_app
import os
import io
from AudioStoryGenerator import AudioStoryGenerator
from flask import send_file, make_response
from flask_cors import CORS 


app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("./credentials.json")
initialize_app(cred, {"storageBucket": "night-whisper-baf55.appspot.com"})

@app.route('/post_audio', methods=['POST'])
def post_audio():
    try:
        if request.is_json:
            data = request.json
            topic = data.get('topic', 'default_topic')

            generator = AudioStoryGenerator()
            audio_filename = generator.generate(topic)

            firebase_path = f"audio_files/{audio_filename}"
            bucket = storage.bucket()

            with open(f"static/{audio_filename}", "rb") as audio_file:
                blob = bucket.blob(firebase_path)
                blob.upload_from_file(audio_file, content_type="audio/wav")

            return jsonify({"message": "Audio posted successfully"})
        else:
            return jsonify({"error": "Invalid request format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-audio/<filename>', methods=['GET'])
def get_audio(filename):
    try:
        # Download the audio file from Firebase Storage
        firebase_path = f"audio_files/{filename}"
        bucket = storage.bucket()
        blob = bucket.blob(firebase_path)
        audio_data = blob.download_as_bytes()

        # response_headers = {
        #     'Content-Disposition': f'inline; filename={filename}',
        #     'Content-Type': 'audio/wav',
        #     'Cache-Control': 'no-store, must-revalidate',
        #     'Pragma': 'no-cache',
        #     'Expires': '0'
        # }

        # return send_file(io.BytesIO(audio_data), mimetype='audio/wav', as_attachment=True,
        #                  download_name=filename, conditional=True, response_headers=response_headers)
        response = make_response(audio_data)
        response.headers['Content-Disposition'] = f'inline; filename={filename}'
        response.headers['Content-Type'] = 'audio/wav'
        response.headers['Cache-Control'] = 'no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def hello():
    print('server is live')
    return {200: "API Running"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)


