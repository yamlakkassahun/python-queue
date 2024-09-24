import os
from flask import Flask, request, jsonify, send_from_directory
from redis import Redis
from rq import Queue
from tasks import convert_video_to_audio  # Import the task function
import random

app = Flask(__name__)

# Redis and RQ setup
redis_conn = Redis()
q = Queue(connection=redis_conn)

# Directory to save uploaded and processed files
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_video():
    """ Upload video and enqueue conversion task """
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
    video_file.save(video_path)
    
    random_no = random.random()
    
    output_filename = os.path.splitext(video_file.filename)[0] + f'{random_no}.mp3'
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # Enqueue the background job
    job = q.enqueue(convert_video_to_audio, video_path, output_path)

    return jsonify({"job_id": job.get_id(), "status": "Job enqueued", "output_file": output_filename})

@app.route('/status/<job_id>', methods=['GET'])
def job_status(job_id):
    """ Check the status of a job """
    job = q.fetch_job(job_id)
    if job:
        return jsonify({"job_id": job_id, "status": job.get_status(), "result": job.result})
    else:
        return jsonify({"error": "Job not found"}), 404

@app.route('/download/<filename>', methods=['GET'])
def download_audio(filename):
    """ Serve the processed audio file """
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
