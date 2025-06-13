import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from datetime import datetime
import streamlit.components.v1 as components

# Cấu hình giao diện
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
        .stApp {
            background-image: url('https://images.unsplash.com/photo-1517816743773-6e0fd518b4a6');
            background-size: cover;
            background-position: center;
        }
        header, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Logo và menu
st.sidebar.image("/mnt/data/40abd5fb-56fd-45ad-a8bd-8bce72d96b04.png", width=200)
menu = st.sidebar.selectbox("📋 Menu", ["Phân tích lô đề", "Đăng ký cá nhân"])

# Tiêu đề trang
st.markdown("<div class='main-title'>📊 Thống kê Lô Đề Miền Bắc</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Phân tích xác suất theo dữ liệu 10 năm</div>", unsafe_allow_html=True)

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
