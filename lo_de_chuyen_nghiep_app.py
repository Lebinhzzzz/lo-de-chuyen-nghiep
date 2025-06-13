import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from datetime import datetime
import os

# Cấu hình giao diện
st.set_page_config(page_title="Soi cầu lô đề chuyên nghiệp", layout="wide")

# Menu chính
menu = st.sidebar.selectbox("📋 Menu", ["Phân tích lô đề", "Đăng ký cá nhân", "Nhóm hội thoại"])

st.markdown("""
    <h1 style='text-align: center; color: #e91e63;'>📊 Thống kê Lô Đề Miền Bắc</h1>
    <p style='text-align: center; color: gray;'>Phân tích xác suất theo dữ liệu 10 năm</p>
""", unsafe_allow_html=True)

# Hình ảnh minh họa
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
        st.dataframe(df_top20, use_container_width=True)

        fig = px.bar(df_top20, x="Lô", y="Số lần xuất hiện", color="Xác Suất (%)",
                     color_continuous_scale="reds", title="Biểu đồ tần suất và xác suất")
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
    st.subheader("💬 Nhóm hội thoại thành viên")

    with st.form(key="chat_form"):
        message = st.text_input("💭 Nhập tin nhắn", placeholder="Nhập nội dung...")
        submit = st.form_submit_button("Gửi")
        if submit and message.strip():
            with open("chat_group.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message.strip()}\n")
            st.success("📨 Tin nhắn đã gửi!")

    st.markdown("### 📜 Lịch sử hội thoại")
    if os.path.exists("chat_group.txt"):
        with open("chat_group.txt", "r", encoding="utf-8") as f:
            chat_history = f.read()
        st.text_area("📩 Nội dung hội thoại", chat_history, height=400, disabled=True, key='chat_display')
    else:
        st.info("💬 Chưa có tin nhắn nào.")
