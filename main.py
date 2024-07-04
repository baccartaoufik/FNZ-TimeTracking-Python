from flask import Flask, request, jsonify
import os
import face_recognition
import numpy as np
from sqlalchemy import create_engine, Table, MetaData, select
from sqlalchemy.orm import sessionmaker
from PIL import Image

app = Flask(__name__)


engine = create_engine('mysql://remote_user:root@172.16.4.16:3306/Time_tracking')
Session = sessionmaker(bind=engine)
session = Session()

# Load user data
metadata = MetaData()
utilisateur_table = Table('utilisateur', metadata, autoload_with=engine)

def get_user_photos():
    columns = utilisateur_table.columns.keys()
    print("Available columns:", columns)
    stmt = select(utilisateur_table)
    result = session.execute(stmt)
    
    # Print the first row to see its structure
    first_row = result.fetchone()
    if first_row:
        print("First row type:", type(first_row))
        print("First row dir:", dir(first_row))
        try:
            print("First row as dict:", dict(first_row))
        except Exception as e:
            print("Error converting first row to dict:", str(e))
        
        for column in columns:
            try:
                value = getattr(first_row, column)
                print(f"{column}: {value}")
            except Exception as e:
                print(f"Error accessing {column}: {str(e)}")
    
    result = session.execute(stmt)

    user_photos = {}
    for user in result:
        try:
            user_id = getattr(user, 'id_utilisateur')
            photo = getattr(user, 'photo')
            print(f"User ID: {user_id}, Photo: {photo}")
            if photo:
                user_photos[str(user_id)] = photo
        except Exception as e:
            print(f"Error processing user: {str(e)}")

    return user_photos

def load_image_encodings(user_photos):
    encodings = {}
    for user_id, photo_name in user_photos.items():
        image_path = os.path.join('static', 'images', photo_name)
        print(f"Processing image: {image_path}")
        if os.path.exists(image_path):
            try:
                with Image.open(image_path) as img:
                    img = img.convert('RGB')
                    
                    img = img.resize((640, 480))
                    image = np.array(img)
                print(f"Image shape: {image.shape}, dtype: {image.dtype}")
                encoding = face_recognition.face_encodings(image)
                if encoding:
                    encodings[user_id] = encoding[0]
                else:
                    print(f"No face found in image: {photo_name}")
            except Exception as e:
                print(f"Error processing image {photo_name}: {str(e)}")
        else:
            print(f"Image not found: {image_path}")
    return encodings

def calculate_similarity(known_encoding, unknown_encoding):
    face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
    similarity = 1 - face_distance
    return similarity * 100  

def recognize_face(unknown_image, user_encodings):
    unknown_encoding = face_recognition.face_encodings(unknown_image)
    
    if not unknown_encoding:
        return "No face detected in the image."

    unknown_encoding = unknown_encoding[0]
    results = []

    for user_id, known_encoding in user_encodings.items():
        similarity = calculate_similarity(known_encoding, unknown_encoding)
        results.append((user_id, similarity))

    results.sort(key=lambda x: x[1], reverse=True)
    return results

user_photos = get_user_photos()
print("User photos:", user_photos)
user_encodings = load_image_encodings(user_photos)
SIMILARITY_THRESHOLD = 50.0

@app.route('/validate', methods=['POST'])
def validate():
    if 'file' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['file']
    image = face_recognition.load_image_file(image_file)
    
    recognition_results = recognize_face(image, user_encodings)
    
    print(f"Recognition results: {recognition_results}") 
    
    if isinstance(recognition_results, str):
        return jsonify({"error": recognition_results}), 400
    
    if recognition_results:
        top_match = recognition_results[0]
        top_user_id, top_similarity = top_match[0], float(top_match[1])
        
        print(f"Top match: User ID {top_user_id}, Similarity {top_similarity}%")
        
        if top_similarity >= SIMILARITY_THRESHOLD:
            stmt = select(utilisateur_table.c.email).where(utilisateur_table.c.id_utilisateur == top_user_id)
            result = session.execute(stmt).fetchone()
            if result:
                email = result[0]
                return jsonify({"email": email})
            else:
                print(f"No email found for user ID {top_user_id}") 
        else:
            print(f"Similarity {top_similarity}% is below threshold {SIMILARITY_THRESHOLD}%")
    else:
        print("No recognition results")
    
    return jsonify({"error": "No user is found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)