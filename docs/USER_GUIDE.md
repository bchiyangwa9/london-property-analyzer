# 📖 User Guide

Complete guide to using the London Property Search Analyzer effectively.

## 🏠 Introduction

The London Property Search Analyzer is designed to help you find, analyze, and understand the London property market. This guide covers all features and functionality in detail.

## 🚀 Getting Started

### Initial Setup
1. Follow the [Quick Start Guide](Quick_Start_Guide.md) to install and run the application
2. Open your browser to `http://localhost:8501`
3. Familiarize yourself with the interface layout

### Interface Overview
- **Sidebar**: Search configuration and filters
- **Main Area**: Results, visualizations, and data tables
- **Header**: Application title and navigation
- **Footer**: Credits and last updated information

## 🔍 Property Search

### Basic Search Parameters

#### Property Type Selection
- **All**: Search across all property types
- **Flat**: Apartments and flats only
- **House**: All house types (terraced, semi-detached, detached)
- **Studio**: Studio apartments
- **Penthouse**: Luxury penthouse properties
- **Maisonette**: Multi-level apartments

#### Price Range Configuration
- **Minimum Price**: Set the lowest acceptable price
- **Maximum Price**: Set the highest acceptable price
- **Tips**:
  - Use realistic London price ranges (£200k - £5M+)
  - Consider your budget carefully
  - Wider ranges return more results

#### Bedroom Requirements
- **Slider Control**: Select minimum and maximum bedrooms
- **Range**: 0-5 bedrooms supported
- **Studio Consideration**: Studios typically show as 0 bedrooms

### Advanced Filters

#### Location Targeting
- **Borough Selection**: Choose specific London boroughs
- **Available Boroughs**:
  - Westminster (Central London)
  - Kensington and Chelsea (Luxury area)
  - Camden (Trendy north London)
  - Islington (Popular residential)
  - Tower Hamlets (East London, Canary Wharf)
  - Hackney (Trendy east London)
  - Southwark (South of Thames)
  - Lambeth (South London)
  - Wandsworth (Southwest London)
  - Hammersmith and Fulham (West London)

#### Special Requirements
- **New Build Only**: Filter for recently constructed properties
- **Garden Required**: Properties with private or shared gardens
- **Parking Required**: Properties with dedicated parking spaces

### Executing Searches
1. Configure all desired parameters in the sidebar
2. Click **"🔍 Search Properties"** button
3. Wait for the progress indicator to complete
4. Review results in the main area

## 📊 Results Analysis

### Overview Statistics
The results overview provides key metrics:
- **Total Properties**: Number of matching properties found
- **Average Price**: Mean price of all results
- **Median Price**: Middle value price (often more representative)
- **Average Size**: Mean square footage

### Data Table Features

#### Interactive Filtering
- **Filter by Type**: Narrow results to specific property types
- **Filter by Borough**: Focus on particular areas
- **Sort Options**: Order by price, bedrooms, size, or price per sq ft

#### Column Information
- **Address**: Full property address including postcode
- **Property Type**: Flat, House, Studio, etc.
- **Bedrooms**: Number of bedrooms
- **Price**: Listed price in GBP
- **Square Feet**: Property size
- **Price per Sq Ft**: Calculated efficiency metric
- **Borough**: London borough location

### Visualization Tabs

#### Price Analysis Tab
- **Price Distribution Histogram**: Shows how properties are distributed across price ranges
- **Price vs Size Scatter Plot**: Reveals relationship between property size and price
- **Price per Sq Ft by Type**: Compares value across property types

#### Property Types Tab
- **Type Distribution Pie Chart**: Shows proportion of each property type in results
- **Bedroom Distribution Bar Chart**: Displays bedroom count frequency
- **Price Box Plot by Type**: Shows price ranges and outliers by property type

#### Borough Analysis Tab
- **Average Price by Borough**: Horizontal bar chart comparing borough prices
- **Property Count by Borough**: Shows availability in each area
- **Market Insights**: Identify high-value vs high-volume areas

#### Map View Tab
- **Interactive London Map**: Properties plotted by location
- **Price Color Coding**:
  - 🟢 Green: Under £400k
  - 🟠 Orange: £400k - £700k
  - 🔴 Red: Over £700k
- **Property Details**: Click markers for detailed information

## 📁 Data Export

### Excel Export
Generate comprehensive Excel workbooks with:

#### Multiple Sheets
- **Properties**: Raw property data
- **Summary**: Key statistics and metrics
- **Borough Analysis**: Geographic breakdown
- **Property Types**: Type-based analysis
- **Chart Data**: Data formatted for charts

#### Features
- **Professional Formatting**: Headers, colors, and styling
- **Auto-sized Columns**: Optimized for readability
- **Number Formatting**: Currency symbols and thousands separators

#### Usage
1. Click **"📊 Export to Excel"** button
2. Wait for processing to complete
3. Click **"📥 Download Excel File"** when ready
4. Save to your desired location

### Report Generation
Create comprehensive market analysis reports:

