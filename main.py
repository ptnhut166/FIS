import streamlit as st
from streamlit_option_menu import option_menu
from vnstock import * 
from vnstock.chart import *
import datetime
from datetime import date
from functools import lru_cache
import asyncio
import json
from streamlit_lightweight_charts import renderLightweightCharts
import plotly.express as px
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Define the options
options = ["Tra cứu doanh nghiệp", 'Hướng về tương lai', 'Hỗ trợ chứng khoán']

# Create a dictionary to map the options to their positions
option_to_position = {}
for i, option in enumerate(options):
    option_to_position[option] = i

@lru_cache()
def is_stock_valid(stock_name):
    df = listing_companies()
    stocks = df['ticker'].unique()
    return stock_name in stocks

@lru_cache()
# Define the get_stock_data function
async def get_stock_data(stock_name, start_date, end_date):
    df = stock_historical_data(stock_name, str(start_date), str(end_date), "1D", "stock")
    return df

async def predict_stock_price(stock_name, n_days):
    df = await get_stock_data(stock_name, date.today() - datetime.timedelta(days=30), date.today())
    # TODO: Implement the prediction algorithm
    return df

async def main():

    with st.sidebar:
        selected_option = option_menu(
            "Danh mục", options, 
            icons=['info-square-fill', 'bar-chart-line-fill','reddit'], 
            menu_icon="justify", 
            default_index=1
        )

    with st.container():
        selected_position = option_to_position[selected_option]
        if selected_position == 0:
            st.title("Thông tin doanh nghiệp")
            stock_name = st.text_input("Nhập tên cổ phiếu:")
            stock_name = stock_name.upper()

            if not is_stock_valid(stock_name):
                st.error("Xin nhập mã cổ phiếu chính xác")
                return

            company_info = company_overview(stock_name).drop(["industryID", "industryIDv2"], axis=1)
            st.table(company_info)

            df_cp = company_profile(stock_name)
            name = df_cp["companyName"].iloc[0]
            pro = df_cp["companyProfile"].iloc[0]
            his = df_cp["historyDev"].iloc[0]

            st.title(name)
            st.markdown(pro)
            st.header("Lịch sử")
            st.markdown(his)

            st.header("Danh sách cổ đông")
            df_sh=company_large_shareholders (symbol=stock_name).iloc[:, 1:]

            st.table(df_sh)

            st.header("Các chỉ số tài chính cơ bản")
            st.table((company_fundamental_ratio (symbol=stock_name, mode='simplify', missing_pct=0.8)).drop(["ticker"], axis=1))

            st.header("Mức biến động giá cổ phiếu")
            st.table(ticker_price_volatility (symbol=stock_name).drop(["ticker"], axis=1))

            st.header("Thông tin giao dịch nội bộ")
            st.table(company_insider_deals (symbol=stock_name, page_size=20, page=0).drop(["ticker"], axis=1))

            st.header("Danh sách các công ti con, công ti liên kết")
            st.table(company_subsidiaries_listing (symbol=stock_name, page_size=100, page=0).drop(["ticker"], axis=1))

            st.header("Ban lãnh đạo")
            df_off=company_officers (symbol=stock_name, page_size=20, page=0).dropna()
            df_off=df_off.drop(["ticker"], axis=1)
            st.table(df_off)
    #_____________________________________________________________________________________  
        elif selected_position == 1:
            st.title("Thông tin cổ phiếu")

            stock_name = st.text_input("Nhập tên cổ phiếu:")
            stock_name = stock_name.upper()

            if not is_stock_valid(stock_name):
                st.error("Xin nhập mã cổ phiếu chính xác")
                return
            
            start_date = st.date_input("Nhập ngày bắt đầu", datetime.date(2020, 1, 1))
            end_date = date.today()

            df_his = await get_stock_data(stock_name, start_date, end_date)

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

            n_days = st.slider('Số ngày dự đoán:', 1, 30)
            prediction = await predict_stock_price(stock_name, n_days)
            st.line_chart(prediction["close"])

        elif selected_position == 2:
            st.title("Giao dịch tự động")
            st.markdown("Trading bot with oanda")

if __name__ == '__main__':
    asyncio.run(main())
