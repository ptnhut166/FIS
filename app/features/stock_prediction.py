# app/features/stock_prediction.py
import streamlit as st
import datetime 
import asyncio
from vnstock import *
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from datetime import date
from app.features.stock_info import is_stock_valid
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression

# Replace the following line with the actual import for the prediction function you are using
# from vnstock import predict_stock_price

# Mock function for demonstration purposes





def predict_stock():
    st.title("Dự đoán cổ phiếu")

    stock_name = st.text_input("Nhập tên cổ phiếu:",key =1)
    stock_name = stock_name.upper()

    if not is_stock_valid(stock_name):
        st.error("Xin nhập mã cổ phiếu chính xác")
        return

    n_days = st.slider('Số ngày dự đoán:', 1, 30, key=2)

    option = st.selectbox(
    'Chọn thuật toán dự đoán:',
    ('Linear Regression', 'ARIMA', 'GNN', 'LSTM', 'GRU', 'SSA', 'Random Forest'))
    st.write('Bạn chọn:', option)

    start_date = date.today() - timedelta(days= 365)
    end_date = date.today()
    df_origin = stock_historical_data(stock_name, str(start_date), str(end_date), "1D", "stock")
    # Chuẩn bị dữ liệu cho huấn luyện
    df = df_origin[['close']]
    df = df.dropna() # Drop missing values
    df = df.reset_index(drop=True) # Reset the index

    if option =='Linear Regression':
        # Split the data into training, testing, and validation sets
        train_size = int(0.7 * len(df))
        test_size = int(0.2 * len(df))
        val_size = len(df) - train_size - test_size

        train_data = df[:train_size]
        test_data = df[train_size:train_size+test_size]
        val_data = df[train_size+test_size:]
        # 3. Quá trình Training
        x_train = np.array(train_data.index).reshape(-1, 1)
        y_train = np.array(train_data['close'])
        model = LinearRegression()
        model.fit(x_train, y_train)
        # 4. Quá trình testing
        x_test = np.array(test_data.index).reshape(-1, 1)
        y_test = np.array(test_data['close'])
        y_pred = model.predict(x_test)

        # 5. Quá trình Validate
        x_val= np.array(val_data.index).reshape(-1, 1)
        y_val = np.array(val_data['close'])
        y_pred_val =  model.predict(x_val)
        # 6. Quá trình tạo index predict ndays ngày tiếp theo
        last_index =  df.index[-1]
        last_data = pd.RangeIndex(start=last_index, stop=last_index+n_days, step=1)
        # Create an array of 30 consecutive integers starting from last_index
        x_next_n_days = np.array(range(last_index+1, last_index+n_days+1)).reshape(-1, 1)
        # Predict the closing prices for the next 30 days
        y_next_n_days = model.predict(x_next_n_days)
    elif option =='ARIMA':
        # Split the data into training, testing, and validation sets
        train_size = int(0.7 * len(df))
        test_size = int(0.2 * len(df))
        val_size = len(df) - train_size - test_size

        train_data = df[:train_size]
        test_data = df[train_size:train_size+test_size]
        val_data = df[train_size+test_size:]
        # 3. Quá trình Training
        x_train = np.array(train_data.index).reshape(-1, 1)
        y_train = np.array(train_data['close'])
        # Find the best ARIMA model using auto_arima
        from pmdarima.arima import auto_arima
        model = auto_arima(y_train, trace=True, error_action='ignore', suppress_warnings=True)
        # Fit the model
        model.fit(y_train)
        # 4. Quá trình testing
        x_test = np.array(test_data.index).reshape(-1, 1)
        y_test = np.array(test_data['close'])
        y_pred = model.predict(n_periods=len(y_test))
        # 5. Quá trình Validate
        x_val= np.array(val_data.index).reshape(-1, 1)
        y_val = np.array(val_data['close'])
        y_pred_val =  model.predict(n_periods=len(y_val))
        # 6. Quá trình tạo index predict 30 ngày tiếp theo
        last_index =  df.index[-1]
        last_data = pd.RangeIndex(start=last_index, stop=last_index+n_days, step=1)
        # Create an array of 30 consecutive integers starting from last_index
        x_next_n_days = np.array(range(last_index+1, last_index+n_days+1)).reshape(-1, 1)
        # Predict the closing prices for the next 30 days
        y_next_n_days = model.predict(n_periods=len(x_next_n_days))
        # Print the predicted closing prices for the next n days
        print('Predicted closing prices for the next 30 days:')
        print(y_next_n_days)

    
    #elif option =='LSTM':
    #elif option =='GRU':
    #elif option =='SSA':
    #elif option =='Random Forest':


    


    


    

    st.title("Biểu đồ giá cổ phiếu")

    fig = px.line(df_origin, x="time", y="close", labels={"time": "Ngày thực tế", "close": "Giá đóng cửa"})

    # Thêm dòng này để tạo một cột mới cho x_next_30_days
    x_next_n_days = pd.date_range(start=df_origin['time'].max() + pd.Timedelta(days=1), periods=30)

    # Thêm dòng này để vẽ dữ liệu y next 30 days lên fig
    fig.add_scatter(x=x_next_n_days, y=y_next_n_days, mode='lines', name='Dự đoán')

    st.plotly_chart(fig)


    st.dataframe(y_next_n_days)


    




