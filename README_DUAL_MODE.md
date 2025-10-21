
# London Property Analyzer - Dual Mode System 🏠

**Enhanced property search, analysis, and scoring platform with automated scraping capabilities**

## 🚀 New Features Overview

### **Dual Mode Architecture**
- **Mode 1:** Individual Property Analysis (manual entry + URL import)
- **Mode 2:** Area Search & Bulk Discovery (automated search + batch processing)

### **Enhanced Capabilities**
- 🔍 **Property Scraping:** Rightmove, Zoopla, OnTheMarket support
- 📊 **Advanced Analytics:** Interactive graphs, radar charts, scatter plots
- 🗺️ **Interactive Maps:** Property markers, commute circles, clustering  
- 📈 **Real-time Scoring:** Dynamic 7-category scoring system
- 💾 **Data Persistence:** CSV/Excel import/export with full state management

---

## 📋 Complete Features List

### **🏠 Tab 1: Add Property (Individual Analysis)**
**Original functionality preserved and enhanced:**
- ✅ All 17 data entry fields (A-Q) with proper organization
- ✅ Reference postcode settings in sidebar (default: SE1 9SP London Bridge)  
- ✅ Real-time automated scoring (7 categories, 0-100 points)
- ✅ Required fields marked with red asterisk (*)
- ✅ Auto-calculated fields clearly labeled
- ✅ **NEW:** Quick import from property URLs (Rightmove, Zoopla, OnTheMarket)
- ✅ **NEW:** Auto-population of scraped property data
- ✅ **NEW:** Enhanced form validation and error handling

**Enhanced Scoring System:**
- Price Score (0-20 points) - Weighted by budget range
- Commute Score (0-20 points) - Based on travel time to reference location
- Property Type Score (0-15 points) - House > Maisonette > Flat preference
- Bedrooms Score (0-15 points) - Based on minimum requirements
- Outdoor Space Score (0-10 points) - Garden > Terrace > Balcony > None
- Schools Score (0-10 points) - Outstanding > Good > Requires Improvement
- Grammar School Bonus (0-10 points) - Distance-based proximity scoring

### **🔍 Tab 2: Search & Discover (Bulk Discovery)**
**Completely new functionality:**
- 🔗 **Search URL Generation:** Create optimized search links for all major sites
- 🏘️ **Area Search:** Filter by postcode, radius, price range, bedrooms, property type
- 🤖 **Experimental Auto-Search:** Automated scraping with anti-bot protection
- 📋 **Batch URL Import:** Process multiple property URLs simultaneously  
- ⚡ **Parallel Processing:** Multi-threaded scraping with rate limiting
- 📊 **Import Preview:** Review scraped data before adding to analysis
- 🛡️ **Error Handling:** Graceful degradation when scraping fails

**Supported Websites:**
- Rightmove (full scraping + search URL generation)
- Zoopla (full scraping + search URL generation)  
- OnTheMarket (full scraping + search URL generation)
- Generic property sites (basic scraping support)

### **📊 Tab 3: Analysis & Graphs**
**Professional data visualization:**
- 📈 **Price Distribution:** Histogram showing property price spread
- 🎯 **Score Distribution:** Analysis of property scores across portfolio
- 🥧 **Property Type Breakdown:** Pie chart of house/flat/maisonette distribution
- 🏠 **Bedroom Distribution:** Bar chart of bedroom counts
- 💰 **Price vs Commute:** Scatter plot with score-based sizing
- 🕷️ **Radar Chart:** Multi-dimensional analysis of top 5 properties
- 📋 **Sortable Data Table:** Interactive property data with custom sorting
- 📊 **Summary Metrics:** Total properties, average price, score statistics

### **🗺️ Tab 4: Property Map**  
**Interactive geospatial analysis:**
- 🗺️ **Folium Integration:** Professional interactive mapping
- 🏠 **Property Markers:** Color-coded by score, price, or commute time
- 📍 **Reference Location:** Home/work postcode marker
- ⭕ **Commute Radius:** Visual circle showing maximum travel distance
- 💬 **Rich Popups:** Detailed property information on click
- 🎨 **Dynamic Coloring:** Green (good) → Orange (okay) → Red (poor)
- 🏷️ **Smart Tooltips:** Quick property info on hover
- 📱 **Responsive Design:** Mobile-friendly map controls