#### Report Content
- **Executive Summary**: Key findings and statistics
- **Price Analysis**: Detailed price breakdowns
- **Borough Insights**: Geographic market analysis
- **Property Type Analysis**: Type-specific data
- **Investment Recommendations**: Market suggestions

#### Format Options
- **Markdown**: Text-based format for documentation
- **Future Formats**: PDF and HTML reports planned

### Email Scheduling (Demo)
Set up automated report delivery:

#### Configuration
- **Email Address**: Recipient for reports
- **Frequency**: Daily, Weekly, or Monthly
- **Time Slot**: Morning, Afternoon, or Evening delivery

#### Note
This is currently a demonstration feature showing how email automation would work in a production environment.

## 📤 Data Import

### CSV Template Usage

#### Available Templates
- **Sample Template**: Contains example London properties
- **Empty Template**: Blank template for new data

#### Required Columns
- **address**: Full property address (required)
- **property_type**: Type of property (required)
- **price**: Property price in GBP (required)

#### Optional Columns
- **bedrooms**: Number of bedrooms
- **bathrooms**: Number of bathrooms
- **square_feet**: Property size
- **borough**: London borough
- **features**: Comma-separated amenities
- **listing_date**: Date property was listed
- **agent_name**: Estate agent name
- **agent_phone**: Contact phone number
- **energy_rating**: Energy efficiency rating (A-G)
- **council_tax_band**: Council tax band (A-H)

### Data Validation
The system automatically validates imported data:

#### Validation Checks
- **Required Fields**: Ensures essential data is present
- **Price Ranges**: Validates realistic London prices
- **Property Types**: Confirms valid property categories
- **London Postcodes**: Checks for valid London postcode patterns
- **Date Formats**: Validates date fields
- **Contact Information**: Checks phone and email formats

#### Error Handling
- **Detailed Reports**: Specific error messages for each issue
- **Data Cleaning**: Automatic correction where possible
- **Warning System**: Alerts for unusual but valid data

## 🔧 Advanced Features

### Search History
The application maintains a history of your recent searches:
- **Last 5 Searches**: Displayed in sidebar
- **Search Parameters**: Shows what criteria were used
- **Result Counts**: How many properties were found
- **Timestamps**: When each search was performed

### Performance Optimization
The application includes several performance features:
- **Efficient Data Processing**: Optimized pandas operations
- **Caching**: Reduced repeated calculations
- **Progress Indicators**: Real-time feedback on operations
- **Error Recovery**: Graceful handling of issues

### Sample Data
The application includes realistic sample data:
- **10 Sample Properties**: Across different boroughs
- **Varied Property Types**: Flats, houses, studios, penthouses
- **Realistic Pricing**: Based on current London market
- **Complete Metadata**: All fields populated

## 🛠️ Customization

### Theme Configuration
Modify the visual appearance through `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"        # Accent color
backgroundColor = "#ffffff"      # Main background
secondaryBackgroundColor = "#f0f2f6"  # Sidebar background
textColor = "#262730"           # Text color
font = "sans serif"             # Font family
```

### Server Configuration
Adjust server settings:

```toml
[server]
port = 8501                     # Port number
headless = false                # Browser auto-open
maxUploadSize = 200             # Max file size (MB)
enableCORS = true               # Security setting
```

## 🐛 Troubleshooting

### Common Issues

#### No Search Results
**Possible Causes**:
- Search criteria too restrictive
- Price range too narrow
- Specific borough has limited properties

**Solutions**:
- Widen price range
- Select "All" for property type and borough
- Reduce bedroom requirements

#### Slow Performance
**Possible Causes**:
- Large result sets
- Multiple browser tabs
- Limited system resources

**Solutions**:
- Use more specific search criteria
- Close unnecessary browser tabs
- Restart the application

#### Export/Import Errors
**Possible Causes**:
- Invalid file formats
- Missing required data
- File permission issues

**Solutions**:
- Use provided templates
- Check required fields
- Ensure file write permissions

### Error Messages

#### "Invalid search parameters"
- Check that price ranges are logical (min < max)
- Ensure bedroom ranges are valid
- Verify all required fields are filled

#### "No properties found"
- This is normal - try broader search criteria
- London market can be limited in some segments
- Consider adjusting price range or location

#### "File upload failed"
- Check file format (CSV/Excel only)
- Ensure file is not corrupted
- Try a smaller file size

## 📞 Support Resources

### Documentation
- **[Quick Start Guide](Quick_Start_Guide.md)**: Installation and setup
- **[Deployment Guide](README_DEPLOYMENT.md)**: Production deployment
- **[Main README](../README.md)**: Project overview

### Community Support
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: Check existing guides first

### Best Practices
- **Regular Updates**: Keep dependencies current
- **Data Backup**: Save important searches and exports
- **Performance Monitoring**: Monitor system resources
- **Security**: Keep API keys secure (when using real APIs)

---

**📚 This guide covers the complete functionality of the London Property Search Analyzer. For additional help, refer to other documentation files or community support channels.**
