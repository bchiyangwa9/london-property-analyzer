
"""
Enhanced London Property Analyzer - Dual Mode System
Combines individual property analysis with bulk search & discovery
Includes graphs, maps, and comprehensive data analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import requests
import json
import time
from datetime import datetime
import base64
from io import BytesIO
import os
import sys

# Import our custom modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from property_scraper import PropertyScraper
    from automation_engine import AutomationEngine
    from api_simulator import APISimulator
except ImportError:
    st.error("Please ensure property_scraper.py, automation_engine.py, and api_simulator.py are in the same directory")

# Page config
st.set_page_config(
    page_title="London Property Analyzer - Dual Mode",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'properties_df' not in st.session_state:
    st.session_state.properties_df = pd.DataFrame()
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'scraper' not in st.session_state:
    st.session_state.scraper = PropertyScraper()
if 'automation_engine' not in st.session_state:
    st.session_state.automation_engine = AutomationEngine()
if 'api_simulator' not in st.session_state:
    st.session_state.api_simulator = APISimulator()

# Sidebar configuration
st.sidebar.title("🏠 Property Analyzer Settings")

# Reference postcode settings
st.sidebar.subheader("📍 Reference Location")
reference_postcode = st.sidebar.text_input(
    "Home/Work Postcode", 
    value="SE1 9SP", 
    help="All commute times and distances will be calculated from this location (London Bridge Station default)"
)

# Budget settings
st.sidebar.subheader("💰 Budget Criteria")
min_budget = st.sidebar.number_input("Minimum Budget (£)", min_value=100000, max_value=2000000, value=300000, step=10000)
max_budget = st.sidebar.number_input("Maximum Budget (£)", min_value=100000, max_value=2000000, value=420000, step=10000)

# Basic requirements
st.sidebar.subheader("🏡 Basic Requirements")
min_bedrooms = st.sidebar.selectbox("Minimum Bedrooms", [1, 2, 3, 4, 5], index=2)
max_commute = st.sidebar.slider("Max Commute Time (minutes)", 15, 120, 60, 5)

# Scoring weights (advanced)
with st.sidebar.expander("⚖️ Scoring Weights"):
    st.write("Adjust the importance of each category:")
    price_weight = st.slider("Price Importance", 0.1, 0.4, 0.2, 0.05)
    commute_weight = st.slider("Commute Importance", 0.1, 0.4, 0.2, 0.05)
    property_type_weight = st.slider("Property Type Importance", 0.05, 0.25, 0.15, 0.05)
    bedrooms_weight = st.slider("Bedrooms Importance", 0.05, 0.25, 0.15, 0.05)
    outdoor_weight = st.slider("Outdoor Space Importance", 0.05, 0.15, 0.1, 0.05)
    schools_weight = st.slider("Schools Importance", 0.05, 0.15, 0.1, 0.05)
    grammar_weight = st.slider("Grammar School Bonus", 0.05, 0.15, 0.1, 0.05)

# Main app
st.title("🏠 London Property Analyzer - Dual Mode System")
st.markdown("**Comprehensive property search, analysis, and scoring platform**")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Add Property", 
    "🔍 Search & Discover", 
    "📊 Analysis & Graphs",
    "🗺️ Property Map",
    "🏆 Top 5 Dashboard"
])

# Helper functions
def calculate_property_score(property_data):
    """Calculate comprehensive property score using current weights"""
    try:
        score = 0

        # Price score (0-20 points)
        if property_data.get('price'):
            price = property_data['price']
            if price <= min_budget:
                price_score = 20
            elif price >= max_budget:
                price_score = 0
            else:
                # Linear scoring between min and max budget
                price_score = 20 * (max_budget - price) / (max_budget - min_budget)
            score += price_score * (price_weight / 0.2)  # Normalize to weight

        # Commute score (0-20 points)  
        commute_time = property_data.get('commute_time', 60)
        if commute_time <= 30:
            commute_score = 20
        elif commute_time >= max_commute:
            commute_score = 0
        else:
            commute_score = 20 * (max_commute - commute_time) / (max_commute - 30)
        score += commute_score * (commute_weight / 0.2)

        # Property type score (0-15 points)
        property_type = property_data.get('property_type', '').lower()
        if 'house' in property_type:
            type_score = 15
        elif 'maisonette' in property_type or 'duplex' in property_type:
            type_score = 12
        elif 'flat' in property_type or 'apartment' in property_type:
            type_score = 8
        else:
            type_score = 5
        score += type_score * (property_type_weight / 0.15)

        # Bedrooms score (0-15 points)
        bedrooms = property_data.get('bedrooms', 0)
        if bedrooms >= min_bedrooms + 2:
            bedroom_score = 15
        elif bedrooms >= min_bedrooms + 1:
            bedroom_score = 12
        elif bedrooms >= min_bedrooms:
            bedroom_score = 8
        else:
            bedroom_score = max(0, bedrooms * 3)
        score += bedroom_score * (bedrooms_weight / 0.15)

        # Outdoor space score (0-10 points)
        outdoor = property_data.get('outdoor_space', 'None').lower()
        if any(word in outdoor for word in ['garden', 'terrace', 'patio']):
            outdoor_score = 10
        elif 'balcony' in outdoor:
            outdoor_score = 6
        else:
            outdoor_score = 2
        score += outdoor_score * (outdoor_weight / 0.1)

        # Schools score (0-10 points)
        school_rating = property_data.get('nearest_school_ofsted', 'Good')
        if school_rating == 'Outstanding':
            school_score = 10
        elif school_rating == 'Good':
            school_score = 7
        elif school_rating == 'Requires Improvement':
            school_score = 4
        else:
            school_score = 2
        score += school_score * (schools_weight / 0.1)

        # Grammar school bonus (0-10 points)
        grammar_distance = property_data.get('grammar_school_distance', 999)
        if grammar_distance <= 2:
            grammar_score = 10
        elif grammar_distance <= 5:
            grammar_score = 6
        elif grammar_distance <= 10:
            grammar_score = 3
        else:
            grammar_score = 0
        score += grammar_score * (grammar_weight / 0.1)

        return min(100, max(0, round(score, 1)))

    except Exception as e:
        st.error(f"Error calculating score: {str(e)}")
        return 0

def add_property_to_dataframe(property_data):
    """Add a new property to the session dataframe"""
    if st.session_state.properties_df.empty:
        st.session_state.properties_df = pd.DataFrame([property_data])
    else:
        # Check if property already exists
        existing = st.session_state.properties_df[
            st.session_state.properties_df['property_id'] == property_data['property_id']
        ]
        if existing.empty:
            new_df = pd.DataFrame([property_data])
            st.session_state.properties_df = pd.concat([st.session_state.properties_df, new_df], ignore_index=True)
        else:
            st.warning(f"Property {property_data['property_id']} already exists!")
            return False
    return True

def get_mock_auto_data(postcode):
    """Get mock calculated data for auto-filled fields"""
    try:
        # Use API simulator for consistent mock data
        commute_time = st.session_state.api_simulator.get_commute_time(reference_postcode, postcode)
        station_distance = st.session_state.api_simulator.get_nearest_station_distance(postcode)
        school_rating = st.session_state.api_simulator.get_school_rating(postcode)
        grammar_distance = st.session_state.api_simulator.get_grammar_school_distance(postcode)

        return {
            'commute_time': commute_time,
            'distance_to_station': station_distance,
            'nearest_school_ofsted': school_rating,
            'grammar_school_distance': grammar_distance,
            'summary_description': f"Property in {postcode} area with {commute_time}min commute"
        }
    except Exception as e:
        return {
            'commute_time': 45,
            'distance_to_station': 0.8,
            'nearest_school_ofsted': 'Good', 
            'grammar_school_distance': 5.2,
            'summary_description': f"Property in {postcode} area"
        }

# TAB 1: Add Property (Individual Analysis)
with tab1:
    st.header("🏠 Individual Property Analysis")
    st.markdown("Enter property details manually or import from URL")

    # Quick import section
    with st.expander("🚀 Quick Import from URL", expanded=False):
        st.markdown("**Paste a property URL to auto-fill most fields:**")

        col1, col2 = st.columns([3, 1])
        with col1:
            import_url = st.text_input(
                "Property URL", 
                placeholder="https://www.rightmove.co.uk/properties/123456789 or Zoopla/OnTheMarket URL",
                help="Supports Rightmove, Zoopla, and OnTheMarket URLs"
            )
        with col2:
            if st.button("🔍 Fetch Details", type="primary"):
                if import_url:
                    with st.spinner("Scraping property details..."):
                        scraped_data = st.session_state.scraper.scrape_single_property(import_url)

                        if scraped_data and not scraped_data.get('error'):
                            st.success("✅ Property details imported successfully!")

                            # Store scraped data in session state for form population
                            st.session_state.scraped_property = scraped_data
                            st.rerun()
                        else:
                            error_msg = scraped_data.get('error', 'Unknown error') if scraped_data else 'Failed to scrape'
                            st.error(f"❌ Failed to import: {error_msg}")
                else:
                    st.warning("Please enter a property URL")

    # Main property entry form
    st.subheader("📝 Property Information")

    # Initialize form data
    form_data = {}
    if 'scraped_property' in st.session_state:
        form_data = st.session_state.scraped_property
        # Clear after use
        del st.session_state.scraped_property

    # Basic Information
    with st.expander("🏷️ Basic Information", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            property_id = st.text_input(
                "Property ID *", 
                value=form_data.get('property_id', ''),
                help="Unique identifier for this property"
            )
            property_url = st.text_input(
                "Property URL", 
                value=form_data.get('url', ''),
                help="Link to the property listing"
            )
            price = st.number_input(
                "Price (£) *", 
                min_value=50000, 
                max_value=5000000, 
                value=form_data.get('price') or min_budget,
                step=5000
            )
            property_type = st.selectbox(
                "Property Type *", 
                ["House", "Flat", "Maisonette", "Bungalow", "Other"],
                index=0 if not form_data.get('property_type') else 
                      ['house', 'flat', 'maisonette', 'bungalow', 'other'].index(
                          next((t for t in ['house', 'flat', 'maisonette', 'bungalow', 'other'] 
                                if t in form_data.get('property_type', '').lower()), 'house')
                      )
            )

        with col2:
            bedrooms = st.selectbox(
                "Bedrooms *", 
                [1, 2, 3, 4, 5, 6],
                index=form_data.get('bedrooms', min_bedrooms) - 1 if form_data.get('bedrooms') else min_bedrooms - 1
            )
            postcode = st.text_input(
                "Postcode *", 
                value=form_data.get('postcode', ''),
                help="Used for commute and local area calculations"
            )
            tenure = st.selectbox(
                "Tenure", 
                ["Freehold", "Leasehold", "Unknown"],
                index=0
            )
            lease_years = st.number_input(
                "Lease Years (if Leasehold)", 
                min_value=0, 
                max_value=999, 
                value=999 if tenure == "Freehold" else 99
            )

    # Agent and Property Details
    with st.expander("🏢 Agent & Property Details"):
        col1, col2 = st.columns(2)

        with col1:
            agent_name = st.text_input(
                "Agent Name", 
                value=form_data.get('agent_name', '')
            )
            agent_phone = st.text_input(
                "Agent Phone", 
                value=form_data.get('agent_phone', '')
            )
            outdoor_space = st.selectbox(
                "Outdoor Space *", 
                ["Garden", "Terrace", "Balcony", "Patio", "None"],
                index=0
            )

        with col2:
            # Get auto-calculated data when postcode is provided
            auto_data = {}
            if postcode:
                auto_data = get_mock_auto_data(postcode)

            st.markdown("**📊 Auto-Calculated Fields:**")
            commute_time = st.number_input(
                "Commute Time (min) [AUTO]", 
                value=auto_data.get('commute_time', 45),
                disabled=True,
                help="Automatically calculated based on postcode and reference location"
            )
            distance_to_station = st.number_input(
                "Distance to Station (km) [AUTO]", 
                value=auto_data.get('distance_to_station', 0.8),
                disabled=True,
                help="Distance to nearest train station"
            )
            nearest_school_ofsted = st.selectbox(
                "Nearest School Ofsted [AUTO]", 
                ["Outstanding", "Good", "Requires Improvement", "Inadequate"],
                index=["Outstanding", "Good", "Requires Improvement", "Inadequate"].index(
                    auto_data.get('nearest_school_ofsted', 'Good')
                ),
                disabled=True
            )

    # Additional Information
    with st.expander("📋 Additional Information"):
        grammar_school_distance = st.number_input(
            "Grammar School Distance (km) [AUTO]", 
            value=auto_data.get('grammar_school_distance', 5.2),
            disabled=True
        )

        summary_description = st.text_area(
            "Summary Description [AUTO]", 
            value=auto_data.get('summary_description', form_data.get('description', '')),
            height=100,
            disabled=True,
            help="Auto-generated summary based on property details"
        )

    # Calculate and display score
    if property_id and price and postcode:
        current_property = {
            'property_id': property_id,
            'url': property_url,
            'price': price,
            'property_type': property_type,
            'bedrooms': bedrooms,
            'postcode': postcode,
            'tenure': tenure,
            'lease_years': lease_years,
            'outdoor_space': outdoor_space,
            'agent_name': agent_name,
            'agent_phone': agent_phone,
            'commute_time': commute_time,
            'distance_to_station': distance_to_station,
            'nearest_school_ofsted': nearest_school_ofsted,
            'grammar_school_distance': grammar_school_distance,
            'summary_description': summary_description,
            'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        score = calculate_property_score(current_property)
        current_property['total_score'] = score

        # Score display
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.subheader("🎯 Property Score")
            # Color-coded score bar
            if score >= 80:
                bar_color = "🟢"
                score_color = "green"
            elif score >= 60:
                bar_color = "🟡"
                score_color = "orange"
            else:
                bar_color = "🔴"
                score_color = "red"

            st.markdown(f"### {bar_color} **{score}/100 points**")
            st.progress(score/100)

        with col2:
            if st.button("💾 Add Property", type="primary", use_container_width=True):
                if add_property_to_dataframe(current_property):
                    st.success("✅ Property added successfully!")
                    st.balloons()

        with col3:
            if st.button("🔄 Clear Form", use_container_width=True):
                st.rerun()

# TAB 2: Search & Discover (Bulk Analysis)
with tab2:
    st.header("🔍 Property Search & Bulk Discovery")
    st.markdown("Search for properties by area and import multiple properties at once")

    # Search criteria
    st.subheader("📍 Area Search")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_postcode = st.text_input("Search Postcode/Area", value="SE1 0AA", help="Center point for property search")
        search_radius = st.selectbox("Search Radius (miles)", [1, 3, 5, 10, 15, 20], index=2)

    with col2:
        search_min_price = st.number_input("Min Price (£)", min_value=100000, value=min_budget, step=10000)
        search_max_price = st.number_input("Max Price (£)", min_value=100000, value=max_budget, step=10000)

    with col3:
        search_min_beds = st.selectbox("Min Bedrooms", [1, 2, 3, 4, 5], index=2)
        search_property_type = st.selectbox("Property Type", ["Any", "House", "Flat", "Bungalow"])

    # Generate search URLs
    if st.button("🔗 Generate Search URLs", type="primary"):
        with st.spinner("Generating search URLs..."):
            search_urls = st.session_state.scraper.generate_search_urls(
                postcode=search_postcode,
                radius=search_radius,
                min_price=search_min_price,
                max_price=search_max_price,
                min_bedrooms=search_min_beds,
                property_type=search_property_type if search_property_type != "Any" else None
            )

            st.success("🔗 Search URLs generated! Click to browse properties:")

            for site, url in search_urls.items():
                st.markdown(f"**{site}:** [Open {site} Search]({url})")

    st.markdown("---")

    # Experimental: Auto search
    with st.expander("🤖 Experimental: Automated Search (May be blocked)", expanded=False):
        st.warning("⚠️ This feature may be blocked by anti-bot measures. Use responsibly and consider Terms of Service.")

        col1, col2 = st.columns(2)
        with col1:
            auto_search_site = st.selectbox("Choose Site", ["Rightmove", "Zoopla", "OnTheMarket"])
            search_limit = st.slider("Max Results", 5, 50, 20)

        with col2:
            if st.button("🔍 Auto Search", type="secondary"):
                if search_postcode:
                    with st.spinner(f"Searching {auto_search_site} (this may take 30+ seconds)..."):
                        search_urls = st.session_state.scraper.generate_search_urls(
                            postcode=search_postcode,
                            radius=search_radius,
                            min_price=search_min_price,
                            max_price=search_max_price,
                            min_bedrooms=search_min_beds,
                            property_type=search_property_type if search_property_type != "Any" else None
                        )

                        search_url = search_urls.get(auto_search_site)
                        if search_url:
                            results = st.session_state.scraper.attempt_search_scraping(
                                search_url, auto_search_site.lower(), search_limit
                            )

                            if results:
                                st.session_state.search_results = results
                                st.success(f"✅ Found {len(results)} properties!")
                            else:
                                st.error("❌ No results found or search blocked")

        # Display search results
        if st.session_state.search_results:
            st.subheader("🏠 Search Results")

            for i, result in enumerate(st.session_state.search_results):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(f"**{result.get('title', 'Property')}**")
                        st.markdown(f"Price: {result.get('price_text', 'N/A')}")
                        st.markdown(f"Source: {result.get('source', 'Unknown')}")

                    with col2:
                        st.markdown(f"[View Property]({result['url']})")

                    with col3:
                        if st.button(f"➕ Import", key=f"import_{i}"):
                            with st.spinner("Importing property..."):
                                scraped = st.session_state.scraper.scrape_single_property(result['url'])
                                if scraped and not scraped.get('error'):
                                    # Add auto-calculated data
                                    auto_data = get_mock_auto_data(scraped.get('postcode', ''))
                                    scraped.update(auto_data)
                                    scraped['total_score'] = calculate_property_score(scraped)
                                    scraped['added_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                                    if add_property_to_dataframe(scraped):
                                        st.success("✅ Property imported!")
                                else:
                                    st.error("❌ Import failed")

                    st.markdown("---")

    # Batch URL import
    st.subheader("📋 Batch URL Import")
    st.markdown("Paste multiple property URLs (one per line) to import them all at once:")

    batch_urls = st.text_area(
        "Property URLs", 
        height=150,
        placeholder="""https://www.rightmove.co.uk/properties/123456789
