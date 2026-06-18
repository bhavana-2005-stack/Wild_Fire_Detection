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
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        prediction, confidence = detector.predict(filepath)
        log_prediction(filename, prediction, confidence)
        
        return render_template('result.html', 
                             prediction=prediction, 
                             confidence=confidence, 
                             image_path=filename)
    
    return redirect(url_for('index'))

@app.route('/monitor')
def monitor():
    global fire_counter, fire_frames
    import shutil
    
    files = [f for f in os.listdir(AUTO_INPUT_FOLDER) if allowed_file(f)]
    
    if not files:
        return render_template('monitoring.html', 
                             fire_counter=fire_counter, 
                             message="No images in auto_input folder")
    
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
    
    return render_template('monitoring.html', 
                         fire_counter=fire_counter, 
                         current_image=filename, 
                         prediction=prediction, 
                         confidence=confidence)

@app.route('/upload-auto-input', methods=['POST'])
def upload_auto_input():
    if 'file' not in request.files:
        return redirect(url_for('monitor'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('monitor'))
    
    if file and allowed_file(file.filename):
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

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
