# run.py
import streamlit as st
from streamlit_option_menu import option_menu
import asyncio
from app.features import is_stock_valid, display_company_info, display_stock_info, predict_stock, trading_bot

options = ["Tra cứu doanh nghiệp", 'Hướng về tương lai', 'Hỗ trợ chứng khoán']

option_to_position = {}
for i, option in enumerate(options):
    option_to_position[option] = i

@st.cache_data()
def init():
    return {}

state = init()

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
            display_company_info()
        elif selected_position == 1:
            display_stock_info()
            predict_stock()
        elif selected_position == 2:
            trading_bot()

if __name__ == '__main__':
    asyncio.run(main())
