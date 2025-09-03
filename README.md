# ETF Geographic Analyzer

A Python tool for analyzing the geographic allocation of ETF holdings from CSV files. Automatically calculates country-wise distribution percentages and excludes cash/currency positions for accurate equity allocation analysis.

## 🌍 Features

- **Automatic CSV parsing** with multiple format support (comma, semicolon, tab separators)
- **Smart column detection** for weight and location data
- **Cash filtering** - Automatically excludes cash, money market, and currency positions
- **Geographic normalization** - Standardizes country names (e.g., "Korea (South)" → "South Korea")
- **Multiple encoding support** (UTF-8, Latin-1)
- **Export functionality** - Saves results to CSV
- **Diversification metrics** - Includes Herfindahl concentration index
- **Robust error handling** with manual parsing fallback

## 📋 Requirements

```
pandas>=1.3.0
numpy>=1.20.0
```

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/etf-geographic-analyzer.git
cd etf-geographic-analyzer
```

2. Install dependencies:
```bash
pip install pandas numpy
```

## 📊 Usage

### Basic Usage

Place your ETF holdings CSV file in the project directory and run:

```bash
python percentage_nations_etf.py
```

The script will look for `eimi_holdings.csv` by default, or prompt you for a file path.

### CSV Format Requirements

Your CSV should contain at least these columns:
- **Weight column**: Contains percentage weights (e.g., "Weight (%)", "Allocation", "Peso")
- **Location column**: Contains country/region names (e.g., "Location", "Country", "Region")

Example CSV structure:
```csv
Ticker,Name,Sector,Weight (%),Location
2330,TAIWAN SEMICONDUCTOR MANUFACTURING,Information Technology,8.75,Taiwan
700,TENCENT HOLDINGS LTD,Communication,4.65,China
CASH_USD,US Dollar Cash,Cash,2.1,United States
```

### Quick Analysis

If you know your column names, you can use the quick analysis function:

```python
from percentage_nations_etf import quick_analysis

# Analyze with known column names
percentages = quick_analysis("your_file.csv", "Weight (%)", "Location")
```

## 📈 Output

The tool provides:

### Console Output
```
ETF GEOGRAPHIC ALLOCATION
============================================================

Country                   Total Weight    Percentage     
------------------------------------------------------------
China                     15.23           32.45%
Taiwan                    10.14           21.60%
India                     8.95            19.08%
South Korea               4.23            9.02%
Brazil                    2.87            6.12%
...

TOP 5 COUNTRIES:
1. China: 32.45%
2. Taiwan: 21.60%
3. India: 19.08%
4. South Korea: 9.02%
5. Brazil: 6.12%

STATISTICS:
Total equity holdings analyzed: 3156
Number of countries: 24
Cash/currency positions excluded: 65
Geographic concentration index (Herfindahl): 24.67
```

### CSV Export
Results are automatically exported to `country_allocation.csv`:
```csv
Country,Total_Weight,Percentage
China,15.23,32.45
Taiwan,10.14,21.60
India,8.95,19.08
...
```

## 🛠️ Advanced Features

### Manual Column Selection
If automatic detection fails, the tool prompts for manual column selection:
```
Available columns:
0: Ticker
1: Name
2: Weight (%)
3: Location
Enter weight column index: 2
Enter location column index: 3
```

### Country Name Normalization
The tool normalizes similar country names:
- "Korea (South)" → "South Korea"
- Maintains consistency across datasets

### Error Handling
- Multiple parsing attempts with different separators and encodings
- Manual parsing fallback for complex formats
- Detailed error messages and debugging information

## 📊 Supported File Formats

- **CSV files** with various separators (`,`, `;`, `\t`)
- **Multiple encodings** (UTF-8, Latin-1)
- **Headers with metadata** (automatically skips non-data rows)
- **Quoted fields** with embedded commas

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Example Use Cases

- **Portfolio analysis**: Understand geographic diversification of your ETF investments
- **Risk assessment**: Identify concentration risk in specific countries/regions
- **Compliance**: Generate reports for regulatory requirements
- **Research**: Analyze ETF composition changes over time

## ⚡ Performance

- Processes thousands of holdings in seconds
- Memory efficient with pandas optimization
- Handles large CSV files (tested up to 10MB+)

## 🐛 Troubleshooting

### Common Issues

1. **"Cannot automatically identify columns"**
   - Solution: Use manual column selection or rename CSV headers

2. **"Error tokenizing data"**
   - Solution: The tool automatically tries multiple parsing methods

3. **"No valid data found"**
   - Solution: Ensure CSV contains numeric weight data and location information

### Debug Mode
Run with verbose output to see parsing attempts:
```python
# The tool automatically shows debug information during parsing
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [pandas](https://pandas.pydata.org/) for data manipulation
- Inspired by the need for better ETF portfolio analysis tools

## 📞 Support

If you encounter issues or have questions:
1. Check the troubleshooting section
2. Open an issue on GitHub
3. Provide sample data (anonymized) for better support

---

**Made with ❤️ for better investment analysis**