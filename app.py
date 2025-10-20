
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import uuid
import re

# Configure Streamlit page
st.set_page_config(
    page_title="🏠 Property Analysis Tool", 
    page_icon="🏠", 
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .required-field {
        color: red;
        font-weight: bold;
    }
    .auto-field {
        background-color: #e8f4f8;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 0.8em;
    }
    .score-high { color: #28a745; font-weight: bold; }
    .score-medium { color: #fd7e14; font-weight: bold; }
    .score-low { color: #dc3545; font-weight: bold; }
    .top5-table { font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'properties' not in st.session_state:
    st.session_state.properties = []

if 'settings' not in st.session_state:
    st.session_state.settings = {
        'reference_postcode': 'SE1 9SP',
        'budget_min': 300000,
        'budget_max': 420000,
        'min_bedrooms': 3,
        'max_commute_time': 60
    }

# Helper functions for scoring
def calculate_price_score(price):
    """Calculate price score based on criteria"""
    if price <= 320000:
        return 20
    elif price <= 350000:
        return 15
    elif price <= 380000:
        return 10
    elif price <= 420000:
        return 5
    else:
        return 0

def calculate_commute_score(commute_time):
    """Calculate commute score based on criteria"""
    if commute_time <= 30:
        return 20
    elif commute_time <= 40:
        return 15
    elif commute_time <= 50:
        return 10
    elif commute_time <= 60:
        return 5
    else:
        return 0

def calculate_property_type_score(property_type):
    """Calculate property type score based on criteria"""
    scores = {
        'Detached': 15,
        'Semi-Detached': 12,
        'Terraced': 10,
        'Maisonette': 8,
        'Flat/Apartment': 5
    }
    return scores.get(property_type, 0)

def calculate_bedroom_score(bedrooms):
    """Calculate bedroom score based on criteria"""
    if bedrooms >= 4:
        return 15
    elif bedrooms == 3:
        return 12
    elif bedrooms == 2:
        return 8
    else:
        return 0

def calculate_outdoor_space_score(outdoor_space):
    """Calculate outdoor space score based on criteria"""
    scores = {
        'Large Garden': 10,
        'Medium Garden': 8,
        'Small Garden': 6,
        'Balcony/Patio': 4,
        'None': 0
    }
    return scores.get(outdoor_space, 0)

def calculate_school_score(ofsted_rating):
    """Calculate school score based on Ofsted rating"""
    if 'Outstanding' in str(ofsted_rating):
        return 10
    elif 'Good' in str(ofsted_rating):
        return 7
    elif 'Requires Improvement' in str(ofsted_rating):
        return 4
    elif 'Inadequate' in str(ofsted_rating):
        return 2
    else:
        return 0

def calculate_grammar_bonus(grammar_school_info):
    """Calculate grammar school bonus"""
    if 'Y -' in str(grammar_school_info):
        return 10
    else:
        return 0

def calculate_total_score(property_data):
    """Calculate total score for a property"""
    price_score = calculate_price_score(property_data['asking_price'])
    commute_score = calculate_commute_score(property_data['commute_time'])
    type_score = calculate_property_type_score(property_data['property_type'])
    bedroom_score = calculate_bedroom_score(property_data['bedrooms'])
    outdoor_score = calculate_outdoor_space_score(property_data['outdoor_space'])
    school_score = calculate_school_score(property_data['school_ofsted'])
    grammar_bonus = calculate_grammar_bonus(property_data['grammar_school'])

    return {
        'price_score': price_score,
        'commute_score': commute_score,
        'type_score': type_score,
        'bedroom_score': bedroom_score,
        'outdoor_score': outdoor_score,
        'school_score': school_score,
        'grammar_bonus': grammar_bonus,
        'total_score': price_score + commute_score + type_score + bedroom_score + outdoor_score + school_score + grammar_bonus
    }

def format_currency(amount):
    """Format currency with proper commas"""
    return f"£{amount:,.0f}"

def get_score_color_class(score):
    """Get CSS class for score color coding"""
    if score >= 70:
        return "score-high"
    elif score >= 50:
        return "score-medium"
    else:
        return "score-low"

# Mock API functions (simulating automation_engine.py functionality)
def simulate_commute_calculation(postcode, reference_postcode):
    """Simulate commute time calculation"""
    # Mock calculation based on distance estimation
    base_times = {
        'SE1': 15, 'SW1': 20, 'E1': 25, 'N1': 30, 'W1': 18,
        'DA': 45, 'BR': 40, 'CR': 35, 'SM': 38, 'KT': 42,
        'TW': 50, 'UB': 55, 'HA': 48, 'WD': 52, 'EN': 45
    }
    area_code = postcode[:2] if len(postcode) >= 2 else 'XX'
    return base_times.get(area_code, 35) + np.random.randint(-5, 10)

def simulate_distance_to_station(postcode):
    """Simulate distance to nearest station"""
    distance = round(np.random.uniform(0.1, 2.0), 2)
    stations = ['Station', 'Railway Station', 'Underground', 'Overground']
    station_name = f"{postcode.split()[0]} {np.random.choice(stations)}"
    return f"{distance} miles ({station_name})"

def simulate_school_lookup(postcode):
    """Simulate school lookup"""
    schools = [
        "Burnt Oak Junior | Outstanding | 0.2mi",
        "St. Mary's Primary | Good | 0.3mi", 
        "Park View School | Outstanding | 0.4mi",
        "Riverside Primary | Good | 0.5mi",
        "Oak Tree Academy | Requires Improvement | 0.6mi"
    ]
    return np.random.choice(schools)

def simulate_grammar_school_lookup(postcode):
    """Simulate grammar school lookup"""
    grammar_options = [
        "Y - Chislehurst & Sidcup Grammar, 1.5mi",
        "Y - Dartford Grammar School, 2.1mi", 
        "Y - Bexley Grammar School, 1.8mi",
        "N - No grammar school within catchment"
    ]
    return np.random.choice(grammar_options)

def generate_property_summary(property_data):
    """Generate automated property summary"""
    return f"{property_data['bedrooms']}-bed {property_data['property_type'].lower()}, {property_data['tenure'].lower()}, {property_data['outdoor_space'].lower()}, {property_data['commute_time']}min commute"

# Sidebar - Settings/Configuration
with st.sidebar:
    st.header("🔧 Search Configuration")

    with st.expander("📍 Reference Settings", expanded=True):
        st.session_state.settings['reference_postcode'] = st.text_input(
            "Reference Postcode (Commute From)",
            value=st.session_state.settings['reference_postcode'],
            help="The postcode you'll be commuting from (e.g., your office)"
        )

    with st.expander("💰 Budget Settings", expanded=True):
        budget_range = st.slider(
            "Budget Range (£)",
            min_value=250000,
            max_value=500000,
            value=(st.session_state.settings['budget_min'], st.session_state.settings['budget_max']),
            step=10000,
            format="£%d"
        )
        st.session_state.settings['budget_min'] = budget_range[0]
        st.session_state.settings['budget_max'] = budget_range[1]

    with st.expander("🏠 Property Requirements", expanded=True):
        st.session_state.settings['min_bedrooms'] = st.selectbox(
            "Minimum Bedrooms",
            options=[1, 2, 3, 4, 5],
            index=2  # Default to 3 bedrooms
        )

        st.session_state.settings['max_commute_time'] = st.slider(
            "Maximum Commute Time (minutes)",
            min_value=15,
            max_value=90,
            value=st.session_state.settings['max_commute_time'],
            step=5
        )

    # Display current criteria
    st.info(f"""
    **Current Search Criteria:**
    - Budget: {format_currency(st.session_state.settings['budget_min'])} - {format_currency(st.session_state.settings['budget_max'])}
    - Min Bedrooms: {st.session_state.settings['min_bedrooms']}
    - Max Commute: {st.session_state.settings['max_commute_time']} mins
    - From: {st.session_state.settings['reference_postcode']}
    """)

# Main content area
st.title("🏠 Property Analysis Tool")
st.markdown("**Comprehensive property evaluation with automated scoring**")

# Create tabs for different sections
tab1, tab2 = st.tabs(["📝 Property Entry", "🏆 Top 5 Dashboard"])

with tab1:
    st.header("Property Data Entry")

    # Property entry form
    with st.form("property_form", clear_on_submit=False):
        # Basic Property Info Section
        with st.expander("🏠 Basic Property Information", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                property_url = st.text_input(
                    "🔗 Property URL",
                    placeholder="https://www.rightmove.co.uk/properties/...",
                    help="Optional: Link to the property listing"
                )

                agent_name = st.text_input(
                    "🏢 Agent Name", 
                    placeholder="e.g., Barnard Marcus"
                )

            with col2:
                agent_contact = st.text_input(
                    "📞 Agent Contact",
                    placeholder="e.g., 020 8300 9393"
                )

        # Pricing & Tenure Section
        with st.expander("💷 Pricing & Tenure Details", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                asking_price = st.number_input(
                    "💷 Asking Price (£) *", 
                    min_value=0,
                    max_value=1000000,
                    step=1000,
                    format="%d",
                    help="Required field"
                )
                if asking_price == 0:
                    st.markdown('<span class="required-field">* Required field</span>', unsafe_allow_html=True)

            with col2:
                price_change = st.selectbox(
                    "📉 Price Change",
                    options=["None", "Reduced", "Increased"],
                    help="Has the price changed recently?"
                )

            with col3:
                property_type = st.selectbox(
                    "🏠 Property Type *",
                    options=["", "Detached", "Semi-Detached", "Terraced", "Maisonette", "Flat/Apartment"],
                    help="Required field"
                )
                if not property_type:
                    st.markdown('<span class="required-field">* Required field</span>', unsafe_allow_html=True)

        # Property Details Section
        with st.expander("🛏️ Property Details", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                bedrooms = st.number_input(
                    "🛏️ Bedrooms *",
                    min_value=1,
                    max_value=10,
                    step=1,
                    help="Required field"
                )

            with col2:
                postcode = st.text_input(
                    "📍 Postcode/Area *",
                    placeholder="e.g., DA15 9DE",
                    help="Required field"
                ).upper()
                if not postcode:
                    st.markdown('<span class="required-field">* Required field</span>', unsafe_allow_html=True)

            with col3:
                tenure = st.selectbox(
                    "📜 Tenure *",
                    options=["", "Freehold", "Share of Freehold", "Leasehold"],
                    help="Required field"
                )
                if not tenure:
                    st.markdown('<span class="required-field">* Required field</span>', unsafe_allow_html=True)

        # Conditional lease years field
        lease_years = None
        if tenure == "Leasehold":
            lease_years = st.number_input(
                "⏳ Lease Years Remaining",
                min_value=1,
                max_value=999,
                step=1,
                help="Required for leasehold properties"
            )

        outdoor_space = st.selectbox(
            "🌳 Outdoor Space",
            options=["None", "Balcony/Patio", "Small Garden", "Medium Garden", "Large Garden"]
        )

        # Auto-filled sections
        with st.expander("🚇 Location & Transport (Auto-filled)", expanded=False):
            st.markdown('<span class="auto-field">🤖 Auto-filled</span>', unsafe_allow_html=True)

            if postcode and st.session_state.settings['reference_postcode']:
                with st.spinner("Calculating commute time..."):
                    commute_time = simulate_commute_calculation(postcode, st.session_state.settings['reference_postcode'])
                    distance_to_station = simulate_distance_to_station(postcode)

                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("🚇 Commute Time D2D", value=f"{commute_time} minutes", disabled=True)
                with col2:
                    st.text_input("🚉 Distance to Station", value=distance_to_station, disabled=True)
            else:
                commute_time = 0
                distance_to_station = "N/A"
                st.info("Enter postcode to auto-calculate transport details")

        with st.expander("🏫 Schools & Education (Auto-filled)", expanded=False):
            st.markdown('<span class="auto-field">🤖 Auto-filled</span>', unsafe_allow_html=True)

            if postcode:
                with st.spinner("Looking up school information..."):
                    school_ofsted = simulate_school_lookup(postcode)
                    grammar_school = simulate_grammar_school_lookup(postcode)

                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("🏫 Nearest School Ofsted", value=school_ofsted, disabled=True)
                with col2:
                    st.text_input("🎓 Grammar School Proximity", value=grammar_school, disabled=True)
            else:
                school_ofsted = "N/A"
                grammar_school = "N/A"
                st.info("Enter postcode to auto-lookup school information")

        # Auto-generated summary
        if all([property_type, bedrooms, tenure, outdoor_space, postcode]):
            property_summary = generate_property_summary({
                'bedrooms': bedrooms,
                'property_type': property_type,
                'tenure': tenure,
                'outdoor_space': outdoor_space,
                'commute_time': commute_time if postcode else 0
            })
            st.text_area("📝 Summary Description (Auto-generated)", value=property_summary, disabled=True)

        # Real-time scoring display
        if asking_price > 0 and property_type and postcode:
            st.markdown("---")
            st.subheader("🎯 Real-time Property Score")

            property_data = {
                'asking_price': asking_price,
                'commute_time': commute_time if postcode else 0,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'outdoor_space': outdoor_space,
                'school_ofsted': school_ofsted if postcode else "N/A",
                'grammar_school': grammar_school if postcode else "N/A"
            }

            scores = calculate_total_score(property_data)

            # Score breakdown in columns
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("💷 Price Score", f"{scores['price_score']}/20")
                st.metric("🛏️ Bedroom Score", f"{scores['bedroom_score']}/15")

            with col2:
                st.metric("🚇 Commute Score", f"{scores['commute_score']}/20")
                st.metric("🌿 Outdoor Score", f"{scores['outdoor_score']}/10")

            with col3:
                st.metric("🏠 Property Type", f"{scores['type_score']}/15")
                st.metric("🏫 School Score", f"{scores['school_score']}/10")

            with col4:
                st.metric("🎓 Grammar Bonus", f"{scores['grammar_bonus']}/10")

                # Total score with color coding
                total_score = scores['total_score']
                score_class = get_score_color_class(total_score)
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🏆 TOTAL SCORE</h3>
                    <h2 class="{score_class}">{total_score}/100</h2>
                </div>
                """, unsafe_allow_html=True)

        # Form submission
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            submitted = st.form_submit_button(
                "➕ Add Property", 
                type="primary",
                use_container_width=True
            )

        # Validation and submission logic
        if submitted:
            # Validate required fields
            required_fields = {
                'Asking Price': asking_price > 0,
                'Property Type': bool(property_type),
                'Bedrooms': bedrooms > 0,
                'Postcode': bool(postcode),
                'Tenure': bool(tenure)
            }

            missing_fields = [field for field, valid in required_fields.items() if not valid]

            if missing_fields:
                st.error(f"Please complete the following required fields: {', '.join(missing_fields)}")
            else:
                # Create property record
                property_id = f"{len(st.session_state.properties) + 1:02d}"

                property_record = {
                    'property_id': property_id,
                    'property_url': property_url,
                    'agent_name': agent_name,
                    'agent_contact': agent_contact,
                    'asking_price': asking_price,
                    'price_change': price_change,
                    'property_type': property_type,
                    'bedrooms': bedrooms,
                    'postcode': postcode,
                    'tenure': tenure,
                    'lease_years': lease_years,
                    'outdoor_space': outdoor_space,
                    'commute_time': commute_time,
                    'distance_to_station': distance_to_station,
                    'school_ofsted': school_ofsted,
                    'grammar_school': grammar_school,
                    'summary_description': property_summary,
                    'timestamp': datetime.now().isoformat(),
                    **scores
                }

                st.session_state.properties.append(property_record)
                st.success(f"✅ Property {property_id} added successfully! Total Score: {scores['total_score']}/100")
                st.rerun()

with tab2:
    st.header("🏆 Top 5 Properties Dashboard")

    if st.session_state.properties:
        # Sort properties by total score
        sorted_properties = sorted(
            st.session_state.properties, 
            key=lambda x: x['total_score'], 
            reverse=True
        )[:5]

        # Create top 5 table
        top5_data = []
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

        for i, prop in enumerate(sorted_properties):
            top5_data.append({
                'Rank': f"{medals[i]} {i+1}",
                'Property ID': prop['property_id'],
                'Address/Area': prop['postcode'],
                'Price': format_currency(prop['asking_price']),
                'Beds': prop['bedrooms'],
                'Commute': f"{prop['commute_time']}min",
                'Total Score': f"{prop['total_score']}/100",
                'Summary': prop['summary_description'][:50] + "..." if len(prop['summary_description']) > 50 else prop['summary_description']
            })

        # Display as styled dataframe
        df_top5 = pd.DataFrame(top5_data)

        # Color-code the scores
        def highlight_scores(val):
            if '/100' in str(val):
                score = int(val.split('/')[0])
                if score >= 70:
                    return 'background-color: #d4edda; color: #155724'
                elif score >= 50:
                    return 'background-color: #fff3cd; color: #856404'
                else:
                    return 'background-color: #f8d7da; color: #721c24'
            return ''

        styled_df = df_top5.style.applymap(highlight_scores, subset=['Total Score'])

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )

        # Export functionality
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            # Download individual property
            selected_property = st.selectbox(
                "Select Property to Download",
                options=[f"Property {p['property_id']} - {format_currency(p['asking_price'])}" for p in sorted_properties],
                help="Choose a property to download as Excel"
            )

        with col2:
            if st.button("📄 Download Selected Property", use_container_width=True):
                # Create Excel for selected property
                selected_idx = int(selected_property.split()[1]) - 1
                prop_data = [sorted_properties[selected_idx]]

                df_export = pd.DataFrame(prop_data)

                # Create Excel file in memory
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_export.to_excel(writer, sheet_name='Property Data', index=False)

                st.download_button(
                    label="⬇️ Download Excel File",
                    data=output.getvalue(),
                    file_name=f"property_{sorted_properties[selected_idx]['property_id']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        with col3:
            if st.button("📊 Download All Properties", use_container_width=True):
                # Create comprehensive Excel with multiple sheets
                output = io.BytesIO()

                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # All properties sheet
                    df_all = pd.DataFrame(st.session_state.properties)
                    df_all.to_excel(writer, sheet_name='All Properties', index=False)

                    # Top 5 dashboard sheet
                    df_top5_export = pd.DataFrame(top5_data)
                    df_top5_export.to_excel(writer, sheet_name='Top 5 Dashboard', index=False)

                    # Search criteria sheet
                    criteria_data = [{
                        'Setting': 'Reference Postcode',
                        'Value': st.session_state.settings['reference_postcode']
                    }, {
                        'Setting': 'Budget Range',
                        'Value': f"{format_currency(st.session_state.settings['budget_min'])} - {format_currency(st.session_state.settings['budget_max'])}"
                    }, {
                        'Setting': 'Minimum Bedrooms',
                        'Value': st.session_state.settings['min_bedrooms']
                    }, {
                        'Setting': 'Maximum Commute Time',
                        'Value': f"{st.session_state.settings['max_commute_time']} minutes"
                    }]

                    df_criteria = pd.DataFrame(criteria_data)
                    df_criteria.to_excel(writer, sheet_name='Search Criteria', index=False)

                st.download_button(
                    label="⬇️ Download Complete Analysis",
                    data=output.getvalue(),
                    file_name=f"property_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # Statistics
        if len(st.session_state.properties) > 1:
            st.markdown("---")
            st.subheader("📈 Analysis Statistics")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                avg_score = np.mean([p['total_score'] for p in st.session_state.properties])
                st.metric("Average Score", f"{avg_score:.1f}/100")

            with col2:
                avg_price = np.mean([p['asking_price'] for p in st.session_state.properties])
                st.metric("Average Price", format_currency(avg_price))

            with col3:
                avg_commute = np.mean([p['commute_time'] for p in st.session_state.properties])
                st.metric("Average Commute", f"{avg_commute:.0f} min")

            with col4:
                properties_in_budget = len([
                    p for p in st.session_state.properties 
                    if st.session_state.settings['budget_min'] <= p['asking_price'] <= st.session_state.settings['budget_max']
                ])
                st.metric("In Budget", f"{properties_in_budget}/{len(st.session_state.properties)}")

    else:
        st.info("No properties added yet. Use the Property Entry tab to add your first property!")

        # Show example of what the dashboard will look like
        st.markdown("### 🎯 Dashboard Preview")
        st.markdown("Once you add properties, you'll see:")
        st.markdown("""
        - 🏆 **Top 5 ranked properties** with medals and scores
        - 📊 **Detailed comparison table** with all key metrics  
        - 📄 **Export functionality** for individual properties
        - 📈 **Analysis statistics** and insights
        - 🎨 **Color-coded scoring** (Green: 70+, Yellow: 50-69, Red: <50)
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    🏠 Property Analysis Tool | Built with Streamlit | 
    Auto-scoring based on price, location, commute, schools & more
</div>
""", unsafe_allow_html=True)
