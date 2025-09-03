import pandas as pd
import numpy as np
import csv
import os
from io import StringIO
from collections import defaultdict

def manual_csv_parsing(csv_file_path):
    """
    Manual parsing for complex CSV formats
    
    Args:
        csv_file_path (str): Path to the CSV file
    
    Returns:
        pd.DataFrame: Parsed dataframe or None if failed
    """
    print("Attempting manual parsing...")
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        try:
            with open(csv_file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Cannot read file even for manual parsing: {e}")
            return None
    
    # Find header and data rows
    data_rows = []
    headers = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Look for header row (contains "Ticker", "Weight", "Location" etc.)
        if headers is None and any(keyword in line.lower() for keyword in ['ticker', 'weight', 'location', 'name', 'sector']):
            try:
                # Smart split considering commas inside quotes
                reader = csv.reader(StringIO(line))
                headers = next(reader)
                print(f"Found headers: {headers}")
                continue
            except:
                # Fallback: simple split
                headers = [col.strip() for col in line.split(',')]
                continue
        
        # If we found headers, try to parse data
        if headers is not None:
            try:
                reader = csv.reader(StringIO(line))
                row = next(reader)
                if len(row) >= 3:  # At least 3 columns (ticker, weight, location)
                    data_rows.append(row[:len(headers)])
            except:
                # Try simple split as fallback
                try:
                    row = [col.strip() for col in line.split(',')]
                    if len(row) >= 3:
                        # Pad with empty strings if needed
                        while len(row) < len(headers):
                            row.append('')
                        data_rows.append(row[:len(headers)])
                except:
                    continue
    
    if headers and data_rows:
        df = pd.DataFrame(data_rows, columns=headers)
        print(f"✓ Manual parsing successful: {len(data_rows)} rows, {len(headers)} columns")
        return df
    else:
        print("✗ Manual parsing failed")
        return None

def analyze_etf_country_allocation(csv_file_path):
    """
    Analyze geographic allocation of an ETF from CSV file
    
    Args:
        csv_file_path (str): Path to the CSV file
    
    Returns:
        tuple: (country_weights, country_percentages, clean_dataframe) or None
    """
    
    df = None
    
    # Try multiple reading approaches
    try:
        print("Attempting to read CSV file...")
        
        # Option 1: Standard CSV
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8')
            print("✓ Successfully read with comma separator")
        except:
            # Option 2: Semicolon separator
            try:
                df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')
                print("✓ Successfully read with semicolon separator")
            except:
                # Option 3: Tab separator
                try:
                    df = pd.read_csv(csv_file_path, sep='\t', encoding='utf-8')
                    print("✓ Successfully read with tab separator")
                except:
                    # Option 4: Automatic separator detection
                    try:
                        df = pd.read_csv(csv_file_path, sep=None, engine='python', encoding='utf-8')
                        print("✓ Successfully read with automatic separator detection")
                    except:
                        # Option 5: Latin encoding + automatic detection
                        try:
                            df = pd.read_csv(csv_file_path, sep=None, engine='python', encoding='latin-1')
                            print("✓ Successfully read with latin-1 encoding")
                        except:
                            # Try manual parsing as last resort
                            print("All standard methods failed, trying manual parsing...")
                            df = manual_csv_parsing(csv_file_path)
                            if df is None:
                                return None
                            
    except Exception as e:
        print(f"General error reading file: {e}")
        return None
    
    if df is None:
        return None
        
    # Print available columns for debugging
    print("\nAvailable columns in CSV:")
    print(df.columns.tolist())
    print(f"\nDataFrame shape: {df.shape}")
    print("\nFirst 3 rows:")
    print(df.head(3))
    
    # Automatically identify relevant columns
    weight_col = None
    location_col = None
    
    # Search for weight column (weight/peso/%)
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if any(keyword in col_lower for keyword in ['weight', 'peso', '%', 'percent', 'allocation']):
            weight_col = col
            break
    
    # Search for location/country column
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if any(keyword in col_lower for keyword in ['location', 'country', 'paese', 'nazione', 'region']):
            location_col = col
            break
    
    if weight_col is None or location_col is None:
        print(f"\nWARNING: Cannot automatically identify columns.")
        print(f"Weight column found: {weight_col}")
        print(f"Location column found: {location_col}")
        
        # Allow manual input
        print("\nAvailable columns:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")
        
        try:
            weight_idx = int(input("Enter weight column index: "))
            location_idx = int(input("Enter location column index: "))
            
            weight_col = df.columns[weight_idx]
            location_col = df.columns[location_idx]
        except (ValueError, IndexError):
            print("Invalid column selection")
            return None
    
    print(f"\nUsing weight column: {weight_col}")
    print(f"Using location column: {location_col}")
    
    # Clean the data
    df_clean = df.dropna(subset=[weight_col, location_col]).copy()
    
    # Convert weights to numeric (handle % symbols and strings)
    if df_clean[weight_col].dtype == 'object':
        # Remove % symbols and convert
        df_clean[weight_col] = df_clean[weight_col].astype(str).str.replace('%', '').str.replace(',', '.')
        df_clean[weight_col] = pd.to_numeric(df_clean[weight_col], errors='coerce')
    
    # Remove rows with invalid weights
    df_clean = df_clean.dropna(subset=[weight_col])
    
    # Normalize country names
    df_clean[location_col] = df_clean[location_col].astype(str).str.strip()
    
    # Country mapping for similar names (extend as needed)
    country_mapping = {
        'Korea (South)': 'South Korea',
        'China': 'China',
        'Taiwan': 'Taiwan',
        'India': 'India',
        'Germany': 'Germany',
        'South Africa': 'South Africa',
        'Saudi Arabia': 'Saudi Arabia',
        'Brazil': 'Brazil',
        'United States': 'United States',
        'Japan': 'Japan',
        'United Kingdom': 'United Kingdom'
    }
    
    # Apply mapping
    df_clean['Country_Normalized'] = df_clean[location_col].map(country_mapping).fillna(df_clean[location_col])
    
    # Calculate percentages by country
    country_weights = df_clean.groupby('Country_Normalized')[weight_col].sum().sort_values(ascending=False)
    
    # Calculate percentages
    total_weight = country_weights.sum()
    country_percentages = (country_weights / total_weight * 100).round(2)
    
    return country_weights, country_percentages, df_clean

def print_results(country_weights, country_percentages):
    """Print results in a readable format"""
    
    print("\n" + "="*60)
    print("ETF GEOGRAPHIC ALLOCATION")
    print("="*60)
    
    print(f"\n{'Country':<25} {'Total Weight':<15} {'Percentage':<15}")
    print("-" * 60)
    
    for country in country_percentages.index:
        weight = country_weights[country]
        percentage = country_percentages[country]
        print(f"{country:<25} {weight:<15.2f} {percentage:<15.2f}%")
    
    print("-" * 60)
    print(f"{'TOTAL':<25} {country_weights.sum():<15.2f} {country_percentages.sum():<15.2f}%")
    
    # Top 5 countries
    print(f"\nTOP 5 COUNTRIES:")
    for i, (country, percentage) in enumerate(country_percentages.head(5).items(), 1):
        print(f"{i}. {country}: {percentage:.2f}%")

def export_results(country_weights, country_percentages, output_file="country_allocation.csv"):
    """Export results to CSV"""
    
    results_df = pd.DataFrame({
        'Country': country_percentages.index,
        'Total_Weight': country_weights.values,
        'Percentage': country_percentages.values
    }).sort_values('Percentage', ascending=False)
    
    results_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nResults exported to: {output_file}")
    return results_df

def quick_analysis(csv_file, weight_column, location_column):
    """
    Quick analysis if you already know the column names
    
    Args:
        csv_file (str): Path to CSV file
        weight_column (str): Name of weight column
        location_column (str): Name of location column
    
    Returns:
        pd.Series: Country percentages
    """
    df = pd.read_csv(csv_file)
    
    # Calculate percentages by country directly
    country_allocation = df.groupby(location_column)[weight_column].sum().sort_values(ascending=False)
    country_percentages = (country_allocation / country_allocation.sum() * 100).round(2)
    
    print("\nGEOGRAPHIC ALLOCATION (Quick Analysis):")
    for country, percentage in country_percentages.items():
        print(f"{country}: {percentage}%")
    
    return country_percentages

# Main execution
if __name__ == "__main__":
    # Replace with your CSV file path
    csv_file = "eimi_holdings.csv"
    
    print("ETF Geographic Allocation Analysis Script")
    print("=" * 50)
    
    # Check if file exists, ask user if not
    if not os.path.exists(csv_file):
        csv_file = input("Enter CSV file path: ").strip('"\'')
        if not os.path.exists(csv_file):
            print(f"File not found: {csv_file}")
            exit(1)
    
    print(f"Analyzing file: {csv_file}")
    
    # Analyze the file
    result = analyze_etf_country_allocation(csv_file)
    
    if result:
        country_weights, country_percentages, df_clean = result
        
        # Print results
        print_results(country_weights, country_percentages)
        
        # Export results
        export_results(country_weights, country_percentages)
        
        # Additional statistics
        print(f"\nSTATISTICS:")
        print(f"Total holdings: {len(df_clean)}")
        print(f"Number of countries: {len(country_percentages)}")
        print(f"Top 3 countries concentration: {country_percentages.head(3).sum():.2f}%")
        print(f"Top 5 countries concentration: {country_percentages.head(5).sum():.2f}%")
        
        # Concentration analysis
        if len(country_percentages) > 1:
            print(f"Most concentrated country: {country_percentages.iloc[0]:.2f}%")
            print(f"Least concentrated country: {country_percentages.iloc[-1]:.2f}%")
        
    else:
        print("\n" + "="*60)
        print("UNABLE TO ANALYZE FILE")
        print("="*60)
        print("Suggestions:")
        print("1. Check that the file is a valid CSV")
        print("2. Ensure it contains 'Weight' and 'Location' columns")
        print("3. Try saving the file as UTF-8 CSV from Excel")
        print("4. Check for special characters in headers")
        print("5. Make sure the file path is correct")
        
        # Show file info for debugging
        try:
            with open(csv_file, 'r') as f:
                first_lines = [next(f) for _ in range(min(3, sum(1 for _ in f) + 1))]
                print(f"\nFirst few lines of the file:")
                for i, line in enumerate(first_lines, 1):
                    print(f"Line {i}: {repr(line[:100])}")  # Show first 100 chars
        except Exception as e:
            print(f"Cannot even read file for debugging: {e}")

print("\n" + "="*60)
print("Script completed!")
print("="*60)