https://www.zoopla.co.uk/for-sale/details/987654321
https://www.onthemarket.com/details/123456/""",
        help="Paste one URL per line. Supports Rightmove, Zoopla, and OnTheMarket."
    )

    if batch_urls:
        urls = [url.strip() for url in batch_urls.split('\n') if url.strip()]

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            st.metric("URLs Found", len(urls))

        with col2:
            if st.button("🚀 Process All URLs", type="primary"):
                if urls:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    with st.spinner("Processing properties in parallel..."):
                        results = st.session_state.scraper.scrape_multiple_properties(urls, max_workers=2)

                        processed_count = 0
                        success_count = 0

                        for i, result in enumerate(results):
                            progress_bar.progress((i + 1) / len(results))
                            status_text.text(f"Processing {i + 1}/{len(results)}...")

                            if result and not result.get('error'):
                                # Add auto-calculated data
                                auto_data = get_mock_auto_data(result.get('postcode', ''))
                                result.update(auto_data)
                                result['total_score'] = calculate_property_score(result)
                                result['added_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                                if add_property_to_dataframe(result):
                                    success_count += 1

                            processed_count += 1

                        progress_bar.progress(1.0)
                        status_text.text("✅ Processing complete!")

                        st.success(f"✅ Successfully imported {success_count}/{processed_count} properties!")
                        if success_count > 0:
                            st.balloons()

        with col3:
            st.markdown("**Preview URLs:**")
            for i, url in enumerate(urls[:3]):
                domain = url.split('/')[2] if '/' in url else url
                st.markdown(f"• {domain}")
            if len(urls) > 3:
                st.markdown(f"... and {len(urls) - 3} more")

# TAB 3: Analysis & Graphs
with tab3:
    st.header("📊 Property Analysis & Graphs")

    if st.session_state.properties_df.empty:
        st.info("📋 No properties added yet. Use the 'Add Property' tab to get started!")
    else:
        df = st.session_state.properties_df

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Properties", len(df))

        with col2:
            avg_price = df['price'].mean()
            st.metric("Average Price", f"£{avg_price:,.0f}")

        with col3:
            avg_score = df['total_score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}/100")

        with col4:
            top_score = df['total_score'].max()
            st.metric("Highest Score", f"{top_score:.1f}/100")

        st.markdown("---")

        # Graphs row 1
        col1, col2 = st.columns(2)

        with col1:
            # Price distribution histogram
            fig_price = px.histogram(
                df, 
                x='price', 
                nbins=20,
                title="Property Price Distribution",
                labels={'price': 'Price (£)', 'count': 'Number of Properties'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_price.update_layout(showlegend=False)
            st.plotly_chart(fig_price, use_container_width=True)

        with col2:
            # Score distribution
            fig_score = px.histogram(
                df, 
                x='total_score', 
                nbins=15,
                title="Property Score Distribution", 
                labels={'total_score': 'Total Score', 'count': 'Number of Properties'},
                color_discrete_sequence=['#ff7f0e']
            )
            fig_score.update_layout(showlegend=False)
            st.plotly_chart(fig_score, use_container_width=True)

        # Graphs row 2
        col1, col2 = st.columns(2)

        with col1:
            # Property type breakdown
            type_counts = df['property_type'].value_counts()
            fig_type = px.pie(
                values=type_counts.values, 
                names=type_counts.index,
                title="Property Type Breakdown"
            )
            st.plotly_chart(fig_type, use_container_width=True)

        with col2:
            # Bedrooms distribution
            bed_counts = df['bedrooms'].value_counts().sort_index()
            fig_beds = px.bar(
                x=bed_counts.index, 
                y=bed_counts.values,
                title="Bedroom Count Distribution",
                labels={'x': 'Number of Bedrooms', 'y': 'Number of Properties'},
                color=bed_counts.values,
                color_continuous_scale='viridis'
            )
            fig_beds.update_layout(showlegend=False)
            st.plotly_chart(fig_beds, use_container_width=True)

        # Graphs row 3
        col1, col2 = st.columns(2)

        with col1:
            # Price vs Commute time scatter
            fig_scatter = px.scatter(
                df, 
                x='commute_time', 
                y='price',
                size='total_score',
                color='total_score',
                hover_data=['property_id', 'postcode'],
                title="Price vs Commute Time (sized by score)",
                labels={'commute_time': 'Commute Time (min)', 'price': 'Price (£)'},
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col2:
            # Radar chart for top 5 properties
            top_5 = df.nlargest(5, 'total_score')

            if len(top_5) > 0:
                # Prepare radar data
                categories = ['Price Score', 'Commute Score', 'Type Score', 'Bedroom Score', 'Outdoor Score']

                fig_radar = go.Figure()

                for idx, (i, prop) in enumerate(top_5.iterrows()):
                    # Calculate individual component scores (simplified)
                    price_score = min(20, 20 * (max_budget - prop['price']) / (max_budget - min_budget)) if prop['price'] else 0
                    commute_score = min(20, 20 * (max_commute - prop['commute_time']) / (max_commute - 30)) if prop['commute_time'] <= max_commute else 0
                    type_score = 15 if 'house' in prop['property_type'].lower() else 8
                    bed_score = min(15, prop['bedrooms'] * 3) if prop['bedrooms'] else 0
                    outdoor_score = 10 if prop['outdoor_space'] != 'None' else 2

                    fig_radar.add_trace(go.Scatterpolar(
                        r=[price_score, commute_score, type_score, bed_score, outdoor_score],
                        theta=categories,
                        fill='toself',
                        name=f"{prop['property_id']} ({prop['total_score']:.1f})"
                    ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 20]
                        )),
                    showlegend=True,
                    title="Top 5 Properties - Score Breakdown"
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        # Data table
        st.subheader("📋 Property Data Table")

        # Sortable columns
        sort_column = st.selectbox(
            "Sort by:", 
            ['total_score', 'price', 'commute_time', 'bedrooms', 'added_date'],
            index=0
        )
        sort_order = st.radio("Order:", ['Descending', 'Ascending'], horizontal=True)

        sorted_df = df.sort_values(
            sort_column, 
            ascending=(sort_order == 'Ascending')
        )

        # Display formatted table
        display_df = sorted_df.copy()
        display_df['price'] = display_df['price'].apply(lambda x: f"£{x:,.0f}")
        display_df['total_score'] = display_df['total_score'].apply(lambda x: f"{x:.1f}")

        st.dataframe(
            display_df[['property_id', 'price', 'property_type', 'bedrooms', 'postcode', 'commute_time', 'total_score']],
            use_container_width=True
        )

# TAB 4: Property Map
with tab4:
    st.header("🗺️ Interactive Property Map")

    if st.session_state.properties_df.empty:
        st.info("📋 No properties added yet. Use the 'Add Property' tab to get started!")
    else:
        df = st.session_state.properties_df

        # Map controls
        col1, col2, col3 = st.columns(3)

        with col1:
            show_reference = st.checkbox("Show Reference Location", value=True)

        with col2:
            show_commute_radius = st.checkbox("Show Commute Radius", value=False)

        with col3:
            color_by = st.selectbox("Color markers by:", ['total_score', 'price', 'commute_time'])

        # Create map
        # Center on London (or reference postcode area)
        center_lat, center_lon = 51.5074, -0.1278  # London coordinates

        # Create folium map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )

        # Add reference location
        if show_reference:
            folium.Marker(
                [center_lat, center_lon],
                popup=f"Reference Location: {reference_postcode}",
                tooltip="Home/Work Location",
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)

        # Add commute radius circle
        if show_commute_radius:
            # Approximate radius in meters (commute time * average speed)
            radius_km = max_commute * 0.5  # Rough estimate: 30km/hour average
            folium.Circle(
                [center_lat, center_lon],
                radius=radius_km * 1000,  # Convert to meters
                popup=f"Max commute: {max_commute} minutes",
                color='blue',
                fill=True,
                fillColor='blue',
                fillOpacity=0.1
            ).add_to(m)

        # Add property markers
        for idx, row in df.iterrows():
            # Generate mock coordinates based on postcode (in real app, use geocoding)
            # This creates scattered points around London
            lat_offset = (hash(row['postcode']) % 200 - 100) / 1000  # -0.1 to +0.1
            lon_offset = (hash(row['postcode'] + 'lon') % 200 - 100) / 1000

            prop_lat = center_lat + lat_offset
            prop_lon = center_lon + lon_offset

            # Color coding
            if color_by == 'total_score':
                if row['total_score'] >= 80:
                    marker_color = 'green'
                elif row['total_score'] >= 60:
                    marker_color = 'orange'  
                else:
                    marker_color = 'red'
                tooltip_text = f"Score: {row['total_score']:.1f}/100"
            elif color_by == 'price':
                if row['price'] <= min_budget * 1.1:
                    marker_color = 'green'
                elif row['price'] <= max_budget * 0.9:
                    marker_color = 'orange'
                else:
                    marker_color = 'red'
                tooltip_text = f"Price: £{row['price']:,.0f}"
            else:  # commute_time
                if row['commute_time'] <= 30:
                    marker_color = 'green'
                elif row['commute_time'] <= 45:
                    marker_color = 'orange'
                else:
                    marker_color = 'red'
                tooltip_text = f"Commute: {row['commute_time']} min"

            # Create popup with property details
            popup_html = f"""
            <div style="width: 200px;">
                <b>{row['property_id']}</b><br>
                <b>Price:</b> £{row['price']:,.0f}<br>
                <b>Type:</b> {row['property_type']}<br>
                <b>Bedrooms:</b> {row['bedrooms']}<br>
                <b>Postcode:</b> {row['postcode']}<br>
                <b>Commute:</b> {row['commute_time']} min<br>
                <b>Score:</b> {row['total_score']:.1f}/100
            </div>
            """

            folium.Marker(
                [prop_lat, prop_lon],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{row['property_id']}: {tooltip_text}",
                icon=folium.Icon(color=marker_color, icon='home')
            ).add_to(m)

        # Display map
        map_data = st_folium(m, width=700, height=500)

        # Map legend
        st.markdown("### 🗺️ Map Legend")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("🔴 **Red Marker:** Home/Work")

        with col2:
            if color_by == 'total_score':
                st.markdown("🟢 **Green:** Score ≥80")
                st.markdown("🟡 **Orange:** Score 60-79")  
                st.markdown("🔴 **Red:** Score <60")
            elif color_by == 'price':
                st.markdown("🟢 **Green:** Under Budget")
                st.markdown("🟡 **Orange:** In Range")
                st.markdown("🔴 **Red:** Over Budget")
            else:
                st.markdown("🟢 **Green:** ≤30 min")
                st.markdown("🟡 **Orange:** 30-45 min")
                st.markdown("🔴 **Red:** >45 min")

        with col3:
            st.markdown("💙 **Blue Circle:** Commute Zone" if show_commute_radius else "")

        with col4:
            st.markdown(f"**Total Properties:** {len(df)}")

# TAB 5: Top 5 Dashboard
with tab5:
    st.header("🏆 Top 5 Properties Dashboard")

    if st.session_state.properties_df.empty:
        st.info("📋 No properties added yet. Use the 'Add Property' tab to get started!")
    else:
        df = st.session_state.properties_df
        top_5 = df.nlargest(5, 'total_score')

        st.markdown("### 🎯 **Top Scoring Properties for Viewing**")
        st.markdown(f"*Based on budget: £{min_budget:,} - £{max_budget:,} | Max commute: {max_commute} min*")

        medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]

        for i, (idx, prop) in enumerate(top_5.iterrows()):
            with st.container():
                # Header with medal and score
                col1, col2, col3 = st.columns([1, 3, 1])

                with col1:
                    st.markdown(f"## {medals[i]}")

                with col2:
                    st.markdown(f"### **{prop['property_id']}**")
                    st.markdown(f"**{prop['property_type']} | {prop['bedrooms']} bed | {prop['postcode']}**")

                with col3:
                    # Score with color
                    score = prop['total_score']
                    if score >= 80:
                        score_color = "🟢"
                    elif score >= 60:
                        score_color = "🟡"
                    else:
                        score_color = "🔴"
                    st.markdown(f"## {score_color} **{score:.1f}/100**")

                # Details columns
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown("**💰 Price**")
                    st.markdown(f"£{prop['price']:,.0f}")
                    budget_status = "✅ Within budget" if min_budget <= prop['price'] <= max_budget else "⚠️ Outside budget"
                    st.markdown(budget_status)

                with col2:
                    st.markdown("**🚇 Commute**")
                    st.markdown(f"{prop['commute_time']} minutes")
                    commute_status = "✅ Acceptable" if prop['commute_time'] <= max_commute else "⚠️ Too long"
                    st.markdown(commute_status)

                with col3:
                    st.markdown("**🏡 Details**")
                    st.markdown(f"Tenure: {prop.get('tenure', 'Unknown')}")
                    st.markdown(f"Outdoor: {prop['outdoor_space']}")

                with col4:
                    st.markdown("**🏫 Schools**")
                    st.markdown(f"Ofsted: {prop['nearest_school_ofsted']}")
                    st.markdown(f"Grammar: {prop['grammar_school_distance']:.1f}km")

                # Action buttons
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if prop.get('url'):
                        st.markdown(f"[🔗 View Listing]({prop['url']})")
                    else:
                        st.markdown("🔗 No URL")

                with col2:
                    if prop.get('agent_phone'):
                        st.markdown(f"📞 {prop['agent_phone']}")
                    else:
                        st.markdown("📞 No phone")

                with col3:
                    if st.button(f"📝 View Details", key=f"details_{idx}"):
                        with st.expander(f"Full Details - {prop['property_id']}", expanded=True):
                            st.json(prop.to_dict())

                with col4:
                    if st.button(f"⭐ Priority View", key=f"priority_{idx}", type="primary" if i < 3 else "secondary"):
                        st.success(f"✅ {prop['property_id']} marked as priority viewing!")

                # Summary description
                if prop.get('summary_description'):
                    with st.expander(f"📄 Property Summary", expanded=False):
                        st.markdown(prop['summary_description'])

                st.markdown("---")

        # Export options
        st.subheader("📥 Export Top 5")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Export to CSV", use_container_width=True):
                csv = top_5.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"top_5_properties_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

        with col2:
            if st.button("📋 Copy Property IDs", use_container_width=True):
                property_ids = ", ".join(top_5['property_id'].tolist())
                st.code(property_ids, language=None)
                st.success("✅ Property IDs ready to copy!")

        with col3:
            if st.button("🗺️ View on Map", use_container_width=True):
                st.info("🗺️ Switch to 'Property Map' tab to view locations")

# Footer
st.markdown("---")
st.markdown("### 💾 Data Management")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Export All Data"):
        if not st.session_state.properties_df.empty:
            csv = st.session_state.properties_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download All Properties CSV",
                data=csv,
                file_name=f"london_properties_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data to export")

with col2:
    uploaded_file = st.file_uploader("📂 Import Properties CSV", type=['csv'])
    if uploaded_file is not None:
        try:
            imported_df = pd.read_csv(uploaded_file)
            st.session_state.properties_df = imported_df
            st.success(f"✅ Imported {len(imported_df)} properties!")
            st.rerun()
        except Exception as e:
            st.error(f"Import failed: {str(e)}")

with col3:
    if st.button("🗑️ Clear All Data"):
        if st.session_state.properties_df.empty:
            st.warning("No data to clear")
        else:
            st.session_state.properties_df = pd.DataFrame()
            st.session_state.search_results = []
            st.success("✅ All data cleared!")
            st.rerun()

# Sidebar status
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Current Status")

    if not st.session_state.properties_df.empty:
        df = st.session_state.properties_df
        st.metric("Properties", len(df))
        st.metric("Avg Score", f"{df['total_score'].mean():.1f}")
        st.metric("Top Score", f"{df['total_score'].max():.1f}")

        # Quick top 3
        top_3 = df.nlargest(3, 'total_score')
        st.markdown("**🏆 Top 3:**")
        for i, (_, prop) in enumerate(top_3.iterrows()):
            medal = ["🥇", "🥈", "🥉"][i]
            st.markdown(f"{medal} {prop['property_id']} ({prop['total_score']:.1f})")
    else:
        st.info("No properties added yet")

    st.markdown("---")
    st.markdown("**📱 Quick Actions:**")
    st.markdown("• Add individual properties in Tab 1")
    st.markdown("• Search areas in Tab 2") 
    st.markdown("• View analytics in Tab 3")
    st.markdown("• Check map in Tab 4")
    st.markdown("• Review top 5 in Tab 5")