### **🏆 Tab 5: Top 5 Dashboard**
**Executive summary and action center:**
- 🥇 **Medal Rankings:** Gold, Silver, Bronze for top performers  
- 📊 **Detailed Cards:** Price, commute, details, schools for each property
- ✅ **Status Indicators:** Within budget, acceptable commute validation
- 🔗 **Action Links:** Direct links to listings, agent phone numbers
- ⭐ **Priority Marking:** Flag properties for priority viewing
- 📄 **Property Summaries:** Expandable detailed descriptions
- 💾 **Export Options:** CSV download, property ID copying, map navigation

---

## 🛠️ Technical Architecture

### **Core Components**

**property_scraper.py:**
- Multi-site scraping engine with anti-bot measures
- User-agent rotation and request delays
- Parallel processing with thread safety
- Error handling and graceful degradation
- Search URL generation for all major sites

**automation_engine.py:**  
- Mock API integration (commute, schools, transport)
- Scoring algorithm implementation
- Data validation and processing
- Reference postcode calculations

**api_simulator.py:**
- Simulated external API responses
- Consistent mock data generation
- London-specific area knowledge
- Grammar school distance calculations

**app.py:**
- 5-tab Streamlit interface  
- Session state management
- Real-time calculations
- Interactive visualizations
- Data persistence layer

### **Anti-Bot Protection**
- Random delays between requests (2-5 seconds)
- User-agent string rotation
- Request rate limiting
- Graceful failure handling
- Terms of service compliance warnings

### **Data Architecture**
- Pandas DataFrames for efficient processing
- Session state persistence across tabs
- CSV/Excel import/export compatibility
- Real-time score recalculation
- Automatic data validation

---

## 🚀 Getting Started

### **Prerequisites**
```bash
Python 3.8+
pip install -r requirements.txt
```

