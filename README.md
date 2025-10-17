# 🏠 London Property Search Analyzer

A comprehensive property search and analysis tool for the London real estate market, built with Python and Streamlit.

![Property Analyzer](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## 🎯 Overview

The London Property Search Analyzer is a powerful web application that provides comprehensive property market analysis for London. It offers advanced search capabilities, interactive visualizations, automated reporting, and market insights to help users make informed property decisions.

## ✨ Key Features

### 🔍 **Advanced Property Search**
- **Multi-criteria filtering**: Property type, price range, bedrooms, location
- **Geographic targeting**: Search by specific London boroughs
- **Special requirements**: New build, garden, parking options
- **Real-time results**: Instant property matching and filtering

### 📊 **Interactive Data Visualization**
- **Price analysis charts**: Distribution histograms, scatter plots, trend analysis
- **Property type breakdowns**: Pie charts and comparative analysis
- **Borough market insights**: Geographic price comparisons
- **Interactive maps**: Property locations with price-coded markers

### 📈 **Market Analytics**
- **Statistical summaries**: Average, median, min/max prices
- **Market trends**: Price per square foot analysis
- **Comparative data**: Borough and property type comparisons
- **Investment insights**: Market recommendations and hotspots

### 📄 **Automated Reporting**
- **Excel export**: Multi-sheet workbooks with charts and analysis
- **PDF reports**: Comprehensive market analysis documents
- **Email scheduling**: Automated report delivery
- **Custom templates**: Branded report generation

### 🔧 **Data Management**
- **Excel import/export**: Bulk property data processing
- **Data validation**: Comprehensive quality checks
- **Template generation**: Standardized data formats
- **API integration**: Real-time property data (simulated)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip package manager

### Installation

1. **Clone or Download the Repository**
   ```bash
   git clone <repository-url>
   cd london-property-analyzer
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

4. **Access the Web Interface**
   - Open your browser and go to `http://localhost:8501`
   - Start searching and analyzing London properties!

## 📁 Project Structure

```
london-property-analyzer/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version specification
├── Procfile                        # Deployment configuration
├── README.md                       # This file
├── .streamlit/
│   └── config.toml                # Streamlit configuration
├── utils/
│   ├── __init__.py               # Package initialization
│   ├── automation_engine.py      # Automated tasks and scheduling
│   ├── api_simulator.py          # Property API simulation
│   ├── excel_handler.py          # Excel import/export functionality
│   └── validators.py             # Data validation utilities
├── templates/
│   ├── sample_properties_template.csv  # Sample data for testing
│   └── empty_template.csv             # Template for data import
└── docs/
    ├── Quick_Start_Guide.md       # Detailed setup instructions
    ├── USER_GUIDE.md             # Comprehensive user manual
    └── README_DEPLOYMENT.md       # Deployment instructions
```

## 🎮 Usage Guide

### 1. **Basic Property Search**
- Use the sidebar to set your search criteria
- Select property type, price range, and number of bedrooms
- Choose specific London boroughs or search all areas
- Apply additional filters (new build, garden, parking)
- Click "Search Properties" to see results

### 2. **Analyzing Results**
- View summary statistics in the overview section
- Browse detailed property listings in the data table
- Explore interactive charts and visualizations
- Check property locations on the interactive map

### 3. **Exporting Data**
- Export results to Excel with multiple analysis sheets
- Generate comprehensive PDF reports
- Schedule automated email reports
- Download raw data in CSV format

### 4. **Importing Your Own Data**
- Use the provided CSV templates
- Upload Excel files with property data
- Validate data quality with built-in checks
- Process bulk property information

## 🛠️ Technical Features

### **Built With**
- **[Streamlit](https://streamlit.io/)**: Web application framework
- **[Pandas](https://pandas.pydata.org/)**: Data manipulation and analysis
- **[Plotly](https://plotly.com/)**: Interactive visualizations
- **[Folium](https://folium.readthedocs.io/)**: Interactive maps
- **[OpenPyXL](https://openpyxl.readthedocs.io/)**: Excel file handling

### **Key Components**
- **API Simulator**: Realistic property data generation
- **Automation Engine**: Background task scheduling
- **Excel Handler**: Advanced spreadsheet operations
- **Data Validators**: Comprehensive data quality checks

### **Data Processing**
- Real-time property filtering and sorting
- Statistical analysis and aggregations
- Geographic data processing
- Price trend calculations

## 🌐 Deployment Options

### **Streamlit Cloud (Recommended)**
1. Fork this repository to your GitHub account
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Deploy with one click

### **Heroku Deployment**
1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Create a new Heroku app
3. Deploy using Git:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### **Local Development**
```bash
# Install in development mode
pip install -e .

# Run with hot reloading
streamlit run app.py --logger.level debug
```

See [docs/README_DEPLOYMENT.md](docs/README_DEPLOYMENT.md) for detailed deployment instructions.

## 📚 Documentation

- **[Quick Start Guide](docs/Quick_Start_Guide.md)**: Get up and running in minutes
- **[User Guide](docs/USER_GUIDE.md)**: Comprehensive feature documentation
- **[Deployment Guide](docs/README_DEPLOYMENT.md)**: Production deployment instructions

## 🔧 Configuration

The application can be configured through:
- **`.streamlit/config.toml`**: Streamlit-specific settings
- **Environment variables**: API keys and deployment settings
- **Runtime configuration**: Python version and dependencies

## 📊 Sample Data

The application includes sample London property data for demonstration:
- **10 sample properties** across different London boroughs
- **Realistic pricing** based on current market conditions
- **Various property types**: Flats, houses, studios, penthouses
- **Complete metadata**: Features, agent details, energy ratings

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### **Development Setup**
```bash
# Clone your fork
git clone https://github.com/yourusername/london-property-analyzer.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run tests (if applicable)
python -m pytest tests/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Getting Help**
- 📖 Check the [User Guide](docs/USER_GUIDE.md) for detailed instructions
- 🐛 Report bugs by opening a GitHub issue
- 💡 Request features through GitHub discussions
- 📧 Contact support at support@propertyanalyzer.com

### **Common Issues**
- **Port already in use**: Change the port in `.streamlit/config.toml`
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Data validation errors**: Check the CSV template format

## 🚧 Roadmap

### **Upcoming Features**
- [ ] **Real API Integration**: Connect to actual property APIs
- [ ] **Machine Learning**: Price prediction and market forecasting
- [ ] **Mobile App**: Native iOS/Android applications
- [ ] **Multi-city Support**: Expand beyond London to other UK cities
- [ ] **Advanced Analytics**: Investment ROI calculations
- [ ] **User Accounts**: Save searches and preferences

### **Technical Improvements**
- [ ] **Database Integration**: PostgreSQL/MongoDB support
- [ ] **Caching Layer**: Redis for improved performance
- [ ] **API Rate Limiting**: Enhanced API management
- [ ] **Unit Testing**: Comprehensive test coverage
- [ ] **CI/CD Pipeline**: Automated testing and deployment

## 🏆 Acknowledgments

- **Streamlit Team**: For the amazing web app framework
- **London Property Market**: For inspiration and data insights
- **Open Source Community**: For the excellent Python libraries
- **Contributors**: Everyone who helps improve this project

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/london-property-analyzer?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/london-property-analyzer?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/london-property-analyzer)
![GitHub license](https://img.shields.io/github/license/yourusername/london-property-analyzer)

---

**Built with ❤️ for the London property market**

*For more information, visit our [documentation](docs/) or [open an issue](https://github.com/yourusername/london-property-analyzer/issues).*
