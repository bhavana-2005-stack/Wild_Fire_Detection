---
title: WildFire Detection
emoji: 🔥
colorFrom: red
colorTo: orange
sdk: docker
app_file: app.py
pinned: false
---

# 🔥 WildFire AI Detection System

An AI-powered wildfire detection platform built using Flask, Deep Learning, and Computer Vision. The system detects fire from images, provides confidence scores, visualizes fire regions using bounding boxes, and generates emergency alerts.

## 🚀 Live Demo

Hugging Face Space:
https://bhavanabondili-wildfire-detection.hf.space

GitHub Repository:
https://github.com/bhavana-2005-stack/Wild_Fire_Detection

---

## 📌 Features

### 🔍 Fire Detection
- Detects Fire / Non-Fire from uploaded images
- Displays prediction confidence score
- Supports image upload and webcam capture

### 🎯 Bounding Box Visualization
- Highlights fire-like regions
- Draws bounding boxes around detected fire areas
- Helps visualize fire location within the image

### 🚨 Emergency Simulation Mode
- Upload a single fire image
- Automatically simulates 10 consecutive fire frames
- Demonstrates real-world emergency workflow
- Triggers emergency alert dashboard

### 📡 Auto Monitoring Mode
- Monitors images from auto-input folder
- Processes images continuously
- Tracks consecutive fire detections

### 📧 Email Alert System
- Sends automated wildfire alerts
- Includes confidence score
- Configurable through environment variables

### 📊 Monitoring Dashboard
- Modern AI dashboard interface
- Real-time monitoring statistics
- Detection history visualization

---

## 🧠 Technology Stack

### Backend
- Python
- Flask

### AI & Computer Vision
- TensorFlow / Keras
- MobileNetV2
- Pillow (PIL)

### Frontend
- HTML5
- CSS3
- JavaScript
- Glassmorphism UI Design

### Deployment
- Docker
- Hugging Face Spaces

---

## 🏗️ Project Workflow

```text
Image Input
      ↓
Preprocessing
      ↓
Fire Detection Model
      ↓
Confidence Score
      ↓
Bounding Box Generation
      ↓
Emergency Validation
      ↓
Alert Generation
      ↓
Email Notification
```

---

## 🚨 Emergency Simulation Workflow

This project includes a special demonstration mode.

In real CCTV systems:

```text
Frame 1
Frame 2
Frame 3
...
Frame 10
```

are obtained from a live surveillance feed.

For demonstration purposes:

- User uploads a single fire image
- The system detects fire
- A bounding box is generated
- The image is repeated as 10 simulated fire frames
- Emergency alert workflow is triggered
- Email notification is generated

This allows evaluators to test the complete wildfire alert pipeline using only one image.

---

## 📁 Project Structure

```text
Wild_Fire_Detection/
│
├── app.py
├── requirements.txt
├── README.md
│
├── model/
│   └── model_loader.py
│
├── static/
│   ├── css/
│   └── uploads/
│
├── templates/
│   ├── index.html
│   ├── result.html
│   ├── monitoring.html
│   ├── alert.html
│   └── emergency_simulation.html
│
├── auto_input/
│
└── logs/
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/bhavana-2005-stack/Wild_Fire_Detection.git
cd Wild_Fire_Detection
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📧 Email Configuration

Create a `.env` file:

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
RECEIVER_EMAIL=receiver_email@gmail.com
```

For Gmail:
Use a Google App Password instead of your normal password.

---

## ▶️ Run Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## 🧪 Testing

### Standard Fire Detection

1. Upload image
2. Click Detect
3. View prediction and confidence

### Emergency Simulation

1. Open Emergency Simulation
2. Upload one fire image
3. View bounding box
4. Simulate 10 fire frames
5. Trigger emergency alert

### Auto Monitoring

1. Upload images into auto-input folder
2. Start monitoring
3. System processes images automatically

---

## 🎓 Academic Project

Department of Computer Science Engineering

CVR College of Engineering

Mini Project:
**Deep Learning-Based Wildfire Detection System**

---

## 👩‍💻 Developed By

**Bhavana Bondili**

Computer Science Engineering

CVR College of Engineering

GitHub:
https://github.com/bhavana-2005-stack

LinkedIn:
https://www.linkedin.com/in/bhavana-bondili-5200ba2a8/

---

## 🔥 WildFire AI

Early Detection • Rapid Response • Safer Environment