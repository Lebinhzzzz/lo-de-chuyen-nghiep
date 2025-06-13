import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import json

# Khởi tạo Firebase từ Streamlit Secrets
if not firebase_admin._apps:
    firebase_json = st.secrets["FIREBASE_KEY"]
    cred = credentials.Certificate(json.loads(firebase_json))
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://YOUR_PROJECT_ID.firebaseio.com'
    })

# Hàm Firebase chat
def send_message(group, user, msg):
    ref = db.reference(f"messages/{group}")
    ref.push({
        "user": user,
        "msg": msg,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def fetch_messages(group):
    ref = db.reference(f"messages/{group}")
    data = ref.get()
    if not data: return []
    return sorted(data.values(), key=lambda x: x['time'])

# Giao diện
st.set_page_config(page_title="Soi cầu lô đề chuyên nghiệp", layout="wide")
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            color: #e91e63;
            font-size: 3em;
            font-weight: bold;
        }
        .subtitle {
            text-align: center;
            color: gray;
            font-size: 1.2em;
        }
        .stButton>button {
            background-color: #e91e63;
            color: white;
            border-radius: 8px;
            padding: 0.5em 1em;
        }
    </style>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox("📋 Menu", ["Phân tích lô đề", "Đăng ký cá nhân", "Nhóm hội thoại"])

st.markdown("<div class='main-title'>📊 Thống kê Lô Đề Miền Bắc</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Phân tích xác suất theo dữ liệu 10 năm</div>", unsafe_allow_html=True)

st.image("https://i.imgur.com/q7vP0G8.png", use_column_width=True)

if menu == "Phân tích lô đề":
    uploaded_file = st.file_uploader("📂 Tải lên file CSV dữ liệu lô đề", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        if 'Ngày' not in df.columns:
            st.error("❗ Cần có cột 'Ngày' trong file CSV!")
            st.stop()

        df['Ngày'] = pd.to_datetime(df['Ngày'], errors='coerce')
        df = df.dropna(subset=['Ngày'])

        selected_date = st.date_input("📅 Chọn ngày muốn phân tích", value=df['Ngày'].max().date())
        df_filtered = df[df['Ngày'] < pd.to_datetime(selected_date)]

        all_los = []
        for _, row in df_filtered.iterrows():
            for val in row[1:]:
                if pd.notna(val):
                    lo = str(val).zfill(2)
                    if lo.isdigit() and len(lo) == 2:
                        all_los.append(lo)

        total = len(all_los)
        freq = Counter(all_los)
        prob = {lo: round((count / total) * 100, 2) for lo, count in freq.items()}
        sorted_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        sorted_prob = [(lo, prob[lo]) for lo, _ in sorted_items]

        st.subheader("🔢 Top 20 lô có xác suất cao")
        df_top20 = pd.DataFrame(sorted_prob[:20], columns=["Lô", "Xác Suất (%)"])
        df_top20['Số lần xuất hiện'] = [freq[lo] for lo in df_top20['Lô']]
        st.dataframe(df_top20, use_container_width=True, height=400)

        fig = px.bar(df_top20, x="Lô", y="Số lần xuất hiện", color="Xác Suất (%)",
                     color_continuous_scale="reds", title="Biểu đồ tần suất và xác suất")
        fig.update_layout(plot_bgcolor='#fff', paper_bgcolor='#fdfdfd')
        st.plotly_chart(fig, use_container_width=True)

        top3 = ", ".join([x[0] for x in sorted_prob[:3]])
        st.success(f"🎯 Gợi ý hôm nay: {top3}")

elif menu == "Đăng ký cá nhân":
    st.subheader("🧍 Đăng ký tài khoản cá nhân")
    name = st.text_input("👤 Họ và tên")
    email = st.text_input("📧 Email")
    phone = st.text_input("📱 Số điện thoại")

    if st.button("Đăng ký"):
        if name and (email or phone):
            user_info = f"{datetime.now()}, {name}, {email}, {phone}\n"
            with open("users.csv", "a") as f:
                f.write(user_info)
            st.success("✅ Đăng ký thành công!")
        else:
            st.warning("⚠️ Vui lòng điền đủ thông tin!")

elif menu == "Nhóm hội thoại":
    st.subheader("💬 Nhóm hội thoại thành viên (Firebase Real-time)")

    group = st.selectbox("Chọn nhóm", ["nhom1", "nhom2", "nhom3"])
    username = st.text_input("Tên bạn", value="Ẩn danh")

    with st.form(key="chat_form"):
        message = st.text_input("💭 Nhập tin nhắn", placeholder="Nhập nội dung...")
        submit = st.form_submit_button("Gửi")
        if submit and message.strip():
            send_message(group, username, message.strip())
            st.success("📨 Tin nhắn đã gửi!")

    st.markdown("---")
    st.subheader(f"🗨 Tin nhắn trong nhóm `{group}`")
    messages = fetch_messages(group)
    chat_html = ""
    for item in messages[-30:]:
        chat_html += f"<p><strong>{item['user']}</strong> ({item['time']}): {item['msg']}</p>"

    components.html(f"""
        <div style='background:#f9f9f9;padding:15px;border-radius:10px;max-height:300px;overflow:auto'>
            {chat_html}
        </div>
    """, height=350)
