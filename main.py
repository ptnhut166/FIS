import streamlit as st
from streamlit_option_menu import option_menu
from vnstock import * 
from vnstock.chart import *

with st.sidebar:
    selected = option_menu("Lựa chọn", ["Thông tin", 'Dự đoán','Bot'], 
        icons=['info-square-fill', 'bar-chart-line-fill','reddit'], menu_icon="cast", default_index=1)
    selected
#_____________________________________________________________________________________  

global stock_name

if selected =="Thông tin":
    st.title("Thông tin công ty")
    df = listing_companies()
    stock_name = st.text_input("Nhập tên cổ phiếu:")
    stock_name = stock_name.upper()
        
    df = df['ticker']
    is_in = stock_name in df.unique()
    if is_in is True:
        st.header("Thông tin tổng quan")
    else:
        st.text("Không tìm thấy ")
        st.error("Xin nhập mã cổ phiếu chính xác")
        time.sleep(100000)
    
    company_info=company_overview(stock_name).drop(["industryID", "industryIDv2"], axis=1)
    st.table(company_info)
    df_cp=company_profile(stock_name)
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
elif selected=="Dự đoán":
    st.title("Thông tin cổ phiếu")

    df = listing_companies()
    stock_name = st.text_input("Nhập tên cổ phiếu:")
    stock_name = stock_name.upper()
        
    df = df['ticker']
    is_in = stock_name in df.unique()
    if is_in is True:
        st.header("Thông tin tổng quan")
    else:
        st.text("none")
        st.error("Xin nhập mã cổ phiếu chính xác")
        time.sleep(100000)

    
    selected_stock=stock_name
    

    

elif selected=="Bot":
    st.title("bot")


