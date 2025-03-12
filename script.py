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
    df["distance_km"] = df.apply(lambda row: geodesic((user_lat, user_long), (row["latitude"], row["longitude"])).kilometers, axis=1)
    return df.nsmallest(num_results, "distance_km")

# G2G Cost Calculator
def g2g_cost_calculator(km, service_type):
    rates = {
        "COCO-UWL": (0, 24.04), "COCO-FBT": (0, 29.32),
        "ASP-UWL": (1600, 17), "ASP-FBT": (1800, 20)
    }
    
    if service_type not in rates:
        return "Invalid Service Type"
    
    basic_rate, per_km = rates[service_type]
    
    if "ASP" in service_type and km > 40:
        total_cost = basic_rate + ((km - 40) * per_km)
    else:
        total_cost = km * per_km  # COCO has no basic rate
    
    return total_cost

# Streamlit UI
def main():
    st.title("MSIL Nearest Workshop")
    
    if df.empty:
        st.warning("No data available. Please check the uploaded file.")
        return
    
    # Sidebar Calculators
    st.sidebar.title("📌 Calculators")
    
    # G2G Cost Calculator
    st.sidebar.subheader("🚗 G2G Cost Calculator")
    service_type = st.sidebar.selectbox("Select Service Type:", ["COCO-UWL", "COCO-FBT", "ASP-UWL", "ASP-FBT"])
    km_input = st.sidebar.number_input("Enter Total Distance (KM):", min_value=0, step=1)
    if st.sidebar.button("Calculate G2G Cost"):
        g2g_cost = g2g_cost_calculator(km_input, service_type)
        st.sidebar.success(f"Total Cost: ₹{g2g_cost:.2f}")
    
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
            st.dataframe(filtered_df)
        else:
            st.warning("No results found for the selected filters.")
    else:
        st.warning("Please enter valid Latitude and Longitude.")

if __name__ == "__main__":
    main()
