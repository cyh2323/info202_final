import streamlit as st
import pandas as pd

st.set_page_config(page_title="Bank Product Recommender", layout="wide")    # Set page title and layout

# ------------------------------
# Load Data
# ------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("input_data.csv", encoding="utf-8-sig")                # Load CSV data
    df.columns = df.columns.str.strip()                                     # Remove whitespace from column names
    return df

df = load_data()                                                            # Load the dataset

# ------------------------------
# Utility Functions
# ------------------------------
def parse_apy(rate_str):                                                    # Function for converting APY string to float
    try:
        if pd.isna(rate_str):                                               # Handle missing values
            return 0.0
        rate_str = str(rate_str)

        if "%" in rate_str:                                               # Handle single percentage
            return float(rate_str.replace("%", "").strip())
        else:                                                               
            return float(rate_str.strip())

    except Exception:                                                       # Handle invalid format
        return 0.0

df["APY_num"] = df["Interest_Rate_APY"].apply(parse_apy)                    # Add numeric APY column

# ------------------------------
# Sidebar – User Preferences
# ------------------------------
st.sidebar.header("User Preferences & Goal Discovery")                      # Sidebar header

goal = st.sidebar.radio(                                                    # User goal selection
    "What is your main goal?",
    ["Travel Rewards", "Cashback Value", "Low-Fee Simplicity", "High-Yield Savings"]
)

st.sidebar.subheader("Direct Filters")                                      # Section for direct filters

max_fee = st.sidebar.number_input("Max Annual Fee ($)", min_value=0, value=100)    # Max annual fee

min_apy = st.sidebar.number_input(                                          # Minimum APY
    "Minimum Interest Rate / APY (%)",
    min_value=0.0,
    value=0.0,
    step=0.1,
    format="%.2f"
)

reward_filter = st.sidebar.multiselect(                                     # Reward type filter
    "Reward Type",
    sorted(df['Reward_or_Interest_Type'].dropna().unique())
)

# ------------------------------
# Filtering Logic
# ------------------------------
filtered = df.copy()                                                        # Copy dataframe for filtering

filtered = filtered[filtered["Annual_Fee"] <= max_fee]                      # Annual Fee Filter

filtered = filtered[filtered["APY_num"] >= min_apy]                         # Filter by min APY
 
if reward_filter:                                                           # Apply reward type filter
    filtered = filtered[filtered["Reward_or_Interest_Type"].isin(reward_filter)]

# Goal Discovery filtering
if goal == "Travel Rewards":                                               
    filtered = filtered[
        filtered["Reward_or_Interest_Type"]
        .str.contains("travel|miles|point", case=False, na=False)
    ]

elif goal == "Cashback Value":
    filtered = filtered[
        filtered["Reward_or_Interest_Type"]
        .str.contains("cash", case=False, na=False)
    ]

elif goal == "Low-Fee Simplicity":
    filtered = filtered[filtered["Annual_Fee"] == 0]

elif goal == "High-Yield Savings":
    filtered = filtered[
        (filtered["Type"].str.contains("Savings", case=False, na=False)) &
        (filtered["APY_num"] > 0.01)
    ]

# ------------------------------
# Main Page
# ------------------------------
st.title("Personalized Banking Product Recommendations")                      # Main page title

st.markdown(
    f"### Showing **{len(filtered)}** recommended products based on your preferences."   # Display count
)

# Show results table
st.dataframe(
    filtered[
        ["Name", "Bank", "Type", "Interest_Rate_APY",
         "Annual_Fee", "Reward_or_Interest_Type", "Notes"]
    ],
    use_container_width=True
)

# ------------------------------
# Product Comparison
# ------------------------------
st.subheader("Compare Selected Products (up to 3)")                          # Comparison header
compare_selection = st.multiselect(                                          # User selects up to 3 products for side-by-side comparison
    "Select products to compare",
    filtered["Name"].tolist(),
    max_selections=3
)

if compare_selection:                                                        # If any product selected for comparison
    compare_df = filtered[filtered["Name"].isin(compare_selection)]

    st.write("### Side-by-Side Comparison")                                  # Comparison table title
    st.table(
        compare_df[
            ["Name", "Bank", "Type", "Interest_Rate_APY",
             "Annual_Fee", "Reward_or_Interest_Type", "Notes"]
        ]
    )