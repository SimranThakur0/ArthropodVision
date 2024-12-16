from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
from PIL import Image
import numpy as np
from io import BytesIO
import base64
import os
import traceback

app = Flask(__name__)


os.makedirs('templates', exist_ok=True)

# Load the YOLO model
model = YOLO('model/model.pt')

def predict_image(image_bytes, conf=0.25):
    try:
        # Convert the image bytes to a PIL Image
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        
        print(f"Image dimensions: {img.size}")
        
        img_array = np.array(img)

        results = model(img_array, conf=conf)

        print(f"Raw results: {results}")

        detections = results[0].boxes.cpu().numpy()  # Convert boxes to NumPy
        output = []

        # Debug: Print number of detections
        print(f"Number of detections: {len(detections)}")

        for box in detections:
            # Unpack with more error handling
            try:
                x_min, y_min, x_max, y_max = box.xyxy[0][:4]
                confidence = box.conf[0]
                class_id = box.cls[0]
                
                output.append({
                    "class_id": int(class_id),
                    "confidence": float(confidence),
                    "x_min": float(x_min),
                    "y_min": float(y_min),
                    "x_max": float(x_max),
                    "y_max": float(y_max),
                })
            except Exception as box_error:
                print(f"Error processing detection: {box_error}")
        
        try:
            results_plotted = results[0].plot()
            _, buffer = cv2.imencode('.jpg', results_plotted)
            annotated_image = base64.b64encode(buffer).decode('utf-8')
        except Exception as plot_error:
            print(f"Error plotting results: {plot_error}")
            annotated_image = None
        
        return {
            "predictions": output,
            "annotated_image": annotated_image,
            "raw_results": str(results)
        }
    except Exception as e:
        return {
            "error": str(e),
            "full_error_details": str(traceback.format_exc())
        }

@app.route('/', methods=['GET'])
def home():
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Handle POST requests
    image_file = request.files.get('image')
    if not image_file:
        return jsonify({"error": "No image file provided"}), 400

    try:
        # Read the image bytes
        image_bytes = image_file.read()

        # Run the prediction
        results = predict_image(image_bytes)

        # If it's an AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(results)
        
        # Otherwise, render the template with results
        return render_template('results.html', 
                               predictions=results.get('predictions', []), 
                               annotated_image=results.get('annotated_image'))
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure required libraries are imported
    import cv2
    
    # Create templates if they don't exist
    os.makedirs('templates', exist_ok=True)
    
    # Run the app
    app.run(debug=True)