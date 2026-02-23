import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import datetime
import os
from database import AttendanceDatabase
from face_encoder import FaceEncoder

class FaceRecognitionAttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1200x700")
        
        self.db = AttendanceDatabase()
        self.face_encoder = FaceEncoder()
        self.camera = None
        self.is_camera_running = False
        self.current_frame = None
        
        self.setup_ui()
        
        # Create attendance_logs folder
        if not os.path.exists("attendance_logs"):
            os.makedirs("attendance_logs")
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Face Recognition Attendance System", 
                               font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Left Panel - Camera Feed
        camera_frame = ttk.LabelFrame(main_frame, text="Camera Feed", padding="10")
        camera_frame.grid(row=1, column=0, padx=10, pady=10)
        
        self.camera_label = ttk.Label(camera_frame)
        self.camera_label.grid(row=0, column=0)
        
        # Camera controls
        camera_controls = ttk.Frame(camera_frame)
        camera_controls.grid(row=1, column=0, pady=10)
        
        self.start_camera_btn = ttk.Button(camera_controls, text="Start Camera", 
                                          command=self.start_camera)
        self.start_camera_btn.grid(row=0, column=0, padx=5)
        
        self.stop_camera_btn = ttk.Button(camera_controls, text="Stop Camera", 
                                         command=self.stop_camera, state='disabled')
        self.stop_camera_btn.grid(row=0, column=1, padx=5)
        
        self.mark_btn = ttk.Button(camera_controls, text="Mark Attendance", 
                                  command=self.mark_attendance)
        self.mark_btn.grid(row=0, column=2, padx=5)
        
        # Middle Panel - Registration
        register_frame = ttk.LabelFrame(main_frame, text="Register New Student", padding="10")
        register_frame.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(register_frame, text="Student ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.student_id_entry = ttk.Entry(register_frame, width=20)
        self.student_id_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(register_frame, text="Full Name:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.student_name_entry = ttk.Entry(register_frame, width=20)
        self.student_name_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(register_frame, text="Department:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.department_combo = ttk.Combobox(register_frame, 
                                           values=["CS", "Engineering", "Business", "Arts"], 
                                           width=17)
        self.department_combo.grid(row=2, column=1, pady=5)
        self.department_combo.set("CS")
        
        ttk.Label(register_frame, text="Year:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.year_combo = ttk.Combobox(register_frame, 
                                      values=["1st", "2nd", "3rd", "4th"], 
                                      width=17)
        self.year_combo.grid(row=3, column=1, pady=5)
        self.year_combo.set("1st")
        
        ttk.Label(register_frame, text="Photo:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.photo_label = ttk.Label(register_frame, text="No file selected")
        self.photo_label.grid(row=4, column=1, pady=5)
        
        ttk.Button(register_frame, text="Browse Photo", 
                  command=self.browse_photo).grid(row=5, column=0, columnspan=2, pady=5)
        
        ttk.Button(register_frame, text="Register Student", 
                  command=self.register_student).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Right Panel - Attendance View
        view_frame = ttk.LabelFrame(main_frame, text="Today's Attendance", padding="10")
        view_frame.grid(row=1, column=2, padx=10, pady=10)
        
        # Treeview
        self.tree = ttk.Treeview(view_frame, columns=("ID", "Name", "Time"), 
                                show="headings", height=15)
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Time", text="Time")
        self.tree.pack()
        
        # Export button
        ttk.Button(view_frame, text="Export to CSV", 
                  command=self.export_attendance).pack(pady=10)
        
        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_label.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.refresh_attendance()
    
    def start_camera(self):
        self.camera = cv2.VideoCapture(0)
        if self.camera.isOpened():
            self.is_camera_running = True
            self.start_camera_btn.config(state='disabled')
            self.stop_camera_btn.config(state='normal')
            self.update_camera()
            self.status_label.config(text="Camera started")
    
    def stop_camera(self):
        self.is_camera_running = False
        if self.camera:
            self.camera.release()
        self.camera_label.config(image='')
        self.start_camera_btn.config(state='normal')
        self.stop_camera_btn.config(state='disabled')
        self.status_label.config(text="Camera stopped")
    
    def update_camera(self):
        if self.is_camera_running:
            ret, frame = self.camera.read()
            if ret:
                self.current_frame = frame
                
                # Recognize faces
                faces = self.face_encoder.recognize_face(frame)
                
                # Draw rectangles
                for face in faces:
                    top, right, bottom, left = face['location']
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, face['name'], (left, top-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Convert to ImageTk
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                img = img.resize((480, 360))
                imgtk = ImageTk.PhotoImage(img)
                
                self.camera_label.config(image=imgtk)
                self.camera_label.image = imgtk
            
            self.root.after(10, self.update_camera)
    
    def browse_photo(self):
        filename = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if filename:
            self.photo_path = filename
            self.photo_label.config(text=os.path.basename(filename))
    
    def register_student(self):
        student_id = self.student_id_entry.get()
        name = self.student_name_entry.get()
        dept = self.department_combo.get()
        year = self.year_combo.get()
        
        if not all([student_id, name]):
            messagebox.showwarning("Warning", "Please fill all fields")
            return
        
        if not hasattr(self, 'photo_path'):
            messagebox.showwarning("Warning", "Please select a photo")
            return
        
        encoding_path = self.face_encoder.encode_face(self.photo_path, student_id, name)
        
        if encoding_path:
            if self.db.register_student(student_id, name, dept, year, encoding_path):
                messagebox.showinfo("Success", f"Student {name} registered!")
                self.student_id_entry.delete(0, tk.END)
                self.student_name_entry.delete(0, tk.END)
                self.photo_label.config(text="No file selected")
            else:
                messagebox.showerror("Error", "Student ID already exists!")
        else:
            messagebox.showerror("Error", "No face detected in photo")
    
    def mark_attendance(self):
        if self.current_frame is None:
            messagebox.showwarning("Warning", "No camera frame available")
            return
        
        faces = self.face_encoder.recognize_face(self.current_frame)
        
        if faces:
            for face in faces:
                if self.db.mark_attendance(face['student_id'], face['name']):
                    self.status_label.config(text=f"Marked: {face['name']}")
                else:
                    self.status_label.config(text=f"{face['name']} already marked")
            self.refresh_attendance()
        else:
            messagebox.showinfo("Info", "No recognized faces found")
    
    def refresh_attendance(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        today = datetime.datetime.now().date()
        df = self.db.get_attendance_by_date(today)
        
        for _, row in df.iterrows():
            self.tree.insert('', 'end', values=(row['student_id'], row['name'], row['time']))
    
    def export_attendance(self):
        filename = f"attendance_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filepath = self.db.export_attendance_to_csv(filename)
        messagebox.showinfo("Success", f"Exported to {filepath}")

def main():
    root = tk.Tk()
    app = FaceRecognitionAttendanceSystem(root)
    root.mainloop()
