# Wildfire AI

A Flask-based web application for detecting wildfires from images using deep learning.

## Features

- Drag-and-drop image upload
- Fire/Non-Fire classification with confidence score
- Webcam capture support
- Auto-monitoring mode
- 10 consecutive fire frames confirmation before alert
- Email alert system (configurable)
- Prediction logging

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Set up email alerts:
   - Copy `.env.example` to `.env`
   - For Gmail: Create an "App Password" at https://myaccount.google.com/apppasswords
   - Fill in your email credentials in `.env`
   ```
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASS=your-app-password
   RECEIVER_EMAIL=alert-email@example.com
   ```

5. Run the application:
```bash
python app.py
```

6. Open your browser and go to: http://127.0.0.1:5000

## How to Test the 10-Frame Alert

1. Go to **Auto Monitoring Mode**
2. Add 10 fire images one after another (or the same fire image 10 times)
3. After 10 consecutive fire detections, you'll see the alert page!
4. If email is configured, you'll get an email alert too!
