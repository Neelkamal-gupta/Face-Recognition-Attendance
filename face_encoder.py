import cv2
import face_recognition
import numpy as np
import pickle
import os

class FaceEncoder:
    def __init__(self, known_faces_path="known_faces/"):
        self.known_faces_path = known_faces_path
        if not os.path.exists(known_faces_path):
            os.makedirs(known_faces_path)
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.load_known_faces()
    
    def encode_face(self, image_path, student_id, name):
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]
                encoding_path = os.path.join(self.known_faces_path, f"{student_id}_{name}.pkl")
                
                with open(encoding_path, 'wb') as f:
                    pickle.dump({
                        'student_id': student_id,
                        'name': name,
                        'encoding': face_encoding
                    }, f)
                
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(name)
                self.known_face_ids.append(student_id)
                
                return encoding_path
            else:
                return None
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None
    
    def load_known_faces(self):
        for filename in os.listdir(self.known_faces_path):
            if filename.endswith('.pkl'):
                filepath = os.path.join(self.known_faces_path, filename)
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings.append(data['encoding'])
                    self.known_face_names.append(data['name'])
                    self.known_face_ids.append(data['student_id'])
    
    def recognize_face(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognized_faces = []
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            top, right, bottom, left = [coord * 4 for coord in face_location]
            
            if len(self.known_face_encodings) > 0:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    student_id = self.known_face_ids[best_match_index]
                    
                    recognized_faces.append({
                        'name': name,
                        'student_id': student_id,
                        'location': (top, right, bottom, left)
                    })
        
        return recognized_faces
