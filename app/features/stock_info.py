from app.features.company_lookup import is_stock_valid  # Add this line to import the function
from vnstock import stock_historical_data
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import datetime
import asyncio
import json


def get_stock_data(stock_name, start_date, end_date):
    df = stock_historical_data(stock_name, str(start_date), str(end_date), "1D", "stock")
    return df

def display_stock_info():
    st.title("Thông tin cổ phiếu")

    stock_name = st.text_input("Nhập tên cổ phiếu:")
    stock_name = stock_name.upper()

    if not is_stock_valid(stock_name):
        st.error("Xin nhập mã cổ phiếu chính xác")
        return
    
    start_date = st.date_input("Nhập ngày bắt đầu", datetime.date(2023, 1, 1))
    end_date = date.today()

    df_his = get_stock_data(stock_name, start_date, end_date)

    # Line chart
    df_his["time"] = pd.to_datetime(df_his["time"], format="%Y-%m-%d")
    fig = px.line(df_his, x="time", y="close", labels={"time": "Ngày thực tế", "close": "Giá đóng cửa"})
    st.plotly_chart(fig)

    # Biểu đồ nến và biểu đồ khối lượng
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3],
                        subplot_titles=("Biểu đồ nến", "Biểu đồ khối lượng"))

    # Biểu đồ nến
    fig.add_trace(go.Candlestick(x=df_his["time"],
                    open=df_his["open"],
                    high=df_his["high"],
                    low=df_his["low"],
                    close=df_his["close"],
                    name="Giá đóng cửa"))

    # Biểu đồ khối lượng
    fig.add_trace(go.Bar(x=df_his["time"], y=df_his["volume"], name="Khối lượng"), row=2, col=1)

    # Cài đặt các thông số khác của biểu đồ
    fig.update_layout(title_text="Biểu đồ giá cổ phiếu",
                    xaxis_title="Ngày thực tế",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    height=600,  # Thay đổi chiều cao của biểu đồ
                    width=800)   # Thay đổi chiều rộng của biểu đồ

    # Hiển thị biểu đồ trong ứng dụng Streamlit
    st.plotly_chart(fig)

    # Hiển thị biểu đồ giá và khối lượng sử dụng lightweight-charts
    st.subheader("Biểu đồ giá và khối lượng (Lightweight Charts)")

    priceVolumeChartOptions = {
        "height": 400,
        "rightPriceScale": {
            "scaleMargins": {
                "top": 0.2,
                "bottom": 0.25,
            },
            "borderVisible": False,
        },
        "overlayPriceScales": {
            "scaleMargins": {
                "top": 0.7,
                "bottom": 0,
            }
        },
        "layout": {
            "background": {
                "type": 'solid',
                "color": '#131722'
            },
            "textColor": '#d1d4dc',
        },
        "grid": {
            "vertLines": {
                "color": 'rgba(42, 46, 57, 0)',
            },
            "horzLines": {
                "color": 'rgba(42, 46, 57, 0.6)',
            }
        }
    }

    price_data = json.loads(df_his.to_json(orient='records', date_format='iso'))

    # Tính toán màu sắc dựa trên sự tăng giảm của giá
    price_colors = []
    for i in range(1, len(price_data)):
        if price_data[i]["close"] > price_data[i - 1]["close"]:
            color = 'rgba(0, 150, 136, 0.8)'  # Green color for price increase
        else:
            color = 'rgba(255, 82, 82, 0.8)'  # Red color for price decrease
        price_colors.append(color)

    priceVolumeSeries = [
        {
            "type": 'Area',
            "data": [{"time": entry["time"], "value": entry["close"]} for entry in price_data],
            "options": {
                "topColor": 'rgba(38,198,218, 0.56)',
                "bottomColor": 'rgba(38,198,218, 0.04)',
                "lineColor": 'rgba(38,198,218, 1)',
                "lineWidth": 2,
            }
        },
        {
            "type": 'Histogram',
            "data": [{"time": entry["time"], "value": entry["close"], "color": color} for entry, color in zip(price_data, price_colors)],
            "options": {
                "color": color,
                "priceFormat": {
                    "type": 'volume',
                },
                "priceScaleId": ""  # set as an overlay setting,
            },
            "priceScale": {
                "scaleMargins": {
                    "top": 0.7,
                    "bottom": 0,
                }
            }
        }
    ]

    renderLightweightCharts([
        {
            "chart": priceVolumeChartOptions,
            "series": priceVolumeSeries
        }
    ], 'priceAndVolume')

    # 
    n_days = st.slider('Số ngày dự đoán:', 1, 30)
    prediction = predict_stock_price(stock_name, n_days)
    st.line_chart(prediction["close"])