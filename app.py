import os
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from model.model_loader import FireDetector
from PIL import Image, ImageDraw

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
AUTO_INPUT_FOLDER = 'auto_input'
LOGS_FOLDER = 'logs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

detector = FireDetector()

fire_counter = 0
fire_frames = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_prediction(filename, prediction, confidence):
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    log_file = os.path.join(LOGS_FOLDER, 'predictions.json')
    log_entry = {
        'filename': filename,
        'prediction': prediction,
        'confidence': confidence,
        'timestamp': datetime.now().isoformat()
    }

    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)

    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

def send_email_alert(confidence):
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    receiver_email = os.getenv('RECEIVER_EMAIL')

    if not email_user or not email_pass or not receiver_email:
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = receiver_email
        msg['Subject'] = "🔥 WILDFIRE ALERT"

        body = f"""
        WILDFIRE DETECTED!

        Confidence: {confidence:.2f}%

        Emergency Alert Triggered.
        10 Consecutive Fire Frames Confirmed.

        Please check the monitoring system immediately.
        """

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)
        text = msg.as_string()
        server.sendmail(email_user, receiver_email, text)
        server.quit()

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def draw_fire_bounding_box(image_path):
    try:
        img = Image.open(image_path).convert('RGB')
        draw = ImageDraw.Draw(img)
        pixels = img.load()
        width, height = img.size

        fire_pixels = []
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                if (r > 150 and g < 120 and b < 100) or (r > 200 and g > 100 and b < 100):
                    fire_pixels.append((x, y))

        if fire_pixels:
            min_x = min(p[0] for p in fire_pixels)
            max_x = max(p[0] for p in fire_pixels)
            min_y = min(p[1] for p in fire_pixels)
            max_y = max(p[1] for p in fire_pixels)

            draw.rectangle([min_x, min_y, max_x, max_y], outline='red', width=5)
            draw.rectangle([min_x + 2, min_y + 2, max_x - 2, max_y - 2], outline='yellow', width=3)

        annotated_filename = f'annotated_{os.path.basename(image_path)}'
        annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
        img.save(annotated_path)

        return annotated_filename
    except Exception as e:
        print(f"Error drawing bounding box: {e}")
        return os.path.basename(image_path)

def simulate_10_fire_frames(image_path):
    simulated_frames = []
    for i in range(1, 11):
        simulated_frames.append({
            'frame_number': i,
            'filename': os.path.basename(image_path),
            'status': 'Fire'
        })
    return simulated_frames

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        prediction, confidence = detector.predict(filepath)
        log_prediction(filename, prediction, confidence)

        return render_template(
            'result.html',
            prediction=prediction,
            confidence=confidence,
            image_path=filename
        )

    return redirect(url_for('index'))

@app.route('/monitor')
def monitor():
    global fire_counter, fire_frames
    import shutil

    os.makedirs(AUTO_INPUT_FOLDER, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    files = [f for f in os.listdir(AUTO_INPUT_FOLDER) if allowed_file(f)]

    if not files:
        return render_template(
            'monitoring.html',
            fire_counter=fire_counter,
            message="No images in auto_input folder"
        )

    filename = files[0]
    filepath = os.path.join(AUTO_INPUT_FOLDER, filename)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    shutil.copy(filepath, upload_path)

    prediction, confidence = detector.predict(filepath)
    log_prediction(filename, prediction, confidence)

    if prediction == "Fire":
        fire_counter += 1
        fire_frames.append({'filename': filename, 'confidence': confidence})
        if len(fire_frames) > 10:
            fire_frames.pop(0)
    else:
        fire_counter = 0
        fire_frames = []

    if fire_counter >= 10:
        send_email_alert(confidence)
        return render_template('alert.html', fire_frames=fire_frames, confidence=confidence)

    os.remove(filepath)

    return render_template(
        'monitoring.html',
        fire_counter=fire_counter,
        current_image=filename,
        prediction=prediction,
        confidence=confidence
    )

@app.route('/upload-auto-input', methods=['POST'])
def upload_auto_input():
    if 'file' not in request.files:
        return redirect(url_for('monitor'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('monitor'))

    if file and allowed_file(file.filename):
        os.makedirs(AUTO_INPUT_FOLDER, exist_ok=True)
        filename = secure_filename(file.filename)
        filepath = os.path.join(AUTO_INPUT_FOLDER, filename)
        file.save(filepath)

    return redirect(url_for('monitor'))

@app.route('/continue-monitoring')
def continue_monitoring():
    global fire_counter, fire_frames
    fire_counter = 0
    fire_frames = []
    return redirect(url_for('monitor'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/emergency-simulation', methods=['GET', 'POST'])
def emergency_simulation():
    print("==== EMERGENCY SIMULATION ROUTE CALLED ====")

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template(
                'emergency_simulation.html',
                message="Please select an image to upload."
            )

        file = request.files['file']

        if file.filename == '':
            return render_template(
                'emergency_simulation.html',
                message="Please select an image to upload."
            )

        if file and allowed_file(file.filename):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            prediction, confidence = detector.predict(filepath)
            log_prediction(filename, prediction, confidence)

            if prediction == "Fire":
                annotated_filename = draw_fire_bounding_box(filepath)

                annotated_path = os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    annotated_filename
                )

                simulated_frames = simulate_10_fire_frames(annotated_path)

                send_email_alert(confidence)

                return render_template(
                    'alert.html',
                    fire_frames=simulated_frames,
                    confidence=confidence,
                    annotated_image=annotated_filename,
                    simulation_mode=True
                )

            return render_template(
                'emergency_simulation.html',
                message="No fire detected. Emergency simulation not activated.",
                prediction=prediction,
                confidence=confidence,
                image_path=filename
            )

        return redirect(url_for('emergency_simulation'))

    return render_template('emergency_simulation.html')

if __name__ == '__main__':
    print("=== REGISTERED ROUTES ===")
    for rule in app.url_map.iter_rules():
        print(rule)
    print("========================")

    port = int(os.environ.get("PORT", 7860))
    app.run(debug=False, host='0.0.0.0', port=port)