import streamlit as st
import pandas as pd

# Load the dataset
FILE_PATH = "Workshop details.xlsx"
try:
    df = pd.read_excel(FILE_PATH)
    df.columns = df.columns.str.strip().str.lower()  # Normalize column names
except FileNotFoundError:
    st.error("Error: The specified file was not found. Please upload the correct file.")
    st.stop()
except Exception as e:
    st.error(f"Error loading the file: {e}")
    st.stop()

# Check if required columns exist
required_columns = ["pincode", "channel", "body shop", "state"]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"Missing columns in the dataset: {', '.join(missing_columns)}")
    st.stop()

# Function to find nearest pincodes based on the first five digits
def get_nearest_pincodes(pincode, df, num_results=5):
    df["pincode"] = df["pincode"].astype(str)
    pincode_prefix = str(pincode)[:5]  # Get first five digits of pincode
    nearest_df = df[df["pincode"].str.startswith(pincode_prefix)]
    return nearest_df.head(num_results) if not nearest_df.empty else df.head(num_results)

# Streamlit UI
def main():
    st.title("Workshop Dashboard")
    
    if df.empty:
        st.warning("No data available. Please check the uploaded file.")
        return
    
    # Search by Pincode
    pincode = st.text_input("Enter Pincode:")
    
    # Filters
    channels = df["channel"].dropna().unique().tolist()
    channel = st.selectbox("Select Channel:", ["All"] + channels)
    
    body_shop = st.selectbox("Body Shop:", ["All"] + sorted(df["body shop"].dropna().unique()))
    
    states = df["state"].dropna().unique().tolist()
    state = st.selectbox("Select State:", ["All"] + states)
    
    # Filter data based on inputs
    filtered_df = df.copy()
    if pincode:
        filtered_df = get_nearest_pincodes(pincode, df)
    if channel != "All":
        filtered_df = filtered_df[filtered_df["channel"] == channel]
    if body_shop != "All":
        filtered_df = filtered_df[filtered_df["body shop"] == body_shop]
    if state != "All":
        filtered_df = filtered_df[filtered_df["state"] == state]
    
    # Display filtered data
    if not filtered_df.empty:
        st.write("### Filtered Workshops")
        st.dataframe(filtered_df)
    else:
        st.warning("No results found for the selected filters.")

if __name__ == "__main__":
    main()