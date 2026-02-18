import os
from flask import Flask, render_template, request, Response, send_from_directory
from detector import detect_people, detect_video, detect_camera
from email_alert import send_alert
from config import ALERT_THRESHOLD

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('header.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files['file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    count, output_path = detect_people(filepath)
    message = ""
    if count > ALERT_THRESHOLD:
        send_alert(count)
        message = "<p class='error'>⚠️ Attention: Frequency exceeded and email sent!</p>"

    return f"""
    <div class="result">
        <h2>Processed Image: {file.filename}</h2>
        <p class="count">People detected: {count}</p>
        {message}
        <img src="/outputs/{os.path.basename(output_path)}" class="output-img">
    </div>
    """

@app.route('/upload_video', methods=['POST'])
def upload_video():
    file = request.files['file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    count, output_path = detect_video(filepath)
    message = ""
    if count > ALERT_THRESHOLD:
        send_alert(count)
        message = "<p class='error'>⚠️ Attention: Frequency exceeded and email sent!</p>"

    return f"""
    <div class="result">
        <h2>Processed Video: {file.filename}</h2>
        <p class="count">People detected: {count}</p>
        {message}
        <video width="600" controls>
            <source src="/outputs/{os.path.basename(output_path)}" type="video/mp4">
        </video>
    </div>
    """

@app.route('/live')
def live_camera():
    return Response(detect_camera(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/outputs/<path:filename>')
def outputs_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    app.run(debug=True)

