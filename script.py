import streamlit as st
import pandas as pd
import numpy as np
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
required_columns = ["latitude", "longitude", "channel", "body shop", "state"]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"Missing columns in the dataset: {', '.join(missing_columns)}")
    st.stop()

# Function to find nearest workshops based on lat/long
def get_nearest_workshops(user_lat, user_long, df, num_results=5):
    df = df.copy()
    df["distance"] = df.apply(lambda row: geodesic((user_lat, user_long), (row["latitude"], row["longitude"])).kilometers, axis=1)
    return df.nsmallest(num_results, "distance")

# Streamlit UI
def main():
    st.title("Workshop Dashboard")
    
    if df.empty:
        st.warning("No data available. Please check the uploaded file.")
        return
    
    # Search by Latitude & Longitude
    user_lat = st.number_input("Enter Latitude:", format="%0.6f")
    user_long = st.number_input("Enter Longitude:", format="%0.6f")
    
    # Filters
    channels = df["channel"].dropna().unique().tolist()
    channel = st.selectbox("Select Channel:", ["All"] + channels)
    
    body_shop = st.selectbox("Body Shop:", ["All"] + sorted(df["body shop"].dropna().unique()))
    
    states = df["state"].dropna().unique().tolist()
    state = st.selectbox("Select State:", ["All"] + states)
    
    # Filter data based on inputs
    if user_lat and user_long:
        filtered_df = get_nearest_workshops(user_lat, user_long, df)
        if channel != "All":
            filtered_df = filtered_df[filtered_df["channel"] == channel]
        if body_shop != "All":
            filtered_df = filtered_df[filtered_df["body shop"] == body_shop]
        if state != "All":
            filtered_df = filtered_df[filtered_df["state"] == state]
        
        # Display filtered data
        if not filtered_df.empty:
            st.write("### Nearest Workshops")
            st.dataframe(filtered_df.drop(columns=["distance"], errors='ignore'))
        else:
            st.warning("No results found for the selected filters.")
    else:
        st.warning("Please enter valid Latitude and Longitude.")

if __name__ == "__main__":
    main()
