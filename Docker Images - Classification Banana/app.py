from flask import Flask, request, jsonify
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

# Load the model
model_path = "./BananaClassModelFinal.h5"
model_0 = load_model(model_path)

# Function to check if the file is a valid image
def image_check(file_stream):
    try:
        img = Image.open(file_stream)
        img.verify()
        return True
    except Exception:
        return False

# Function to classify the image
def classify_banana_image(img_data):
    """
    Classifies the ripeness of a banana in an image.
    Parameters:
        img_data (bytes): The byte data of the image to classify.
    Returns:
        tuple: A tuple containing:
            - predicted_class_name (str): The predicted ripeness category ('Green Banana', 'Ripe Banana', or 'Overripe Banana').
            - accuracy (float): The confidence of the prediction as a percentage.
    Returns (None, None) if the image fails the initial check.
    """
    if image_check(io.BytesIO(img_data)):
        # Load and preprocess the image
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = tf.keras.applications.mobilenet_v3.preprocess_input(img_array)

        # Predict the class
        prediction = model_0.predict(img_array)
        predicted_class = np.argmax(prediction, axis=1)
        predicted_prob = np.max(prediction, axis=1)

        # Map class index to class name
        class_names = {0: 'Rotten Banana', 1: 'Ripe Banana', 2: 'Overripe Banana' , 3: 'Unripe Banana'}
        predicted_class_name = class_names[predicted_class[0]]

        # Get accuracy
        accuracy = predicted_prob[0] * 100
        return predicted_class_name, accuracy
    else:
        return None, None

@app.route('/classify', methods=['POST'])
def classify():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    img_data = file.read()
    predicted_class_name, accuracy = classify_banana_image(img_data)
    if predicted_class_name:
        response = {
            'image_name': file.filename,
            'predicted_class_name': predicted_class_name,
            'accuracy': float(accuracy)
        }
        return jsonify(response), 200
    else:
        return jsonify({'error': 'Invalid image file'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