### **Installation**
```bash
# Clone or download the application files
git clone https://github.com/your-repo/london-property-analyzer

# Install dependencies  
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### **Quick Start Workflow**

**Option 1: Individual Property Analysis**
1. Open **Tab 1: Add Property**
2. Paste a property URL in "Quick Import from URL"
3. Click "Fetch Details" to auto-populate fields
4. Review and adjust any fields as needed  
5. Click "Add Property" to save with automatic scoring

**Option 2: Bulk Property Discovery**
1. Open **Tab 2: Search & Discover**  
2. Set search criteria (postcode, price range, bedrooms)
3. Click "Generate Search URLs" to get optimized search links
4. Browse properties on Rightmove/Zoopla/OnTheMarket
5. Copy interesting property URLs
6. Paste URLs in "Batch URL Import" section
7. Click "Process All URLs" for automatic import and scoring

**Analysis and Decision Making**
1. **Tab 3:** Review graphs and data trends
2. **Tab 4:** View properties on interactive map
3. **Tab 5:** Focus on top 5 scored properties for viewings

---

## 📊 Scoring Methodology

### **Category Weightings (Configurable in Sidebar)**
- **Price Importance:** 20% (0.1-0.4 range)
- **Commute Importance:** 20% (0.1-0.4 range)  
- **Property Type Importance:** 15% (0.05-0.25 range)
- **Bedrooms Importance:** 15% (0.05-0.25 range)
- **Outdoor Space Importance:** 10% (0.05-0.15 range)
- **Schools Importance:** 10% (0.05-0.15 range)
- **Grammar School Bonus:** 10% (0.05-0.15 range)

### **Score Calculation Details**

**Price Score (0-20 points):**
- Properties within minimum budget: 20 points
- Properties above maximum budget: 0 points  
- Linear scaling between min/max budget bounds

**Commute Score (0-20 points):**
- ≤30 minutes: 20 points
- ≥Maximum commute setting: 0 points
- Linear scaling between 30 minutes and maximum

**Property Type Score (0-15 points):**
- House: 15 points
- Maisonette/Duplex: 12 points  
- Flat/Apartment: 8 points
- Other: 5 points

**Bedrooms Score (0-15 points):**
- ≥Minimum + 2: 15 points
- Minimum + 1: 12 points
- Exactly minimum: 8 points
- Below minimum: 3 × bedroom count

**Outdoor Space Score (0-10 points):**
- Garden/Terrace/Patio: 10 points
- Balcony: 6 points
- None: 2 points

**Schools Score (0-10 points):**
- Outstanding: 10 points
- Good: 7 points
- Requires Improvement: 4 points
- Inadequate: 2 points

**Grammar School Bonus (0-10 points):**
- ≤2km: 10 points
- ≤5km: 6 points  
- ≤10km: 3 points
- >10km: 0 points

---

## 🔒 Legal and Ethical Considerations

### **Web Scraping Compliance**
- **Rate Limiting:** 2-5 second delays between requests
- **Respectful Crawling:** Limited concurrent requests
- **Terms of Service:** Clear warnings about website policies
- **Graceful Failure:** No aggressive retry mechanisms
- **User Responsibility:** Scraping is user-initiated and controlled

### **Recommended Usage**
- Use search URL generation for manual browsing (most reliable)
- Import individual property URLs as needed (semi-automated)
- Use bulk scraping sparingly and responsibly (experimental)
- Respect website terms of service and rate limits
- Consider premium API access for commercial use

---

## 🛠️ Configuration Options

### **Sidebar Settings**
- **Reference Location:** Home/work postcode for commute calculations
- **Budget Range:** Minimum and maximum property prices  
- **Requirements:** Minimum bedrooms, maximum commute time
- **Scoring Weights:** Adjust importance of each category
- **Advanced:** Fine-tune scoring algorithm parameters

### **Data Management**
- **Export:** CSV download of all properties or top 5 only
- **Import:** Upload existing property CSV files
- **Clear:** Reset all data and start fresh
- **Backup:** Automatic session state preservation

---

## 🐛 Troubleshooting

### **Common Issues**

**Scraping Fails:**
- Check internet connection
- Verify property URL is accessible
- Some sites may be blocking automated access
- Try manual copy/paste of property details

**Map Not Loading:**
- Ensure folium and streamlit-folium are installed
- Check if running in compatible browser
- Refresh page if map appears blank

**Import Errors:**
- Verify CSV file format matches expected columns
- Check for special characters in property data
- Ensure file is not corrupted or locked

**Performance Issues:**
- Limit batch URL processing to 10-20 properties at once
- Clear browser cache if interface becomes slow
- Restart Streamlit app if memory usage is high

### **Getting Help**
- Check console logs for detailed error messages
- Verify all dependencies are installed correctly
- Test with sample property URLs first
- Review Terms of Service for target websites

---

## 🎯 Best Practices

### **Efficient Workflow**
1. **Start with Search:** Use URL generation to find properties manually
2. **Selective Import:** Only scrape properties you're genuinely interested in  
3. **Regular Reviews:** Use analytics tab to understand your preferences
4. **Top 5 Focus:** Use dashboard to narrow down to viewing candidates
5. **Data Backup:** Export data regularly to avoid loss

### **Scraping Guidelines**
- Limit bulk imports to 10-20 properties per session
- Allow 30+ seconds between large batch operations
- Use during off-peak hours when possible
- Respect website rate limits and error responses
- Consider manual data entry for small numbers of properties

### **Analysis Tips**
- Adjust scoring weights based on your priorities
- Use map view to understand geographic distribution
- Review score breakdown in radar charts
- Export top properties for offline review
- Share CSV files with family/advisors for input

---

## 📈 Future Enhancements

### **Planned Features**
- Real estate API integrations (Rightmove, Zoopla commercial APIs)
- Browser extension for seamless property capture
- Mobile-responsive design improvements
- Advanced filtering and search capabilities
- Property comparison tools and side-by-side analysis
- Historical price tracking and trend analysis
- Automated viewing scheduler integration
- Enhanced geolocation and transport API integration

### **Technical Roadmap**
- Dockerized deployment options
- Database backend for better data persistence
- User authentication and multi-user support
- Advanced caching for improved performance
- Real-time property alerts and notifications
- Integration with mortgage calculators and affordability tools

---

## 📄 License and Support

This application is provided as-is for personal property search use. Please ensure compliance with all applicable terms of service when using web scraping features.

**Support:** For technical issues or feature requests, please refer to the project documentation or create an issue in the project repository.

**Contributing:** Contributions are welcome! Please follow standard GitHub workflow for pull requests and ensure all new features include appropriate tests and documentation.
