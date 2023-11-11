# app/features/stock_prediction.py
import streamlit as st
import datetime
import asyncio

# Replace the following line with the actual import for the prediction function you are using
# from vnstock import predict_stock_price

# Mock function for demonstration purposes
async def predict_stock_price(stock_name, n_days):
    # Implement your own prediction logic or use another library
    # ...
    pass

async def predict_stock():
    st.title("Dự đoán cổ phiếu")

    stock_name = st.text_input("Nhập tên cổ phiếu:")
    stock_name = stock_name.upper()

    if not is_stock_valid(stock_name):
        st.error("Xin nhập mã cổ phiếu chính xác")
        return

    n_days = st.slider('Số ngày dự đoán:', 1, 30)
    prediction = await predict_stock_price(stock_name, n_days)
    st.line_chart(prediction["close"])
