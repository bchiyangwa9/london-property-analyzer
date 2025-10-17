"""
London Property Search Analyzer
A comprehensive property search and analysis tool for London real estate market
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import time
import io
from typing import Dict, List, Optional, Tuple
import warnings

# Import custom utilities
from utils.automation_engine import AutomationEngine
from utils.api_simulator import APISimulator
from utils.excel_handler import ExcelHandler
from utils.validators import DataValidator, SearchValidator

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="London Property Analyzer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }

    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }

    .success-alert {
        background-color: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }

    .warning-alert {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }

    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class PropertyAnalyzer:
    """Main application class for property analysis"""

    def __init__(self):
        self.automation_engine = AutomationEngine()
        self.api_simulator = APISimulator()
        self.excel_handler = ExcelHandler()
        self.data_validator = DataValidator()
        self.search_validator = SearchValidator()

        # Initialize session state
        if 'search_results' not in st.session_state:
            st.session_state.search_results = None
        if 'processed_data' not in st.session_state:
            st.session_state.processed_data = None
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []

    def render_header(self):
        """Render application header"""
        st.markdown('<h1 class="main-header">🏠 London Property Search Analyzer</h1>', 
                   unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
            <h4>🎯 Comprehensive Property Analysis Platform</h4>
            <p>Search, analyze, and visualize London property market data with advanced filtering, 
            market insights, and automated reporting capabilities.</p>
        </div>
        """, unsafe_allow_html=True)

    def render_sidebar(self):
        """Render sidebar with search options"""
        st.sidebar.header("🔍 Search Configuration")

        # Property type selection
        property_types = ['All', 'Flat', 'House', 'Studio', 'Penthouse', 'Maisonette']
        selected_type = st.sidebar.selectbox("Property Type", property_types)

        # Price range
        st.sidebar.subheader("💰 Price Range")
        min_price = st.sidebar.number_input("Minimum Price (£)", 
                                          min_value=0, max_value=5000000, 
                                          value=200000, step=50000)
        max_price = st.sidebar.number_input("Maximum Price (£)", 
                                          min_value=min_price, max_value=10000000, 
                                          value=800000, step=50000)

        # Bedrooms
        bedrooms = st.sidebar.slider("Bedrooms", 0, 5, (1, 3))

        # Location
        st.sidebar.subheader("📍 Location")
        boroughs = ['All', 'Westminster', 'Kensington and Chelsea', 'Camden', 
                   'Islington', 'Tower Hamlets', 'Hackney', 'Southwark', 
                   'Lambeth', 'Wandsworth', 'Hammersmith and Fulham']
        selected_borough = st.sidebar.selectbox("Borough", boroughs)

        # Additional filters
        st.sidebar.subheader("🏗️ Additional Filters")
        new_build = st.sidebar.checkbox("New Build Only")
        garden = st.sidebar.checkbox("Garden Required")
        parking = st.sidebar.checkbox("Parking Required")

        # Search button
        search_params = {
            'property_type': selected_type,
            'min_price': min_price,
            'max_price': max_price,
            'min_bedrooms': bedrooms[0],
            'max_bedrooms': bedrooms[1],
            'borough': selected_borough,
            'new_build': new_build,
            'garden': garden,
            'parking': parking
        }

        if st.sidebar.button("🔍 Search Properties", type="primary"):
            return search_params

        return None

    def perform_search(self, search_params: Dict):
        """Perform property search with given parameters"""
        with st.spinner("🔍 Searching properties..."):
            # Validate search parameters
            validation_result = self.search_validator.validate_search_params(search_params)

            if not validation_result['valid']:
                st.error(f"Invalid search parameters: {validation_result['message']}")
                return

            # Simulate API call with progress
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i in range(100):
                progress_bar.progress(i + 1)
                if i < 30:
                    status_text.text("Connecting to property APIs...")
                elif i < 60:
                    status_text.text("Filtering properties...")
                elif i < 90:
                    status_text.text("Processing results...")
                else:
                    status_text.text("Finalizing data...")
                time.sleep(0.02)

            # Get search results
            results = self.api_simulator.search_properties(search_params)

            if results and len(results) > 0:
                st.session_state.search_results = results
                st.session_state.search_history.append({
                    'timestamp': datetime.now(),
                    'params': search_params,
                    'results_count': len(results)
                })

                st.success(f"✅ Found {len(results)} properties matching your criteria!")

            else:
                st.warning("⚠️ No properties found matching your search criteria. Try adjusting your filters.")

    def render_results_overview(self):
        """Render search results overview"""
        if st.session_state.search_results is None:
            return

        df = pd.DataFrame(st.session_state.search_results)

        st.subheader("📊 Search Results Overview")

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Properties", len(df))

        with col2:
            avg_price = df['price'].mean()
            st.metric("Average Price", f"£{avg_price:,.0f}")

        with col3:
            median_price = df['price'].median()
            st.metric("Median Price", f"£{median_price:,.0f}")

        with col4:
            avg_sqft = df['square_feet'].mean() if 'square_feet' in df.columns else 0
            st.metric("Avg Size", f"{avg_sqft:.0f} sq ft")

    def render_data_table(self):
        """Render interactive data table"""
        if st.session_state.search_results is None:
            return

        df = pd.DataFrame(st.session_state.search_results)

        st.subheader("📋 Property Listings")

        # Add filters above table
        col1, col2, col3 = st.columns(3)

        with col1:
            property_filter = st.selectbox(
                "Filter by Type", 
                ['All'] + list(df['property_type'].unique())
            )

        with col2:
            borough_filter = st.selectbox(
                "Filter by Borough", 
                ['All'] + list(df['borough'].unique())
            )

        with col3:
            sort_by = st.selectbox(
                "Sort by", 
                ['price', 'bedrooms', 'square_feet', 'price_per_sqft']
            )

        # Apply filters
        filtered_df = df.copy()

        if property_filter != 'All':
            filtered_df = filtered_df[filtered_df['property_type'] == property_filter]

        if borough_filter != 'All':
            filtered_df = filtered_df[filtered_df['borough'] == borough_filter]

        # Sort data
        filtered_df = filtered_df.sort_values(sort_by, ascending=False)

        # Format display columns
        display_df = filtered_df.copy()
        display_df['price'] = display_df['price'].apply(lambda x: f"£{x:,.0f}")
        display_df['price_per_sqft'] = display_df['price_per_sqft'].apply(lambda x: f"£{x:.0f}")

        st.dataframe(
            display_df[['address', 'property_type', 'bedrooms', 'price', 
                       'square_feet', 'price_per_sqft', 'borough']],
            use_container_width=True
        )

    def render_visualizations(self):
        """Render data visualizations"""
        if st.session_state.search_results is None:
            return

        df = pd.DataFrame(st.session_state.search_results)

        st.subheader("📈 Data Visualizations")

        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["Price Analysis", "Property Types", "Borough Analysis", "Map View"])

        with tab1:
            self.render_price_analysis(df)

        with tab2:
            self.render_property_type_analysis(df)

        with tab3:
            self.render_borough_analysis(df)

        with tab4:
            self.render_map_visualization(df)

    def render_price_analysis(self, df: pd.DataFrame):
        """Render price analysis charts"""
        col1, col2 = st.columns(2)

        with col1:
            # Price distribution histogram
            fig = px.histogram(
                df, x='price', nbins=20,
                title='Property Price Distribution',
                labels={'price': 'Price (£)', 'count': 'Number of Properties'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Price vs Square Feet scatter
            fig = px.scatter(
                df, x='square_feet', y='price', 
                color='property_type', size='bedrooms',
                title='Price vs Size Analysis',
                labels={'square_feet': 'Square Feet', 'price': 'Price (£)'}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Price per square foot by property type
        price_per_sqft_by_type = df.groupby('property_type')['price_per_sqft'].mean().reset_index()
        fig = px.bar(
            price_per_sqft_by_type, x='property_type', y='price_per_sqft',
            title='Average Price per Square Foot by Property Type',
            labels={'price_per_sqft': 'Price per Sq Ft (£)', 'property_type': 'Property Type'}
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_property_type_analysis(self, df: pd.DataFrame):
        """Render property type analysis"""
        col1, col2 = st.columns(2)

        with col1:
            # Property type distribution pie chart
            type_counts = df['property_type'].value_counts()
            fig = px.pie(
                values=type_counts.values, names=type_counts.index,
                title='Property Type Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Bedrooms distribution
            bedroom_counts = df['bedrooms'].value_counts().sort_index()
            fig = px.bar(
                x=bedroom_counts.index, y=bedroom_counts.values,
                title='Distribution by Number of Bedrooms',
                labels={'x': 'Bedrooms', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Box plot: Price distribution by property type
        fig = px.box(
            df, x='property_type', y='price',
            title='Price Distribution by Property Type',
            labels={'price': 'Price (£)', 'property_type': 'Property Type'}
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    def render_borough_analysis(self, df: pd.DataFrame):
        """Render borough analysis"""
        col1, col2 = st.columns(2)

        with col1:
            # Average price by borough
            borough_prices = df.groupby('borough')['price'].mean().sort_values(ascending=False)
            fig = px.bar(
                x=borough_prices.values, y=borough_prices.index,
                orientation='h',
                title='Average Property Price by Borough',
                labels={'x': 'Average Price (£)', 'y': 'Borough'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Property count by borough
            borough_counts = df['borough'].value_counts()
            fig = px.bar(
                x=borough_counts.index, y=borough_counts.values,
                title='Number of Properties by Borough',
                labels={'x': 'Borough', 'y': 'Count'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    def render_map_visualization(self, df: pd.DataFrame):
        """Render map visualization"""
        st.subheader("🗺️ Property Locations")

        # Create a folium map centered on London
        london_center = [51.5074, -0.1278]
        m = folium.Map(location=london_center, zoom_start=11)

        # Add property markers
        for idx, row in df.iterrows():
            # Generate random coordinates within London bounds for demonstration
            lat = np.random.uniform(51.4, 51.6)
            lon = np.random.uniform(-0.3, 0.1)

            # Create popup text
            popup_text = f"""
            <b>{row['address']}</b><br>
            Type: {row['property_type']}<br>
            Bedrooms: {row['bedrooms']}<br>
            Price: £{row['price']:,.0f}<br>
            Size: {row['square_feet']} sq ft<br>
            Borough: {row['borough']}
            """

            # Color code by price range
            if row['price'] < 400000:
                color = 'green'
            elif row['price'] < 700000:
                color = 'orange'
            else:
                color = 'red'

            folium.Marker(
                [lat, lon],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color)
            ).add_to(m)

        # Display map
        st_folium(m, width=700, height=500)

        # Legend
        st.markdown("""
        **Map Legend:**
        - 🟢 Green: Under £400k
        - 🟠 Orange: £400k - £700k  
        - 🔴 Red: Over £700k
        """)

    def render_export_section(self):
        """Render data export section"""
        if st.session_state.search_results is None:
            return

        st.subheader("📥 Export Results")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Export to Excel"):
                self.export_to_excel()

        with col2:
            if st.button("📄 Generate Report"):
                self.generate_report()

        with col3:
            if st.button("📧 Schedule Email"):
                self.schedule_email_report()

    def export_to_excel(self):
        """Export results to Excel"""
        if st.session_state.search_results is None:
            st.error("No data to export")
            return

        with st.spinner("📊 Generating Excel export..."):
            df = pd.DataFrame(st.session_state.search_results)

            # Create Excel file in memory
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name='Properties', index=False)

                # Summary statistics sheet
                summary_data = {
                    'Metric': ['Total Properties', 'Average Price', 'Median Price', 
                              'Min Price', 'Max Price', 'Average Size (sq ft)'],
                    'Value': [
                        len(df),
                        f"£{df['price'].mean():,.0f}",
                        f"£{df['price'].median():,.0f}",
                        f"£{df['price'].min():,.0f}",
                        f"£{df['price'].max():,.0f}",
                        f"{df['square_feet'].mean():.0f}"
                    ]
                }

                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

            output.seek(0)

            st.download_button(
                label="📥 Download Excel File",
                data=output.getvalue(),
                file_name=f"london_properties_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("✅ Excel file ready for download!")

    def generate_report(self):
        """Generate comprehensive report"""
        if st.session_state.search_results is None:
            st.error("No data to generate report")
            return

        with st.spinner("📄 Generating comprehensive report..."):
            df = pd.DataFrame(st.session_state.search_results)

            # Generate report content
            report_content = f"""
# London Property Search Report
*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*

## Executive Summary
- **Total Properties Found:** {len(df)}
- **Average Price:** £{df['price'].mean():,.0f}
- **Price Range:** £{df['price'].min():,.0f} - £{df['price'].max():,.0f}
- **Most Common Property Type:** {df['property_type'].mode().iloc[0]}
- **Average Size:** {df['square_feet'].mean():.0f} square feet

## Market Analysis

### Price Distribution
- **Median Price:** £{df['price'].median():,.0f}
- **Standard Deviation:** £{df['price'].std():,.0f}
- **Properties Under £500k:** {len(df[df['price'] < 500000])} ({len(df[df['price'] < 500000])/len(df)*100:.1f}%)
- **Properties Over £1M:** {len(df[df['price'] > 1000000])} ({len(df[df['price'] > 1000000])/len(df)*100:.1f}%)

### Borough Breakdown
{df.groupby('borough').agg({'price': ['count', 'mean']}).round(0).to_string()}

### Property Type Analysis  
{df.groupby('property_type').agg({'price': ['count', 'mean'], 'square_feet': 'mean'}).round(0).to_string()}

## Recommendations
Based on the current search results:

1. **Best Value Areas:** {df.groupby('borough')['price_per_sqft'].mean().sort_values().index[0]}
2. **Highest Demand:** {df['borough'].value_counts().index[0]} (most listings)
3. **Investment Potential:** Properties in the £{df['price'].quantile(0.25):,.0f} - £{df['price'].quantile(0.75):,.0f} range

---
*Report generated by London Property Search Analyzer*
            """

            st.download_button(
                label="📥 Download Report (Markdown)",
                data=report_content,
                file_name=f"property_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )

            st.success("✅ Report generated successfully!")

    def schedule_email_report(self):
        """Schedule email report (simulation)"""
        st.info("📧 Email scheduling feature - Demo Mode")

        email_form = st.form("email_schedule")

        with email_form:
            email = st.text_input("Email Address")
            frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
            time_slot = st.selectbox("Time", ["Morning (9 AM)", "Afternoon (1 PM)", "Evening (6 PM)"])

            submitted = st.form_submit_button("Schedule Reports")

            if submitted and email:
                st.success(f"✅ Scheduled {frequency.lower()} reports to {email} at {time_slot.lower()}!")
                st.info("📧 In production, this would integrate with email services like SendGrid or AWS SES")

    def render_search_history(self):
        """Render search history"""
        if not st.session_state.search_history:
            return

        with st.expander("📚 Search History", expanded=False):
            for i, search in enumerate(reversed(st.session_state.search_history[-5:])):  # Last 5 searches
                st.write(f"**Search {len(st.session_state.search_history) - i}** - {search['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                st.write(f"Found {search['results_count']} properties")

                # Show search parameters
                params = search['params']
                param_text = f"Type: {params['property_type']}, Price: £{params['min_price']:,} - £{params['max_price']:,}, Bedrooms: {params['min_bedrooms']}-{params['max_bedrooms']}"
                if params['borough'] != 'All':
                    param_text += f", Borough: {params['borough']}"

                st.caption(param_text)
                st.divider()

    def run(self):
        """Main application execution"""
        self.render_header()

        # Sidebar for search
        search_params = self.render_sidebar()

        # Perform search if parameters provided
        if search_params:
            self.perform_search(search_params)

        # Main content area
        if st.session_state.search_results:
            self.render_results_overview()
            self.render_data_table()
            self.render_visualizations()
            self.render_export_section()

        else:
            # Welcome screen
            st.markdown("""
            <div class="info-box">
                <h3>🎯 Getting Started</h3>
                <p>Use the sidebar to configure your property search parameters:</p>
                <ul>
                    <li><b>Property Type:</b> Filter by flat, house, studio, etc.</li>
                    <li><b>Price Range:</b> Set your budget limits</li>
                    <li><b>Bedrooms:</b> Specify bedroom requirements</li>
                    <li><b>Location:</b> Choose specific boroughs</li>
                    <li><b>Additional Filters:</b> New build, garden, parking options</li>
                </ul>
                <p>Click <b>'Search Properties'</b> to begin your analysis!</p>
            </div>
            """, unsafe_allow_html=True)

            # Sample data demonstration
            st.subheader("📊 Sample Market Insights")

            # Create sample charts for demo
            sample_data = {
                'Borough': ['Westminster', 'Kensington', 'Camden', 'Islington', 'Tower Hamlets'],
                'Avg_Price': [1200000, 1100000, 800000, 700000, 600000],
                'Property_Count': [45, 38, 62, 58, 71]
            }

            sample_df = pd.DataFrame(sample_data)

            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(sample_df, x='Borough', y='Avg_Price',
                           title='Average Property Prices by Borough (Sample Data)')
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.pie(sample_df, values='Property_Count', names='Borough',
                           title='Property Distribution (Sample Data)')
                st.plotly_chart(fig, use_container_width=True)

        # Search history in sidebar
        with st.sidebar:
            self.render_search_history()

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>🏠 London Property Search Analyzer | Built with Streamlit & Python</p>
            <p><small>Data sourced from multiple property APIs | Last updated: {}</small></p>
        </div>
        """.format(datetime.now().strftime('%B %d, %Y')), unsafe_allow_html=True)


if __name__ == "__main__":
    app = PropertyAnalyzer()
    app.run()
