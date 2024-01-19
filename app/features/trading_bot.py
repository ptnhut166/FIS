# app/features/trading_bot.py
import streamlit as st
from openai import OpenAI
from vnstock import *
from datetime import date
from datetime import timedelta

def trading_bot():
    st.title("Chat bot hỗ trợ chứng khoán")
    st.markdown("Chat bot")

    client = OpenAI(api_key=st.secrets["API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.text_input("Xin chào!", key="user_input", help="Nhập câu hỏi ở đây"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Check if the user is asking for stock information
        if "giá cổ phiếu" in prompt.lower():
            stock_symbol = st.text_input("Nhập tên cổ phiếu:", key="stock_symbol", help="Enter stock symbol here")
            if stock_symbol:
                # Get stock information from yfinance
                stock_price = get_stock_data(stock_symbol)
                st.session_state.messages.append({"role": "assistant", "content": f"Stock Information for {stock_symbol}: {stock_price}"})
                with st.chat_message("assistant"):
                    st.markdown(f"Giá hiện tại của cổ phiếu {stock_symbol} là: {stock_price}")

        else:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for response in client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                ):
                    full_response += (response.choices[0].delta.content or "")
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# Hàm để lấy thông tin tài chính từ vnstock
def get_stock_data(stock_name):
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()
    df = stock_historical_data(stock_name, str(start_date), str(end_date), "1D", "stock")
    return df


# Kiểm tra nếu trang đã được làm mới
if st.button("Refresh"):
    # Đặt biến refreshed trong session_state thành True
    st.session_state.refreshed = True

# Sử dụng cảm lệnh CSS để đặt thanh nhập câu hỏi xuống phía dưới cùng
st.markdown(
    """
    <style>
    div[data-testid="stTextInput"] {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
