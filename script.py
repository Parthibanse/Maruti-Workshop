import streamlit as st
import pandas as pd
from geopy.distance import geodesic

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
required_columns = ["pincode", "channel", "body shop", "state", "latitude", "longitude"]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"Missing columns in the dataset: {', '.join(missing_columns)}")
    st.stop()

# Function to find nearest workshops using latitude and longitude
def get_nearest_workshops(pincode, df, num_results=5):
    user_location = df[df["pincode"].astype(str) == str(pincode)][["latitude", "longitude"]].values
    if user_location.size == 0:
        return df.head(num_results)  # Return default results if pincode not found
    user_location = tuple(user_location[0])
    
    df["distance"] = df.apply(lambda row: geodesic(user_location, (row["latitude"], row["longitude"])).km, axis=1)
    return df.nsmallest(num_results, "distance")

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
        filtered_df = get_nearest_workshops(pincode, df)
    if channel != "All":
        filtered_df = filtered_df[filtered_df["channel"] == channel]
    if body_shop != "All":
        filtered_df = filtered_df[filtered_df["body shop"] == body_shop]
    if state != "All":
        filtered_df = filtered_df[filtered_df["state"] == state]
    
    # Display filtered data
    if not filtered_df.empty:
        st.write("### Filtered Workshops")
        st.dataframe(filtered_df.drop(columns=["distance"], errors='ignore'))
    else:
        st.warning("No results found for the selected filters.")

if __name__ == "__main__":
    main()