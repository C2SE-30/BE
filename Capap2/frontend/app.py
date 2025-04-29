import streamlit as st
import pandas as pd
import requests
import io
import base64
import time
from datetime import datetime, date
from dateutil.parser import parse

# URL backend Flask
BASE_URL = "http://localhost:5000"

# Hàm gọi API
def call_api(method, endpoint, json=None, files=None, params=None):
    try:
        if method == "post":
            response = requests.post(f"{BASE_URL}/{endpoint}", json=json, files=files, params=params)
        elif method == "get":
            response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
        elif method == "put":
            response = requests.put(f"{BASE_URL}/{endpoint}", json=json)
        elif method == "delete":
            response = requests.delete(f"{BASE_URL}/{endpoint}", params=params)
        if response.status_code in [200, 204]:
            return response.json() if response.status_code == 200 else None, None
        else:
            return None, response.json().get("error", f"Lỗi {response.status_code}")
    except requests.RequestException as e:
        return None, f"Lỗi kết nối: {str(e)}"

# Hàm kiểm tra quyền truy cập
def protected_route(allowed_role):
    if "user" not in st.session_state:
        st.error("Vui lòng đăng nhập để truy cập trang này.")
        st.stop()
    if st.session_state["user"]["role"].lower() != allowed_role.lower():
        st.error(f"Truy cập bị từ chối. Trang này chỉ dành cho {allowed_role}.")
        st.stop()

# Trang đăng nhập
def login_page():
    st.title("Đăng Nhập")
    email = st.text_input("Email")
    password = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        user, error = call_api("post", "login", json={"username": email, "password": password})
        if user:
            st.session_state["user"] = user["user"]
            st.success("Đăng nhập thành công!")
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error(error or "Email hoặc mật khẩu không đúng")

