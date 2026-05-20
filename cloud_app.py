import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from sklearn.linear_model import LinearRegression

# =================================================================
# 1. CẤU HÌNH HẠ TẦNG GIAO DIỆN CHUẨN ĐỒ ÁN KHỞI NGHIỆP SAAS
# =================================================================
st.set_page_config(page_title="Hệ Thống Quản Trị Y Tế - Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #e2e8f0; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); 
    }
    h1, h2, h3 { color: #1e293b; font-family: 'Arial', sans-serif; }
    .ai-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .warning-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        border-left: 5px solid #ef4444;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .success-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        border-left: 5px solid #10b981;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .chart-insight-card {
        background-color: #f8fafc;
        padding: 15px;
        border-radius: 8px;
        border: 1px dashed #cbd5e1;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# 2. BỘ ĐỆM ĐỌC DỮ LIỆU TỰ ĐỘNG CHỐNG LỖI TÊN FILE
# =================================================================
@st.cache_data
def load_hospital_data():
    file_options = ['Data_Tong.xlsx', 'Data_Tong.xlsx - Sheet1.csv', 'Data_Tong.csv']
    for file_name in file_options:
        if os.path.exists(file_name):
            try:
                if file_name.endswith('.xlsx'):
                    return pd.read_excel(file_name, engine='openpyxl')
                else:
                    return pd.read_csv(file_name, encoding='utf-8')
            except Exception:
                try:
                    return pd.read_csv(file_name, encoding='utf-8')
                except Exception:
                    continue
    return None

df = load_hospital_data()

if df is not None:
    df.columns = df.columns.str.strip()
    
    # =================================================================
    # 3. THANH ĐIỀU HÀNH SIDEBAR (HỆ THỐNG LỌC TỐI ƯU)
    # =================================================================
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=70)
    st.sidebar.header("🏥 HỆ THỐNG LỌC")
    
    danh_sach_bv = sorted(df['Ten_Benh_Vien'].unique().tolist())
    selected_bv = st.sidebar.selectbox(
        "Chọn Bệnh viện cần xem:",
        options=danh_sach_bv,
        index=0
    )
    
    df_filtered = df[df['Ten_Benh_Vien'] == selected_bv]
    
    danh_sach_khoa = sorted(df_filtered['Khoa'].unique().tolist())
    selected_khoa = st.sidebar.multiselect(
        "Chọn Khoa phòng:", 
        options=danh_sach_khoa, 
        default=danh_sach_khoa
    )
    
    final_df = df_filtered[df_filtered['Khoa'].isin(selected_khoa)]

    # =================================================================
    # 4. TIÊU ĐỀ CHÍNH & CHỈ SỐ TỔNG QUAN (METRICS)
    # =================================================================
    st.title(f"📊 Dashboard KPI: {selected_bv}")
    st.markdown(f"**Khu vực:** {final_df['Khu_Vuc'].iloc[0] if not final_df.empty else 'N/A'}")

    m1, m2, m3, m4 = st.columns(4)
    total_rev = final_df['Doanh_Thu'].sum()
    total_pat = final_df['Benh_Nhan'].sum()
    wait_avg = final_df['Thoi_Gian_Cho'].mean()
    power_sum = final_df['Luong_Dien_KWh'].sum()

    m1.metric("Tổng Doanh Thu", f"{total_rev:,.0f} VNĐ")
    m2.metric("Tổng Bệnh Nhân", f"{total_pat:,.0f} Người")
    m3.metric("TG Chờ Trung Bình", f"{wait_avg:.1f} Phút")
    m4.metric("Điện Năng Tiêu Thụ", f"{power_sum:,.0f} KWh")

    st.write("---")

    # =================================================================
    # 5. TIÊU ĐỀ AI THEO BẠN CHỌN & LỚP XỬ LÝ HỌC MÁY
    # =================================================================
    st.subheader("🔮 Hệ Thống Giám Sát & Tối Ưu Hóa Phụ Tải Tự Động AI")
    st.write("Phân tích thực nghiệm dựa trên mô hình Hồi quy Tuyến tính (Linear Regression) để mô phỏng sự dịch chuyển phụ tải điện năng theo lưu lượng.")
    
    if not final_df.empty and len(final_df) >= 2:
        X_train = final_df[['Benh_Nhan']].values
        y_train = final_df['Luong_Dien_KWh'].values

        ai_model = LinearRegression()
        ai_model.fit(X_train, y_train)
        
        r_squared = ai_model.score(X_train, y_train)
        
        st.markdown("##### 🎛️ Bộ Giả Lập Kịch Bản Tải Lượng Hệ Thống Cấp Cao")
        pct_increase = st.slider("Giả định % lưu lượng Bệnh nhân gia tăng đột biến (Giờ cao điểm / Dịch bệnh):", 
                                 min_value=10, max_value=100, value=30, step=5)
        
        simulated_patients = int(total_pat * (1 + pct_increase/100))
        avg_patients_per_khoa = simulated_patients / len(final_df)
        predicted_power_total = ai_model.predict([[avg_patients_per_khoa]])[0] * len(final_df)
        predicted_co2_total = predicted_power_total * 0.7221
        
        col_ai1, col_ai2 = st.columns(2)
        
        with col_ai1:
            st.markdown(f"""
            <div class="ai-card">
                <h4 style="color: #1e3a8a; margin-top:0;">📊 Kết quả mô phỏng Kịch bản Tăng trưởng (+{pct_increase}%)</h4>
                <p>Khi lưu lượng toàn viện chạm ngưỡng dự kiến: <b>{simulated_patients:,} Bệnh nhân</b></p>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 12px 0;">
                <ul style="padding-left: 20px; margin-bottom: 0;">
                    <li style="margin-bottom: 8px;">Dự báo tổng nhu cầu năng lượng lưới: <span style="color:#2563eb; font-weight:bold;">{predicted_power_total:,.1f} kWh</span></li>
                    <li style="margin-bottom: 8px;">Tải lượng dấu chân Carbon dự kiến: <span style="color:#d97706; font-weight:bold;">{predicted_co2_total:,.1f} kg CO₂</span></li>
                    <li>Độ tin cậy thuật toán (R² Score): <span style="color:#10b981; font-weight:bold;">{r_squared:.4f}</span></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col_ai2:
            max_wait_time = final_df['Thoi_Gian_Cho'].max()
            overloaded_khoa = final_df[final_df['Thoi_Gian_Cho'] == max_wait_time]['Khoa'].values[0]
            
            if max_wait_time > 45:
                st.markdown(f"""
                <div class="warning-card">
                    <h4 style="color: #991b1b; margin-top:0;">🚨 Cảnh báo Điểm nóng Quá tải Vận hành (Bottleneck)</h4>
                    <p>Xung đột dòng chảy luồng bệnh nhân cục bộ tại chuyên khoa:</p>
                    <hr style="border: 0; border-top: 1px solid #fee2e2; margin: 12px 0;">
                    <p style="margin-bottom: 8px;">📍 Khoa phòng chịu áp lực lớn nhất: <b style="color:#ef4444;">Khoa {overloaded_khoa}</b></p>
                    <p style="margin-bottom: 8px;">⏱️ Thời gian chờ đợi đỉnh điểm: <b style="color:#ef4444;">{max_wait_time:.1f} phút</b></p>
                    <p style="font-size: 13px; color: #7f1d1d; font-weight: 500; margin-top: 5px;">
                        ⚠️ ĐỀ XUẤT ĐIỀU HÀNH: Điều động khẩn cấp nhân sự hỗ trợ khâu số hóa thủ tục tiếp đón tại Khoa {overloaded_khoa}.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-card">
                    <h4 style="color: #065f46; margin-top:0;">✅ Trạng thái Đồng bộ An toàn Toàn viện</h4>
                    <p>Hệ thống ghi nhận các chỉ số phối hợp tài nguyên đang nằm trong dải tối ưu:</p>
                    <hr style="border: 0; border-top: 1px solid #d1fae5; margin: 12px 0;">
                    <p>Thời gian chờ tối đa tại chuyên khoa cao nhất: <b>{max_wait_time:.1f} Phút</b> (Đạt ngưỡng an toàn định mức).</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Vui lòng chọn từ 2 khoa phòng trở lên ở mục Sidebar để thuật toán AI thực hiện phân tích đối sánh.")

    st.write("---")

    # =================================================================
    # 6. PHẦN TRỰC QUAN HÓA ĐỒ THỊ CHUYÊN SÂU & ĐÁNH GIÁ BIỂU ĐỒ TỰ ĐỘNG
    # =================================================================
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📊 Hiệu suất Bệnh nhân & Giường bệnh")
        fig_bar = px.bar(
            final_df, 
            x='Khoa', 
            y=['Benh_Nhan', 'Tong_Giuong'],
            barmode='group',
            labels={'value': 'Số lượng', 'variable': 'Chỉ số'},
            color_discrete_sequence=['#1f77b4', '#aec7e8']
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with c2:
        st.subheader("🌱 Tỷ trọng Năng lượng theo Khoa")
        fig_pie = px.pie(
            final_df, 
            values='Luong_Dien_KWh', 
            names='Khoa',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # --- ĐOẠN CODE PHÂN TÍCH ĐÁNH GIÁ BIỂU ĐỒ 2 TỰ ĐỘNG ---
        if not final_df.empty:
            idx_max_power = final_df['Luong_Dien_KWh'].idxmax()
            idx_min_power = final_df['Luong_Dien_KWh'].idxmin()
            
            highest_khoa = final_df.loc[idx_max_power, 'Khoa']
            highest_value = final_df.loc[idx_max_power, 'Luong_Dien_KWh']
            lowest_khoa = final_df.loc[idx_min_power, 'Khoa']
            lowest_value = final_df.loc[idx_min_power, 'Luong_Dien_KWh']
            
            percentage_highest = (highest_value / power_sum) * 100 if power_sum > 0 else 0
            
            st.markdown(f"""
            <div class="chart-insight-card">
                <b style="color: #0f172a; font-size: 14px;">📝 Đánh giá & Phân tích cơ cấu năng lượng (AI Insights):</b>
                <p style="font-size: 13px; color: #334155; margin-top: 8px; line-height: 1.5;">
                    • <b>Điểm nóng tiêu thụ:</b> Khoa <span style="color:#ef4444; font-weight:bold;">{highest_khoa}</span> đang đứng đầu danh sách sử dụng điện với <b>{highest_value:,.0f} KWh</b>, chiếm xấp xỉ <b>{percentage_highest:.1f}%</b> tổng năng lượng vận hành của cơ sở y tế này. Đây là mục tiêu cốt lõi cần triển khai hệ thống kiểm soát điện thông minh.<br>
                    • <b>Đơn vị tối ưu xanh:</b> Khoa <span style="color:#10b981; font-weight:bold;">{lowest_khoa}</span> ghi nhận mức tiêu thụ thấp nhất với <b>{lowest_value:,.0f} KWh</b>.<br>
                    • <b>Khuyến nghị quản trị cấp cao:</b> Ban Giám Đốc cần xem xét quy trình kiểm toán năng lượng độc lập đối với khoa <i>{highest_khoa}</i> nhằm sàng lọc các thiết bị cũ lãng phí, bám sát lộ trình cắt giảm phát thải Net Zero của toàn viện.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # =================================================================
    # 7. BẢNG CHI TIẾT NGUỒN
    # =================================================================
    with st.expander("📂 Xem chi tiết bảng dữ liệu nguồn"):
        st.dataframe(final_df, use_container_width=True)

else:
    st.warning("Vui lòng kiểm tra file Data_Tong.xlsx trong thư mục dự án.")