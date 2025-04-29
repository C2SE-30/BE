from flask import Flask, request, jsonify, send_file
import pyodbc
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import io
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://localhost:8501"]}})

# Kết nối cơ sở dữ liệu
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-TBEA6D9U\\SQLEXPRESS;"
    "DATABASE=cap2;"
    "Trusted_Connection=yes;"
)

def get_connection():
    try:
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        print(f"Error connecting to database: {str(e)}")
        raise

# Route favicon.ico
@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return "", 204

# Endpoint đăng nhập
@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    data = request.json
    email = data.get("username")
    password = data.get("password")

    if not email or not password:
        response = jsonify({"error": "Thiếu thông tin đăng nhập"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT u.user_id, u.name, u.email, u.password, r.role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.email = ?
                    """, (email,)
                )
                row = cursor.fetchone()
                if row:
                    user_id, name, email_db, stored_password, role_name = row
                    if stored_password == password:
                        response = jsonify({
                            "message": "Đăng nhập thành công",
                            "user": {
                                "id": user_id,
                                "name": name,
                                "email": email_db,
                                "role": role_name
                            }
                        })
                        response.headers.add("Access-Control-Allow-Origin", "*")
                        return response, 200
                    else:
                        response = jsonify({"error": "Sai mật khẩu"})
                        response.headers.add("Access-Control-Allow-Origin", "*")
                        return response, 401
                response = jsonify({"error": "Email không tồn tại"})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 401
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint lấy thông tin sinh viên
@app.route("/student/<int:user_id>", methods=["GET", "OPTIONS"])
def get_student(user_id):
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT s.student_code, u.name, s.major, u.email, s.enrolled_at
                    FROM students s
                    JOIN users u ON s.user_id = u.user_id
                    WHERE s.user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    response = jsonify({
                        "student": {
                            "student_code": row[0],
                            "name": row[1],
                            "major": row[2],
                            "email": row[3],
                            "enrolled_at": row[4].isoformat() if row[4] else None
                        }
                    })
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response
                response = jsonify({"error": "Không tìm thấy sinh viên"})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 404
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint lấy hồ sơ sinh viên
@app.route("/student-profile/<int:user_id>", methods=["GET", "OPTIONS"])
def get_student_profile(user_id):
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        s.student_code, u.name, s.major, u.email, s.enrolled_at,
                        s.gender, s.birth_date, s.phone, s.id_number, s.class,
                        s.level, s.department, s.current_address_street, s.current_address_ward,
                        s.current_address_district, s.current_address_city, s.current_address_country,
                        s.emergency_contact_name, s.emergency_contact_relationship,
                        s.emergency_contact_phone, s.emergency_contact_email,
                        s.emergency_contact_address_street, s.emergency_contact_address_ward,
                        s.emergency_contact_address_district, s.emergency_contact_address_city,
                        s.emergency_contact_address_country
                    FROM students s
                    JOIN users u ON s.user_id = u.user_id
                    WHERE s.user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    response = jsonify({
                        "student": {
                            "student_code": row[0],
                            "name": row[1],
                            "major": row[2],
                            "email": row[3],
                            "enrolled_at": row[4].isoformat() if row[4] else None,
                            "gender": row[5],
                            "birth_date": row[6].isoformat() if row[6] else None,
                            "phone": row[7],
                            "id_number": row[8],
                            "class": row[9],
                            "level": row[10],
                            "department": row[11],
                            "current_address": {
                                "street": row[12],
                                "ward": row[13],
                                "district": row[14],
                                "city": row[15],
                                "country": row[16]
                            },
                            "emergency_contact": {
                                "name": row[17],
                                "relationship": row[18],
                                "phone": row[19],
                                "email": row[20],
                                "address": {
                                    "street": row[21],
                                    "ward": row[22],
                                    "district": row[23],
                                    "city": row[24],
                                    "country": row[25]
                                }
                            }
                        }
                    })
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response
                response = jsonify({"error": "Không tìm thấy sinh viên"})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 404
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint cập nhật hồ sơ sinh viên
@app.route("/update-student-profile/<int:user_id>", methods=["PUT", "OPTIONS"])
def update_student_profile(user_id):
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "PUT, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    major = data.get("major")
    gender = data.get("gender")
    birth_date = data.get("birth_date")
    id_number = data.get("id_number")
    class_name = data.get("class")
    level = data.get("level")
    department = data.get("department")
    current_address = data.get("current_address", {})
    emergency_contact = data.get("emergency_contact", {})

    if not all([name, email, phone, major]):
        response = jsonify({"error": "Thiếu thông tin cần cập nhật"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE users
                    SET name = ?, email = ?, updated_at = ?
                    WHERE user_id = ?
                    """, (name, email, datetime.now(), user_id)
                )
                cursor.execute(
                    """
                    UPDATE students
                    SET 
                        major = ?, gender = ?, birth_date = ?, phone = ?, id_number = ?,
                        class = ?, level = ?, department = ?,
                        current_address_street = ?, current_address_ward = ?,
                        current_address_district = ?, current_address_city = ?, current_address_country = ?,
                        emergency_contact_name = ?, emergency_contact_relationship = ?,
                        emergency_contact_phone = ?, emergency_contact_email = ?,
                        emergency_contact_address_street = ?, emergency_contact_address_ward = ?,
                        emergency_contact_address_district = ?, emergency_contact_address_city = ?,
                        emergency_contact_address_country = ?
                    WHERE user_id = ?
                    """,
                    (
                        major, gender, birth_date, phone, id_number,
                        class_name, level, department,
                        current_address.get("street"), current_address.get("ward"),
                        current_address.get("district"), current_address.get("city"), current_address.get("country"),
                        emergency_contact.get("name"), emergency_contact.get("relationship"),
                        emergency_contact.get("phone"), emergency_contact.get("email"),
                        emergency_contact.get("address", {}).get("street"), emergency_contact.get("address", {}).get("ward"),
                        emergency_contact.get("address", {}).get("district"), emergency_contact.get("address", {}).get("city"),
                        emergency_contact.get("address", {}).get("country"),
                        user_id
                    )
                )
                conn.commit()
                response = jsonify({"message": "Cập nhật hồ sơ thành công"})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 200
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint lấy danh sách sinh viên
@app.route("/students", methods=["GET", "OPTIONS"])
def get_students():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    user_id = request.args.get("user_id")
    search = request.args.get("search", "")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if not row or row[0].lower() != "advisor":
                    response = jsonify({"error": "Chỉ cố vấn học tập (Advisor) được phép truy cập"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 403

                query = """
                    SELECT s.student_code, u.name, s.major, p.risk_level
                    FROM students s
                    JOIN users u ON s.user_id = u.user_id
                    LEFT JOIN ai_predictions p ON s.student_id = p.student_id
                    WHERE u.name LIKE ? OR s.student_code LIKE ?
                    """
                params = (f"%{search}%", f"%{search}%")
                cursor.execute(query + " ORDER BY s.student_code OFFSET ? ROWS FETCH NEXT ? ROWS ONLY",
                              params + ((page - 1) * per_page, per_page))
                rows = cursor.fetchall()
                students = [
                    {
                        "mssv": row[0],
                        "name": row[1],
                        "nganh": row[2],
                        "trangthai": row[3] if row[3] else "Bình thường",
                        "color": {"Low": "normal", "Medium": "yellow", "High": "red", "Bình thường": "normal"}.get(row[3], "normal")
                    }
                    for row in rows
                ]
                cursor.execute("SELECT COUNT(*) FROM students s JOIN users u ON s.user_id = u.user_id WHERE u.name LIKE ? OR s.student_code LIKE ?", params)
                total = cursor.fetchone()[0]
                response = jsonify({
                    "students": students,
                    "total": total,
                    "page": page,
                    "per_page": per_page
                })
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint xử lý file CSV và dự đoán nguy cơ bỏ học
@app.route("/predict-student", methods=["GET", "POST", "OPTIONS"])
def predict_student():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    user_id = request.args.get("user_id")
    if not user_id:
        response = jsonify({"error": "Thiếu user_id"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if not row or row[0].lower() != "advisor":
                    response = jsonify({"error": "Chỉ cố vấn học tập (Advisor) được phép truy cập"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 403
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    try:
        if request.method == "POST":
            if 'file' not in request.files:
                response = jsonify({"error": "Không có file được tải lên"})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 400
            file = request.files['file']
            data = pd.read_csv(file)
        else:
            data = pd.read_csv("data.csv")

        data['DropoutRisk'] = np.where((data['Grades'] < 40) | (data['Attendant'] < 50), 1, 0)
        high_risk_students = data[data['DropoutRisk'] == 1]
        data_dict = data.to_dict('records')
        high_risk_dict = high_risk_students.to_dict('records')
        socioecon_mean = float(data['SOCIECON'].mean())
        study_hours_mean = float(data['Study HOU'].mean())
        sleep_hours_mean = float(data['Sleep HOU'].mean())
        attendant_mean = float(data['Attendant'].mean())
        grades_mean = float(data['Grades'].mean())
        data.to_csv('temp_data.csv', index=False)
        high_risk_students.to_csv('temp_high_risk.csv', index=False)
        response = jsonify({
            "data": data_dict,
            "high_risk_students": high_risk_dict,
            "columns": list(data.columns),
            "socioecon_mean": socioecon_mean,
            "study_hours_mean": study_hours_mean,
            "sleep_hours_mean": sleep_hours_mean,
            "attendant_mean": attendant_mean,
            "grades_mean": grades_mean
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except Exception as e:
        response = jsonify({"error": f"Lỗi khi xử lý dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint dự đoán thủ công
@app.route("/predict-manual", methods=["POST", "OPTIONS"])
def predict_manual():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        response = jsonify({"error": "Thiếu user_id"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if not row or row[0].lower() != "advisor":
                    response = jsonify({"error": "Chỉ cố vấn học tập (Advisor) được phép truy cập"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 403
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    try:
        data_df = pd.read_csv('temp_data.csv')
        X = data_df[['SOCIECON', 'Study HOU', 'Sleep HOU', 'Attendant', 'Grades']]
        y = data_df['DropoutRisk']
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = LogisticRegression()
        model.fit(X_scaled, y)
        socioecon = float(data.get("socioecon"))
        study_hours = float(data.get("study_hours"))
        sleep_hours = float(data.get("sleep_hours"))
        attendant = float(data.get("attendant"))
        grades = float(data.get("grades"))
        input_data = np.array([[socioecon, study_hours, sleep_hours, attendant, grades]])
        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)[0]
        probability = model.predict_proba(input_scaled)[0][1]
        prediction_data = pd.DataFrame({
            'SOCIECON': [socioecon],
            'Study HOU': [study_hours],
            'Sleep HOU': [sleep_hours],
            'Attendant': [attendant],
            'Grades': [grades],
            'DropoutRisk': [prediction],
            'Probability': [probability],
            'Timestamp': [pd.Timestamp.now()]
        })
        prediction_data.to_csv('predictions.csv', mode='a', header=not os.path.exists('predictions.csv'), index=False)
        response = jsonify({
            "prediction": int(prediction),
            "probability": float(probability)
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    except Exception as e:
        response = jsonify({"error": f"Lỗi khi dự đoán: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint tải danh sách sinh viên nguy cơ cao
@app.route("/download-high-risk-students", methods=["GET"])
def download_high_risk_students():
    user_id = request.args.get("user_id")
    if not user_id:
        response = jsonify({"error": "Thiếu user_id"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if not row or row[0].lower() != "advisor":
                    response = jsonify({"error": "Chỉ cố vấn học tập (Advisor) được phép truy cập"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 403
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    try:
        high_risk_students = pd.read_csv('temp_high_risk.csv')
        csv_buffer = io.StringIO()
        high_risk_students.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        return send_file(
            io.BytesIO(csv_data.encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='high_risk_students.csv'
        )
    except Exception as e:
        response = jsonify({"error": f"Lỗi khi tải file: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint lấy lịch sử dự đoán
@app.route("/prediction-history", methods=["GET"])
def prediction_history():
    user_id = request.args.get("user_id")
    if not user_id:
        response = jsonify({"error": "Thiếu user_id"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if not row or row[0].lower() != "advisor":
                    response = jsonify({"error": "Chỉ cố vấn học tập (Advisor) được phép truy cập"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 403
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    try:
        if os.path.exists('predictions.csv'):
            df = pd.read_csv('predictions.csv')
            history = df.to_dict('records')
            response = jsonify({"history": history})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        else:
            response = jsonify({"history": []})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
    except Exception as e:
        response = jsonify({"error": f"Lỗi khi đọc lịch sử dự đoán: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint lấy thông báo
@app.route("/notifications", methods=["GET", "OPTIONS"])
def notifications():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    user_id = request.args.get("user_id")
    if not user_id:
        response = jsonify({"notifications": []})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT notification_id, message, is_read, created_at
                    FROM notifications
                    WHERE user_id = ?
                    """, (user_id,)
                )
                rows = cursor.fetchall()
                notifications = [
                    {
                        "id": row[0],
                        "message": row[1],
                        "is_read": bool(row[2]),
                        "created_at": row[3].isoformat() if row[3] else None
                    }
                    for row in rows
                ]
                response = jsonify({"notifications": notifications})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint đánh dấu thông báo đã đọc hoặc xóa
@app.route("/notifications/<int:notification_id>", methods=["DELETE", "OPTIONS"])
def delete_notification(notification_id):
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "DELETE, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    user_id = request.args.get("user_id")
    if not user_id:
        response = jsonify({"error": "Thiếu user_id"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM notifications
                    WHERE notification_id = ? AND user_id = ?
                    """, (notification_id, user_id)
                )
                conn.commit()
                if cursor.rowcount > 0:
                    response = jsonify({"message": "Xóa thông báo thành công"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 200
                else:
                    response = jsonify({"error": "Không tìm thấy thông báo"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 404
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint lấy điểm số
@app.route("/grades", methods=["GET", "OPTIONS"])
def grades():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    user_id = request.args.get("user_id")
    if not user_id:
        response = jsonify({"error": "Thiếu user_id"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT ar.record_id, ar.course, ar.grade, ar.semester
                    FROM academic_records ar
                    JOIN students s ON ar.student_id = s.student_id
                    WHERE s.user_id = ?
                    """, (user_id,)
                )
                rows = cursor.fetchall()
                grades = [
                    {
                        "record_id": row[0],
                        "course": row[1],
                        "grade": row[2],
                        "semester": row[3]
                    }
                    for row in rows
                ]
                response = jsonify({"grades": grades})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint hành động
@app.route("/actions", methods=["GET", "OPTIONS"])
def actions():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    user_id = request.args.get("user_id")
    if not user_id:
        response = jsonify({"error": "Thiếu user_id"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT a.action, a.timestamp
                    FROM activity_logs a
                    WHERE a.user_id = ?
                    ORDER BY a.timestamp DESC
                    """, (user_id,)
                )
                rows = cursor.fetchall()
                actions = [
                    {
                        "action": row[0],
                        "timestamp": row[1].isoformat()
                    }
                    for row in rows
                ]
                response = jsonify({"actions": actions})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint tài liệu
@app.route("/resources", methods=["GET", "OPTIONS"])
def resources():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT resource_id, title, url, description, created_at
                    FROM resources
                    """
                )
                rows = cursor.fetchall()
                resources = [
                    {
                        "resource_id": row[0],
                        "title": row[1],
                        "url": row[2],
                        "description": row[3],
                        "created_at": row[4].isoformat() if row[4] else None
                    }
                    for row in rows
                ]
                response = jsonify({"resources": resources})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint lưu gợi ý tư vấn
@app.route("/advise", methods=["POST", "OPTIONS"])
def advise():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    data = request.json
    user_id = data.get("user_id")
    student_code = data.get("student_code")
    strategy = data.get("strategy")

    if not all([user_id, student_code, strategy]):
        response = jsonify({"error": "Thiếu thông tin cần thiết"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if not row or row[0].lower() != "advisor":
                    response = jsonify({"error": "Chỉ cố vấn học tập (Advisor) được phép truy cập"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 403

                cursor.execute(
                    """
                    SELECT student_id
                    FROM students
                    WHERE student_code = ?
                    """, (student_code,)
                )
                row = cursor.fetchone()
                if not row:
                    response = jsonify({"error": "Không tìm thấy sinh viên"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 404
                student_id = row[0]

                cursor.execute(
                    """
                    SELECT advisor_id
                    FROM advisors
                    WHERE user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if not row:
                    response = jsonify({"error": "Không tìm thấy cố vấn"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 404
                advisor_id = row[0]

                cursor.execute(
                    """
                    INSERT INTO intervention_plans (student_id, advisor_id, strategy)
                    VALUES (?, ?, ?)
                    """, (student_id, advisor_id, strategy)
                )
                conn.commit()
                response = jsonify({"message": "Lưu gợi ý tư vấn thành công"})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 200
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint gửi tin nhắn
@app.route("/messages", methods=["POST", "OPTIONS"])
def send_message():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    data = request.json
    sender_id = data.get("sender_id")
    student_code = data.get("student_code")
    content = data.get("content")

    if not all([sender_id, student_code, content]):
        response = jsonify({"error": "Thiếu thông tin cần thiết"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = ?
                    """, (sender_id,)
                )
                row = cursor.fetchone()
                if not row or row[0].lower() != "advisor":
                    response = jsonify({"error": "Chỉ cố vấn học tập (Advisor) được phép gửi tin nhắn"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 403

                cursor.execute(
                    """
                    SELECT user_id
                    FROM students
                    WHERE student_code = ?
                    """, (student_code,)
                )
                row = cursor.fetchone()
                if not row:
                    response = jsonify({"error": "Không tìm thấy sinh viên"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 404
                receiver_id = row[0]

                cursor.execute(
                    """
                    INSERT INTO messages (sender_id, receiver_id, content)
                    VALUES (?, ?, ?)
                    """, (sender_id, receiver_id, content)
                )
                conn.commit()
                response = jsonify({"message": "Gửi tin nhắn thành công"})
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response, 200
    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

# Endpoint quản lý lịch hẹn
@app.route("/appointments", methods=["POST", "GET", "PUT", "OPTIONS"])
def manage_appointments():
    if request.method == "OPTIONS":
        response = jsonify({"status": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, GET, PUT, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Accept")
        return response, 200

    user_id = request.args.get("user_id")
    if not user_id:
        response = jsonify({"error": "Thiếu user_id"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT r.role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.role_id
                    WHERE u.user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if not row or row[0].lower() != "advisor":
                    response = jsonify({"error": "Chỉ cố vấn học tập (Advisor) được phép truy cập"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 403

                cursor.execute(
                    """
                    SELECT advisor_id
                    FROM advisors
                    WHERE user_id = ?
                    """, (user_id,)
                )
                row = cursor.fetchone()
                if not row:
                    response = jsonify({"error": "Không tìm thấy cố vấn"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 404
                advisor_id = row[0]

    except pyodbc.Error as e:
        response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 500

    if request.method == "POST":
        data = request.json
        student_code = data.get("student_code")
        appointment_type = data.get("appointment_type")
        appointment_date = data.get("appointment_date")
        appointment_time = data.get("appointment_time")
        location = data.get("location")

        if not all([student_code, appointment_type, appointment_date, appointment_time, location]):
            response = jsonify({"error": "Thiếu thông tin cần thiết"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 400

        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT student_id
                        FROM students
                        WHERE student_code = ?
                        """, (student_code,)
                    )
                    row = cursor.fetchone()
                    if not row:
                        response = jsonify({"error": "Không tìm thấy sinh viên"})
                        response.headers.add("Access-Control-Allow-Origin", "*")
                        return response, 404
                    student_id = row[0]

                    cursor.execute(
                        """
                        INSERT INTO appointments (student_id, advisor_id, appointment_type, appointment_date, appointment_time, location)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (student_id, advisor_id, appointment_type, appointment_date, appointment_time, location)
                    )
                    conn.commit()
                    response = jsonify({"message": "Tạo lịch hẹn thành công"})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response, 200
        except pyodbc.Error as e:
            response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 500

    elif request.method == "GET":
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT a.appointment_id, s.student_code, s.name, a.appointment_type,
                               a.appointment_date, a.appointment_time, a.location, a.created_at
                        FROM appointments a
                        JOIN students s ON a.student_id = s.student_id
                        WHERE a.advisor_id = ?
                        """, (advisor_id,)
                    )
                    rows = cursor.fetchall()
                    appointments = [
                        {
                            "appointment_id": row[0],
                            "student_code": row[1],
                            "student_name": row[2],
                            "type": row[3],
                            "date": row[4].isoformat() if row[4] else None,
                            "time": row[5],
                            "location": row[6],
                            "created_at": row[7].isoformat() if row[7] else None
                        }
                        for row in rows
                    ]
                    response = jsonify({"appointments": appointments})
                    response.headers.add("Access-Control-Allow-Origin", "*")
                    return response
        except pyodbc.Error as e:
            response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 500

    elif request.method == "PUT":
        data = request.json
        appointment_id = data.get("appointment_id")
        appointment_date = data.get("appointment_date")
        appointment_time = data.get("appointment_time")
        location = data.get("location")

        if not all([appointment_id, appointment_date, appointment_time, location]):
            response = jsonify({"error": "Thiếu thông tin cần thiết"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 400

        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE appointments
                        SET appointment_date = ?, appointment_time = ?, location = ?
                        WHERE appointment_id = ? AND advisor_id = ?
                        """, (appointment_date, appointment_time, location, appointment_id, advisor_id)
                    )
                    conn.commit()
                    if cursor.rowcount > 0:
                        response = jsonify({"message": "Cập nhật lịch hẹn thành công"})
                        response.headers.add("Access-Control-Allow-Origin", "*")
                        return response, 200
                    else:
                        response = jsonify({"error": "Không tìm thấy lịch hẹn"})
                        response.headers.add("Access-Control-Allow-Origin", "*")
                        return response, 404
        except pyodbc.Error as e:
            response = jsonify({"error": f"Lỗi cơ sở dữ liệu: {str(e)}"})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response, 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)