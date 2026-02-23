import sqlite3
import datetime
import pandas as pd

class AttendanceDatabase:
    def __init__(self, db_path="attendance_records.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT,
                year TEXT,
                face_encoding_path TEXT,
                registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                name TEXT,
                date DATE,
                time TIME,
                status TEXT DEFAULT 'Present'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_student(self, student_id, name, department, year, face_encoding_path):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students (student_id, name, department, year, face_encoding_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, name, department, year, face_encoding_path))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def mark_attendance(self, student_id, name):
        today = datetime.datetime.now().date()
        current_time = datetime.datetime.now().time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM attendance 
            WHERE student_id = ? AND date = ?
        ''', (student_id, today))
        
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO attendance (student_id, name, date, time)
                VALUES (?, ?, ?, ?)
            ''', (student_id, name, today, current_time))
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    
    def get_attendance_by_date(self, date):
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM attendance WHERE date = ?"
        df = pd.read_sql_query(query, conn, params=(date,))
        conn.close()
        return df
    
    def get_all_students(self):
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM students"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def export_attendance_to_csv(self, filename):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM attendance ORDER BY date DESC, time DESC", conn)
        df.to_csv(f"attendance_logs/{filename}.csv", index=False)
        conn.close()
        return f"attendance_logs/{filename}.csv"
