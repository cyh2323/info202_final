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

        if "%" in rate_str:                                                 # Handle single percentage
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

# ------------------------------
# Sidebar – Product Type Selection
# ------------------------------
product_type = st.sidebar.selectbox(
    "Select Product Type",
    ["Credit Card", "Checking Account", "Savings Account"]
)

filtered = df[df["Type"] == product_type].copy()                            # Initialize the filtered dataset based on the selected product typ

# ------------------------------
# Sidebar – Goal Discovery (Options depend on Product Type)
# ------------------------------
if product_type == "Credit Card":
    goal_options = ["None", "Travel Rewards", "Cashback Value", "Low-Fee Simplicity"]
elif product_type == "Checking Account":
    goal_options = ["None", "Low-Fee Simplicity"]
elif product_type == "Savings Account":
    goal_options = ["None", "Low-Fee Simplicity", "High-Yield Savings"]
else:
    goal_options = ["None"]


goal = st.sidebar.selectbox(                                                # Goal selection
    "What is your main goal?",
    goal_options,
    index=0                                                                 # The goal is reset to "None" whenever the product type changes
)

st.sidebar.subheader("Direct Filters")                                      # Section for direct filters

# ------------------------------
# Type-Specific Filtering Logic
# ------------------------------
if product_type == "Credit Card":                                           # Credit cards are filtered primarily by reward type
    reward_options = filtered["Reward_or_Interest_Type"].dropna().unique().tolist()
    selected_reward = st.sidebar.multiselect("Reward Type", sorted(reward_options))
    
    if selected_reward:
        filtered = filtered[filtered["Reward_or_Interest_Type"].isin(selected_reward)]

elif product_type in ["Checking Account", "Savings Account"]:               
    min_apy = st.sidebar.number_input(                                      # Deposit accounts support interest-based filtering
        "Minimum Interest Rate / APY (%)",
        min_value=0.0,
        value=0.0,
        step=0.1,
        format="%.2f"
    )
    filtered = filtered[filtered["APY_num"] >= min_apy]                     # Filter by minimum APY

    atm_options = filtered["ATM_Access_Notes"].dropna().unique().tolist()   # ATM access filter      
    selected_atm = st.sidebar.multiselect("ATM Access", atm_options)

    mobile_options = filtered["Mobile_Check_Deposit_Support"].dropna().unique().tolist()          # Mobile or check deposit support filter
    selected_mobile = st.sidebar.multiselect("Mobile / Check Deposit Support", mobile_options)

    transfer_options = filtered["Transfer_Methods"].dropna().unique().tolist()                    # Transfer method filter (e.g., Zelle, ACH)
    selected_transfer = st.sidebar.multiselect("Transfer Methods", transfer_options)

    # Apply deposit account–specific filters
    if selected_atm:
        filtered = filtered[filtered["ATM_Access_Notes"].isin(selected_atm)]
    if selected_mobile:
        filtered = filtered[filtered["Mobile_Check_Deposit_Support"].isin(selected_mobile)]
    if selected_transfer:
        filtered = filtered[filtered["Transfer_Methods"].isin(selected_transfer)]

# ------------------------------
# Goal Discovery Filtering (Rule-Based)
# ------------------------------
# Apply additional filtering rules based on the selected user goal
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
         "Annual_Fee", "Reward_or_Interest_Type", "ATM_Access_Notes", "Mobile_Check_Deposit_Support", "Transfer_Methods"]
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
             "Annual_Fee", "Reward_or_Interest_Type", "ATM_Access_Notes", "Mobile_Check_Deposit_Support", "Transfer_Methods"]
        ]
    )