**IoT-Based Intelligent Traffic Management System**

**Overview**

This project implements an IoT-based Intelligent Traffic Management System using ESP32-CAM modules and ultrasonic sensors. The system adjusts traffic light timings in real-time to optimize traffic flow, reduce congestion, and improve safety.

**Required Packages for the OpenCV algorithm**

    • https://github.com/pjreddie/darknet/blob/master/data/coco.names

    • https://github.com/patrick013/Object-Detection---Yolov3/blob/master/model/yolov3.weights

    • https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg

**System Components**

    • ESP32-CAM: Captures images and sends them to the server via WiFi.
    
    • Ultrasonic Sensors: Measure vehicle distance and send data to the server.
    
    • ESP32-CAM-MB Programmer: Programs the ESP32-CAM module.

**How It Works**

  **1. Data Collection:**

    • Ultrasonic sensors measure vehicle distance.
    
    • ESP32-CAM modules capture images.
    
    • Data is sent to the server every 30 seconds via WiFi.

  **2. Data Processing:**

    • Server analyzes distance data for vehicle density.
    
    • OpenCV analyzes images to count vehicles.

  **3. Traffic Analysis:**

    • Combines sensor and image data.
    
    • Adjusts traffic light timings based on vehicle density and count:
    
      • Red: High density or many vehicles.
      • Orange: Moderate density or vehicle count.
      • Green: Low density and few vehicles.

  **4. Web Interface:**

    • Displays real-time traffic data and live images.
    
    • Provides historical data for analysis.
![dashboard](https://github.com/TheodosiosKatis/Intelligent-Traffic-Management-System/assets/91337898/3d4970e4-996d-4158-b069-6cc576556a07)

**Benefits**

    • Improved Traffic Flow: Real-time adjustments reduce congestion.
    
    • Reduced Emissions: Minimized idle times lower fuel consumption.
    
    • Enhanced Safety: Dynamic control reduces accidents.
    
    • Better User Experience: Real-time traffic information.
