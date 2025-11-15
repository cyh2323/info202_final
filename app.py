import streamlit as st
import pandas as pd

# CSV 불러오기
df = pd.read_csv("bank_products.csv")

st.title("Bank Product Recommender 💳")

# 사용자 입력
purpose = st.selectbox("What is your goal?", ["Travel", "Cashback", "Savings"])
annual_fee = st.checkbox("No annual fee only")

# 추천 로직
filtered = df.copy()
if purpose == "Travel":
    filtered = filtered[filtered["reward_type"].str.contains("travel", case=False, na=False)]
elif purpose == "Cashback":
    filtered = filtered[filtered["reward_type"].str.contains("cashback", case=False, na=False)]

if annual_fee:
    filtered = filtered[filtered["annual_fee"] == 0]

st.write("### Recommended Products")
st.dataframe(filtered[["product_name", "bank", "reward_rate", "annual_fee"]])