# Trang chủ sinh viên
def student_home():
    protected_route("student")
    st.title("Trang Chủ Sinh Viên")
    user_id = st.session_state["user"]["id"]
    data, error = call_api("get", f"student/{user_id}")
    if data:
        student = data["student"]
        st.markdown("""
            <style>
            .student-info {
                border: 1px solid #e0e0e0;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .avatar-container {
                text-align: center;
                margin-bottom: 20px;
            }
            .avatar {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                object-fit: cover;
            }
            .detail-link {
                color: #007bff;
                text-decoration: none;
                font-size: 14px;
                cursor: pointer;
            }
            .info-container {
                display: flex;
                justify-content: space-between;
                gap: 20px;
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                margin-top: 20px;
            }
            .feature-card {
                border: 1px solid #e0e0e0;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                background-color: #f9f9f9;
            }
            .feature-card h3 {
                margin: 10px 0;
                font-size: 18px;
            }
            .feature-card p {
                color: #666;
                font-size: 14px;
                margin-bottom: 15px;
            }
            .icon {
                font-size: 40px;
                color: #007bff;
                margin-bottom: 10px;
            }
            .error {
                color: red;
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="student-info">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="avatar-container">', unsafe_allow_html=True)
            try:
                st.image("student_avatar.png", width=150, caption="")
            except FileNotFoundError:
                st.write("Không có ảnh avatar")
            if st.button("Xem chi tiết", key="view_profile"):
                st.session_state["page"] = "student_profile"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.subheader("Thông tin sinh viên")
            col_left, col_right = st.columns(2)
            with col_left:
                st.write(f"**MSSV:** {student['student_code']}")
                st.write(f"**Họ tên:** {student['name']}")
                st.write(f"**E-mail:** {student['email']}")
            with col_right:
                st.write(f"**Ngành:** {student['major']}")
        st.markdown('</div>', unsafe_allow_html=True)
        if error:
            st.markdown(f'<p class="error">{error}</p>', unsafe_allow_html=True)
        st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown('<div class="icon">📬</div>', unsafe_allow_html=True)
            st.markdown("<h3>Thông báo & Gợi ý</h3>", unsafe_allow_html=True)
            st.markdown("<p>Nhận thông báo & gợi ý cải thiện</p>", unsafe_allow_html=True)
            if st.button("Xem thông báo", key="notifications"):
                st.session_state["page"] = "notifications"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown('<div class="icon">💬</div>', unsafe_allow_html=True)
            st.markdown("<h3>Phản hồi & Hành động</h3>", unsafe_allow_html=True)
            st.markdown("<p>Trả lời thông báo & thực hiện hành động</p>", unsafe_allow_html=True)
            if st.button("Thực hiện ngay", key="actions"):
                st.session_state["page"] = "actions"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown('<div class="icon">📚</div>', unsafe_allow_html=True)
            st.markdown("<h3>Cải thiện học tập</h3>", unsafe_allow_html=True)
            st.markdown("<p>Đề xuất tài liệu & hỗ trợ học tập</p>", unsafe_allow_html=True)
            if st.button("Khám phá ngay", key="resources"):
                st.session_state["page"] = "resources"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    elif error:
        st.error(error)
        if st.button("Quay lại đăng nhập"):
            st.session_state["user"] = None
            st.session_state["page"] = "login"
            st.rerun()
    else:
        st.write("Đang tải...")

# Trang hồ sơ sinh viên
def student_profile():
    protected_route("student")
    st.title("Hồ Sơ Sinh Viên")
    user_id = st.session_state["user"]["id"]
    data, error = call_api("get", f"student-profile/{user_id}")
    st.markdown("""
        <style>
        .section {
            border: 1px solid #e0e0e0;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .profile-content {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        .avatar {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
        }
        .info {
            flex: 1;
        }
        .update-button {
            text-align: center;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    if data:
        student = data["student"]
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("Thông tin học vấn")
        st.markdown('<div class="profile-content">', unsafe_allow_html=True)
        try:
            st.image("student_avatar.png", width=150, caption="")
        except FileNotFoundError:
            st.write("Không có ảnh avatar")
        st.markdown('<div class="info">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**MSSV:** {student['student_code']}")
            st.write(f"**Họ tên:** {student['name']}")
            st.write(f"**Giới tính:** {student['gender']}")
            st.write(f"**Ngày sinh:** {student['birth_date']}")
            st.write(f"**E-mail:** {student['email']}")
            st.write(f"**Số điện thoại:** {student['phone']}")
        with col2:
            st.write(f"**CCCD:** {student['id_number']}")
            st.write(f"**Trạng thái:** {student['status']}")
            st.write(f"**Lớp học:** {student['class']}")
            st.write(f"**Bậc đào tạo:** {student['level']}")
            st.write(f"**Khoa:** {student['department']}")
            st.write(f"**Ngành:** {student['major']}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("Địa chỉ hiện thời")
        st.write(f"**Địa chỉ:** {student['current_address']['street']}, {student['current_address']['ward']}, {student['current_address']['district']}, {student['current_address']['city']}, {student['current_address']['country']}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("Người liên hệ khẩn cấp")
        st.write(f"**Tên:** {student['emergency_contact']['name']}")
        st.write(f"**Quan hệ:** {student['emergency_contact']['relationship']}")
        st.write(f"**Địa chỉ:** {student['emergency_contact']['address']['street']}, {student['emergency_contact']['address']['ward']}, {student['emergency_contact']['address']['district']}, {student['emergency_contact']['address']['city']}, {student['emergency_contact']['address']['country']}")
        st.write(f"**Số điện thoại:** {student['emergency_contact']['phone']}")
        st.write(f"**Email:** {student['emergency_contact']['email']}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.subheader("Cập nhật thông tin")
        with st.form(key="update_profile_form"):
            name = st.text_input("Họ tên", value=student["name"])
            email = st.text_input("E-mail", value=student["email"])
            phone = st.text_input("Số điện thoại", value=student["phone"])
            major = st.text_input("Ngành học", value=student["major"])
            gender = st.selectbox("Giới tính", ["Nam", "Nữ"], index=["Nam", "Nữ"].index(student["gender"]) if student["gender"] in ["Nam", "Nữ"] else 0)
            birth_date = st.date_input("Ngày sinh", value=parse(student["birth_date"]) if student["birth_date"] else date.today())
            id_number = st.text_input("CCCD", value=student["id_number"])
            class_name = st.text_input("Lớp học", value=student["class"])
            level = st.text_input("Bậc đào tạo", value=student["level"])
            department = st.text_input("Khoa", value=student["department"])
            current_address_street = st.text_input("Địa chỉ (Đường)", value=student["current_address"]["street"])
            current_address_ward = st.text_input("Phường", value=student["current_address"]["ward"])
            current_address_district = st.text_input("Quận", value=student["current_address"]["district"])
            current_address_city = st.text_input("Thành phố", value=student["current_address"]["city"])
            current_address_country = st.text_input("Quốc gia", value=student["current_address"]["country"])
            emergency_contact_name = st.text_input("Tên người liên hệ khẩn cấp", value=student["emergency_contact"]["name"])
            emergency_contact_relationship = st.text_input("Quan hệ", value=student["emergency_contact"]["relationship"])
            emergency_contact_phone = st.text_input("Số điện thoại liên hệ khẩn cấp", value=student["emergency_contact