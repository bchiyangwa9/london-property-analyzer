# 🚀 Quick Start Guide

Get up and running with the London Property Search Analyzer in just a few minutes!

## 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.11+** installed on your system
- **pip** package manager
- **Git** (optional, for cloning)

### Checking Your Python Version
```bash
python --version
# Should show Python 3.11.0 or higher
```

## 🔧 Installation Methods

### Method 1: Direct Download (Recommended)
1. Download the complete ZIP archive
2. Extract to your desired directory
3. Continue to the "Setup" section below

### Method 2: Git Clone
```bash
git clone <repository-url>
cd london-property-analyzer
```

## ⚙️ Setup

### 1. Navigate to Project Directory
```bash
cd london-property-analyzer
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install all required packages:
- streamlit>=1.28.0
- pandas>=2.0.0
- numpy>=1.24.0
- plotly>=5.15.0
- folium>=0.14.0
- streamlit-folium>=0.13.0
- openpyxl>=3.1.0
- And more...

## 🎉 Running the Application

### Start the Streamlit Server
```bash
streamlit run app.py
```

### Expected Output
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501
```

### Access the Application
1. Open your web browser
2. Go to `http://localhost:8501`
3. The London Property Search Analyzer should load

## 🏠 First Search

### 1. Set Search Criteria
In the sidebar, configure:
- **Property Type**: Select "Flat" for your first search
- **Price Range**: Set min £400,000 and max £800,000
- **Bedrooms**: Choose 1-2 bedrooms
- **Borough**: Select "Camden"

### 2. Execute Search
Click the **"🔍 Search Properties"** button

### 3. View Results
You should see:
- Property count and statistics
- Interactive data table
- Price analysis charts
- Property locations on map

## 📊 Exploring Features

### Data Visualization Tabs
- **Price Analysis**: Histograms and scatter plots
- **Property Types**: Distribution pie charts
- **Borough Analysis**: Geographic comparisons
- **Map View**: Interactive property locations

### Export Options
- **📊 Export to Excel**: Download multi-sheet workbook
- **📄 Generate Report**: Create comprehensive analysis
- **📧 Schedule Email**: Set up automated reports

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Port Already in Use
```
Error: Port 8501 is in use
```
**Solution**: Use a different port
```bash
streamlit run app.py --server.port 8502
```

#### Missing Dependencies
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### Browser Doesn't Open Automatically
**Solution**: Manually open http://localhost:8501

#### Blank Page or Loading Issues
**Solutions**:
1. Refresh the browser page
2. Check terminal for error messages
3. Restart the Streamlit server

### Performance Tips
- **Close unused browser tabs** to free memory
- **Use Chrome or Firefox** for best compatibility
- **Restart the app** if it becomes slow

## 📱 Browser Compatibility

### Recommended Browsers
- ✅ **Google Chrome** (latest)
- ✅ **Mozilla Firefox** (latest)
- ✅ **Microsoft Edge** (latest)
- ✅ **Safari** (macOS/iOS)

### Mobile Support
The application is responsive and works on:
- 📱 **Smartphones** (portrait/landscape)
- 📱 **Tablets** (recommended for best experience)

## 🎛️ Configuration

### Default Settings
The application runs with these defaults:
- **Port**: 8501
- **Host**: localhost
- **Theme**: Light mode with blue accents

### Customizing Configuration
Edit `.streamlit/config.toml` to modify:
```toml
[server]
port = 8501
headless = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
```

## 📚 Next Steps

Now that you have the application running:

1. **📖 Read the [User Guide](USER_GUIDE.md)** for detailed feature explanations
2. **🧪 Try the sample data** provided in `templates/`
3. **📤 Import your own data** using the CSV templates
4. **🚀 Deploy to production** following the [Deployment Guide](README_DEPLOYMENT.md)

## 🆘 Getting Help

### Documentation Resources
- 📘 **[User Guide](USER_GUIDE.md)**: Comprehensive feature documentation
- 🚀 **[Deployment Guide](README_DEPLOYMENT.md)**: Production deployment
- 📋 **[Main README](../README.md)**: Project overview

### Support Channels
- 🐛 **Bug Reports**: Open a GitHub issue
- 💡 **Feature Requests**: Use GitHub discussions
- ❓ **Questions**: Check existing documentation first

### Community
- 🌟 **Star the project** on GitHub
- 🍴 **Fork and contribute** improvements
- 📢 **Share with others** who might find it useful

---

**🎉 Congratulations!** You now have the London Property Search Analyzer running locally. Happy property hunting! 🏠
