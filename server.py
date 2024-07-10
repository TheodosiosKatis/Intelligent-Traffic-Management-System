from flask import Flask, request, render_template, send_file, jsonify
from flask_cors import CORS
import io
from PIL import Image
from datetime import datetime
import cv2
import numpy as np
import os

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load YOLO
weights_path = os.path.join(current_dir, "yolov3.weights")
config_path = os.path.join(current_dir, "yolov3.cfg")
names_path = os.path.join(current_dir, "coco.names")

# Check if files exist
assert os.path.exists(weights_path), f"Weights file not found at {weights_path}"
assert os.path.exists(config_path), f"Config file not found at {config_path}"
assert os.path.exists(names_path), f"Names file not found at {names_path}"

# Load the network
net = cv2.dnn.readNet(weights_path, config_path)

# Get the names of all the layers
layer_names = net.getLayerNames()

# Get the indices of the output layers, i.e., the layers with unconnected outputs
try:
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
except TypeError:
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Load the COCO class labels
with open(names_path, "r") as f:
    classes = [line.strip() for line in f.readlines()]

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

distances = []
current_image = None
traffic_light_state = 'red'  # Initial state of the traffic light

@app.route('/')
def index():
    global current_image
    return render_template('index.html', distances=distances, image_available=current_image is not None, traffic_light_state=traffic_light_state)

@app.route('/ulsdata', methods=['POST'])
def upload_ultrasonic_data():
    if 'distance' in request.form:
        distance = int(request.form['distance'])
        save_distance(distance)
        analyze_traffic(distance)
        return 'Ultrasonic data uploaded successfully', 200
    return 'Invalid data', 400

@app.route('/picdata', methods=['POST'])
def upload_image():
    global current_image
    if 'imageFile' in request.files:
        image_file = request.files['imageFile']
        image = Image.open(image_file.stream)
        image_io = io.BytesIO()
        image.save(image_io, 'JPEG')
        image_io.seek(0)
        current_image = image_io
        analyze_image(image)
        return 'Image uploaded successfully', 200
    return 'Invalid data', 400

@app.route('/current_image')
def get_current_image():
    global current_image
    if current_image:
        current_image.seek(0)  # Reset the stream position to the beginning
        return send_file(current_image, mimetype='image/jpeg')
    return 'No image available', 404

@app.route('/traffic_light')
def get_traffic_light():
    global traffic_light_state
    return jsonify({'state': traffic_light_state})

@app.route('/chart_data')
def get_chart_data():
    global distances
    data = [{'timestamp': d.split(': ')[0], 'distance': int(d.split(': ')[1].split(' ')[0])} for d in distances]
    return jsonify(data)

def save_distance(distance):
    global distances
    distances.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {distance} cm")

def analyze_image(image):
    # Convert the image to OpenCV format
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Prepare the image for YOLO
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    
    # Analyze the outputs
    class_ids = []
    confidences = []
    boxes = []
    height, width, channels = image.shape
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and classes[class_id] in ["car", "motorbike", "bus", "truck"]:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    
    # Apply Non-Maximum Suppression to remove duplicate boxes
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    num_vehicles = len(indexes)
    print("Number of Vehicles -> ", num_vehicles)

    return num_vehicles

def analyze_traffic(distance):
    global traffic_light_state

    # Thresholds for traffic light state based on distance and number of cars
    DISTANCE_THRESHOLD_HIGH = 100  # in cm
    DISTANCE_THRESHOLD_LOW = 50  # in cm
    CAR_THRESHOLD_HIGH = 5
    CAR_THRESHOLD_LOW = 2

    num_cars = 0
    if current_image:
        current_image.seek(0)
        image = Image.open(current_image)
        num_cars = analyze_image(image)

    # Score calculation
    distance_score = 0
    car_score = 0

    if distance < DISTANCE_THRESHOLD_LOW:
        distance_score = 2
    elif distance < DISTANCE_THRESHOLD_HIGH:
        distance_score = 1

    if num_cars > CAR_THRESHOLD_HIGH:
        car_score = 2
    elif num_cars > CAR_THRESHOLD_LOW:
        car_score = 1

    total_score = distance_score + car_score

    # Determine traffic light state based on total score
    if total_score >= 3:
        traffic_light_state = 'red'
    elif total_score == 2:
        traffic_light_state = 'orange'
    else:
        traffic_light_state = 'green'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
