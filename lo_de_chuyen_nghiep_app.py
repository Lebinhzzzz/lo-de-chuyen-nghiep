# lo_de_chuyen_nghiep_app.py

import pandas as pd
import streamlit as st
import plotly.express as px
from collections import Counter
from datetime import datetime

# Cấu hình giao diện Streamlit
st.set_page_config(page_title="Soi Cầu Lô Đề Chuyên Nghiệp", layout="wide")

# Tạo menu
menu = st.sidebar.selectbox("📋 Chọn chức năng", ["Phân tích lô đề", "Đăng ký nhận thông tin"])

# Giao diện đầu trang
st.markdown("""
    <h1 style='text-align: center; color: #e91e63;'>🔍 Soi Cầu - Lô Đề Miền Bắc</h1>
    <p style='text-align: center; color: gray;'>Phân tích thống kê xác suất từ dữ liệu 10 năm</p>
""", unsafe_allow_html=True)

# Hình ảnh minh họa
st.image("https://i.imgur.com/q7vP0G8.png", use_column_width=True, caption="Thống kê soi cầu lô đề")

if menu == "Phân tích lô đề":
    # Upload file CSV
    uploaded_file = st.file_uploader("📁 Tải lên dữ liệu lô đề (CSV)", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)

            # Kiểm tra dữ liệu đầu vào
            if 'Ngày' not in df.columns:
                st.error("❌ File CSV cần có cột 'Ngày'!")
                st.stop()

            # Chuyển cột 'Ngày' về kiểu datetime
            df['Ngày'] = pd.to_datetime(df['Ngày'], errors='coerce')
            df = df.dropna(subset=['Ngày'])

            # Chọn ngày phân tích
            selected_date = st.date_input("📅 Chọn ngày muốn phân tích", value=df['Ngày'].max().date())

            # Lọc dữ liệu trước ngày được chọn
            df_filtered = df[df['Ngày'] < pd.to_datetime(selected_date)]

            # Trích các con lô trong các dòng
            all_los = []
            for _, row in df_filtered.iterrows():
                for val in row[1:]:  # Bỏ cột 'Ngày'
                    if pd.notna(val):
                        lo = str(val).zfill(2)
                        if lo.isdigit() and len(lo) == 2:
                            all_los.append(lo)

            total = len(all_los)
            freq = Counter(all_los)
            prob = {lo: round((count / total) * 100, 3) for lo, count in freq.items()}
            sorted_prob = sorted(prob.items(), key=lambda x: x[1], reverse=True)

            # Hiển thị thống kê
            st.subheader("📊 Top 20 con lô có xác suất cao")
            df_top20 = pd.DataFrame(sorted_prob[:20], columns=["Lô", "Xác Suất (%)"])
            st.dataframe(df_top20, use_container_width=True)

            # Biểu đồ
            fig = px.bar(df_top20, x="Lô", y="Xác Suất (%)", color="Xác Suất (%)",
                         color_continuous_scale="reds", title="Biểu đồ xác suất xuất hiện")
            st.plotly_chart(fig, use_container_width=True)

            # Gợi ý top 3
            st.subheader("🎯 Gợi ý 3 con lô hôm nay")
            top3 = ", ".join([x[0] for x in sorted_prob[:3]])
            st.success(f"🔮 Nên chú ý: {top3}")

        except Exception as e:
            st.error(f"Đã xảy ra lỗi: {e}")
    else:
        st.info("⬆️ Vui lòng tải lên file dữ liệu để bắt đầu.")

elif menu == "Đăng ký nhận thông tin":
    st.subheader("📨 Đăng ký nhận thông tin thống kê lô đề")
    name = st.text_input("👤 Họ và tên")
    phone = st.text_input("📞 Số điện thoại")
    email = st.text_input("📧 Email")
    group = st.selectbox("💬 Bạn muốn tham gia nhóm nào?", ["Telegram", "Zalo", "Facebook", "Không tham gia"])

    if st.button("Đăng ký"):
        if name and (phone or email):
            st.success(f"✅ Cảm ơn {name}! Bạn đã đăng ký nhận thông tin.")
        else:
            st.warning("⚠️ Vui lòng điền ít nhất họ tên và số điện thoại hoặc email.")
