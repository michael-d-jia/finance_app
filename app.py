import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Jia's Family Finance Summary",
    page_icon="💰",
    layout="wide"
)

# ============================================================================
# CATEGORIZATION LOGIC
# ============================================================================

# Category definitions with keywords and descriptions
CATEGORY_DEFINITIONS = {
    'Utilities': {
        'keywords': [
            'ELECTRIC', 'WATER', 'GAS', 'INTERNET', 'PHONE', 'CELLULAR', 'MOBILE',
            'SHELL', 'CHEVRON', 'EXXON', 'BP', 'ARCO', 'VALERO', 'GAS STATION',
            'POWER', 'UTILITY', 'PG&E', 'EDISON', 'CON EDISON', 'DUKE ENERGY',
            'AT&T', 'VERIZON', 'T-MOBILE', 'SPRINT', 'COMCAST', 'XFINITY',
            'SPECTRUM', 'COX', 'OPTIMUM', 'CABLE', 'INTERNET SERVICE'
        ],
        'description': 'Monthly utilities and services: electricity, water, gas, internet, phone, cable, and gas station purchases'
    },
    'Entertainment': {
        'keywords': [
            'NETFLIX', 'SPOTIFY', 'DISNEY', 'HULU', 'AMAZON PRIME', 'APPLE TV',
            'YOUTUBE PREMIUM', 'PARAMOUNT', 'HBO', 'MAX', 'PEACOCK', 'SHOWTIME',
            'CINEMA', 'MOVIE', 'THEATER', 'AMC', 'REGAL', 'CINEMARK',
            'CONCERT', 'TICKETMASTER', 'STUBHUB', 'EVENTBRITE',
            'GAME', 'STEAM', 'PLAYSTATION', 'XBOX', 'NINTENDO',
            'MUSIC', 'APPLE MUSIC', 'PANDORA', 'AUDIBLE', 'BOOKS'
        ],
        'description': 'Streaming services, movies, concerts, games, books, and entertainment subscriptions'
    },
    'Travel': {
        'keywords': [
            'HOTEL', 'MOTEL', 'AIRBNB', 'VRBO', 'RESORT', 'LODGING',
            'AIRLINE', 'DELTA', 'UNITED', 'AMERICAN AIRLINES', 'SOUTHWEST',
            'JETBLUE', 'ALASKA AIR', 'FRONTIER', 'SPIRIT',
            'UBER', 'LYFT', 'TAXI', 'RIDESHARE', 'TRANSPORTATION',
            'BOOKING', 'EXPEDIA', 'TRIVAGO', 'KAYAK', 'PRICELINE',
            'RENTAL CAR', 'HERTZ', 'ENTERPRISE', 'AVIS', 'BUDGET',
            'TRAVEL', 'VACATION', 'TRIP', 'FLIGHT', 'AIRPORT'
        ],
        'description': 'Hotels, flights, car rentals, rideshares, and all travel-related expenses'
    },
    'Clothes, shoes': {
        'keywords': [
            'ZARA', 'NIKE', 'UNIQLO', 'MACY', "MACY'S", 'H&M', 'ADIDAS',
            'OLD NAVY', 'GAP', 'TARGET', 'WALMART', 'COSTCO', 'AMAZON',
            'NORDSTROM', 'BLOOMINGDALE', 'SAKS', 'NEIMAN MARCUS',
            'FOOT LOCKER', 'FINISH LINE', 'DSW', 'SHOE',
            'CLOTHING', 'APPAREL', 'FASHION', 'OUTFIT', 'WARDROBE',
            'BANANA REPUBLIC', 'J.CREW', 'ABERCROMBIE', 'HOLLISTER',
            'LULULEMON', 'ATHLETA', 'UNDER ARMOUR', 'PUMA', 'REEBOK'
        ],
        'description': 'Clothing, shoes, accessories, and fashion purchases from retail stores'
    },
    'Property Tax': {
        'keywords': [
            'TAX', 'COUNTY', 'PROPERTY TAX', 'REAL ESTATE TAX',
            'ASSESSOR', 'TREASURER', 'TAX ASSESSMENT',
            'PROPERTY ASSESSMENT', 'TAX BILL', 'TAX PAYMENT'
        ],
        'description': 'Property taxes, county assessments, and real estate tax payments'
    },
    'Groceries': {
        'keywords': [
            'WHOLE FOODS', 'TRADER JOE', "TRADER JOE'S", 'COSTCO', 'KROGER',
            'SAFEWAY', 'ALBERTSONS', 'VONS', 'RALPHS', 'FOOD LION',
            'PUBLIX', 'WEGMANS', 'H-E-B', 'WINN-DIXIE', 'GIANT',
            'STOP & SHOP', 'SHOPRITE', 'MEIJER', 'HY-VEE',
            'GROCERY', 'SUPERMARKET', 'MARKET', 'FOOD STORE',
            'SPROUTS', 'FRESH MARKET', 'WHOLE FOODS MARKET'
        ],
        'description': 'Grocery shopping, food purchases, and household essentials from supermarkets'
    },
    'Dining': {
        'keywords': [
            'RESTAURANT', 'CAFE', 'COFFEE', 'STARBUCKS', 'DUNKIN',
            'MCDONALD', 'BURGER KING', 'WENDY', 'TACO BELL',
            'CHIPOTLE', 'PANERA', 'SUBWAY', 'DOMINO', 'PIZZA',
            'DINING', 'EAT', 'FOOD', 'LUNCH', 'DINNER', 'BREAKFAST',
            'GRUBHUB', 'DOORDASH', 'UBER EATS', 'POSTMATES',
            'CAFE', 'BAKERY', 'DELI', 'FAST FOOD'
        ],
        'description': 'Restaurant meals, coffee shops, fast food, and food delivery services'
    },
    'Healthcare': {
        'keywords': [
            'PHARMACY', 'CVS', 'WALGREENS', 'RITE AID', 'PHARMACY',
            'DOCTOR', 'HOSPITAL', 'MEDICAL', 'HEALTH', 'CLINIC',
            'DENTIST', 'DENTAL', 'VISION', 'OPTICAL', 'EYE',
            'INSURANCE', 'HEALTH INSURANCE', 'MEDICAL BILL',
            'PRESCRIPTION', 'MEDICATION', 'DRUG STORE'
        ],
        'description': 'Medical expenses, prescriptions, doctor visits, dental, vision, and health insurance'
    },
    'Education': {
        'keywords': [
            'SCHOOL', 'UNIVERSITY', 'COLLEGE', 'TUITION', 'EDUCATION',
            'TEXTBOOK', 'BOOKSTORE', 'STUDENT', 'COURSE', 'CLASS',
            'TUTOR', 'LESSON', 'TRAINING', 'SEMINAR', 'WORKSHOP'
        ],
        'description': 'Tuition, school supplies, textbooks, courses, and educational expenses'
    },
    'Home & Garden': {
        'keywords': [
            'HOME DEPOT', 'LOWE', "LOWE'S", 'HARDWARE', 'HOME IMPROVEMENT',
            'IKEA', 'WAYFAIR', 'OVERSTOCK', 'BED BATH', 'BED BATH & BEYOND',
            'FURNITURE', 'DECOR', 'GARDEN', 'LANDSCAPING', 'LAWN',
            'HARDWARE STORE', 'PAINT', 'TOOL', 'APPLIANCE'
        ],
        'description': 'Home improvement, furniture, appliances, gardening supplies, and household items'
    },
    'Insurance': {
        'keywords': [
            'INSURANCE', 'AUTO INSURANCE', 'CAR INSURANCE', 'HOME INSURANCE',
            'RENTERS INSURANCE', 'LIFE INSURANCE', 'GEICO', 'STATE FARM',
            'PROGRESSIVE', 'ALLSTATE', 'FARMERS', 'LIBERTY MUTUAL'
        ],
        'description': 'Auto, home, renters, life, and other insurance premiums'
    },
    'Transportation': {
        'keywords': [
            'METRO', 'SUBWAY', 'BUS', 'TRANSIT', 'PUBLIC TRANSPORT',
            'PARKING', 'TOLL', 'EZPASS', 'FASSTRAK', 'TOLL ROAD',
            'CAR WASH', 'AUTO REPAIR', 'MECHANIC', 'OIL CHANGE',
            'TIRE', 'AUTO PARTS', 'NAPA', 'AUTOZONE', 'ORILEY'
        ],
        'description': 'Public transportation, parking, tolls, car maintenance, and auto services (excluding gas)'
    },
    'Shopping': {
        'keywords': [
            'AMAZON', 'EBAY', 'ETSY', 'ONLINE', 'SHOPPING',
            'DEPARTMENT STORE', 'RETAIL', 'STORE'
        ],
        'description': 'General shopping and retail purchases not categorized elsewhere'
    }
}

def categorize_transaction(row):
    """
    Categorize transactions based on priority:
    1. Keyword match in 'Description'
    2. Use existing 'Category' column with mapping
    3. Fallback to original category or 'Other'
    """
    description = str(row.get('Description', '')).upper()
    original_category = str(row.get('Category', 'Other')).upper()
    
    # Priority 1: Keyword Match in Description
    for category, info in CATEGORY_DEFINITIONS.items():
        for keyword in info['keywords']:
            if keyword in description:
                return category
    
    # Priority 2: Map existing Category column
    category_mapping = {
        'BILLS & UTILITIES': 'Utilities',
        'BILLS AND UTILITIES': 'Utilities',
        'UTILITIES': 'Utilities',
        'GROCERIES': 'Groceries',
        'GROCERY': 'Groceries',
        'GAS': 'Utilities',
        'GAS & FUEL': 'Utilities',
        'ENTERTAINMENT': 'Entertainment',
        'TRAVEL': 'Travel',
        'SHOPPING': 'Shopping',
        'DINING': 'Dining',
        'FOOD & DINING': 'Dining',
        'HEALTHCARE': 'Healthcare',
        'MEDICAL': 'Healthcare',
        'EDUCATION': 'Education',
        'HOME & GARDEN': 'Home & Garden',
        'HOME IMPROVEMENT': 'Home & Garden',
        'INSURANCE': 'Insurance',
        'TRANSPORTATION': 'Transportation',
        'AUTO & TRANSPORT': 'Transportation'
    }
    
    if original_category in category_mapping:
        return category_mapping[original_category]
    
    # Priority 3: Fallback to original category
    return original_category.title() if original_category and original_category != 'OTHER' else 'Other'


# ============================================================================
# DATA PROCESSING
# ============================================================================

def normalize_column_names(df):
    """
    Normalize column names to handle variations in CSV headers.
    Maps common variations to standard column names.
    """
    # Create a mapping of possible variations to standard names
    column_mapping = {}
    
    # Normalize all column names to uppercase and remove spaces/underscores
    normalized_columns = {col.upper().replace(' ', '').replace('_', ''): col for col in df.columns}
    
    # Standard column name mappings
    standard_columns = {
        'TRANSACTIONDATE': 'Transaction Date',
        'DATE': 'Transaction Date',
        'TRANSACTION_DATE': 'Transaction Date',
        'TRANS DATE': 'Transaction Date',
        'POSTDATE': 'Post Date',
        'POST_DATE': 'Post Date',
        'POSTEDDATE': 'Post Date',
        'POSTED DATE': 'Post Date',
        'DESCRIPTION': 'Description',
        'DESC': 'Description',
        'DETAILS': 'Description',
        'MERCHANT': 'Description',
        'VENDOR': 'Description',
        'CATEGORY': 'Category',
        'CAT': 'Category',
        'TYPE': 'Type',
        'TRANSACTIONTYPE': 'Type',
        'TRANSACTION_TYPE': 'Type',
        'AMOUNT': 'Amount',
        'AMT': 'Amount',
        'TRANSACTIONAMOUNT': 'Amount',
        'TRANSACTION_AMOUNT': 'Amount',
        'DEBIT': 'Debit',
        'CREDIT': 'Credit',
        'DEBITS': 'Debits',
        'CREDITS': 'Credits',
        'MEMO': 'Memo',
        'NOTES': 'Memo',
        'REFERENCE': 'Memo',
        'REFERENCE NO.': 'Reference No.'
    }
    
    # Find matches and create mapping
    for std_key, std_value in standard_columns.items():
        # Try exact match first
        if std_key in normalized_columns:
            column_mapping[normalized_columns[std_key]] = std_value
        else:
            # Try partial matches
            for norm_key, orig_col in normalized_columns.items():
                if std_key in norm_key or norm_key in std_key:
                    column_mapping[orig_col] = std_value
                    break
    
    # Also check for case-insensitive partial matches
    for orig_col in df.columns:
        orig_upper = orig_col.upper().replace(' ', '').replace('_', '')
        for std_key, std_value in standard_columns.items():
            if std_key in orig_upper or orig_upper in std_key:
                if orig_col not in column_mapping:
                    column_mapping[orig_col] = std_value
    
    # Rename columns
    df_renamed = df.rename(columns=column_mapping)
    
    return df_renamed


def load_and_process_data(uploaded_files):
    """
    Load CSV files, process and categorize transactions.
    Handles inconsistent column headers by normalizing them.
    Returns processed DataFrame or None if error.
    """
    try:
        # Load all uploaded files
        dfs = []
        file_info = []
        
        for idx, file in enumerate(uploaded_files):
            try:
                # Store file content for potential re-reading
                import io
                file_bytes = file.read()
                file_io = io.BytesIO(file_bytes)
                
                # Try different encodings
                try:
                    file_io.seek(0)
                    df = pd.read_csv(file_io, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        file_io.seek(0)
                        df = pd.read_csv(file_io, encoding='latin-1')
                    except:
                        file_io.seek(0)
                        df = pd.read_csv(file_io, encoding='cp1252')
                
                # Check if column names look like data (dates, numbers) rather than headers
                # This handles files with unlabeled headers or headerless files
                column_names = list(df.columns)
                looks_like_unlabeled = False
                
                # Check if column names are dates or numbers (unlabeled headers)
                for col in column_names[:3]:  # Check first 3 columns
                    col_str = str(col)
                    # Check if column name looks like a date (MM/DD/YYYY or similar)
                    if '/' in col_str and any(char.isdigit() for char in col_str):
                        looks_like_unlabeled = True
                        break
                    # Check if column name is numeric or starts with special chars
                    if col_str.replace('-', '').replace('.', '').replace('/', '').isdigit() or col_str.startswith('-'):
                        looks_like_unlabeled = True
                        break
                
                # Check if first row looks like headers or data
                first_row_values = df.iloc[0].astype(str).tolist() if len(df) > 0 else []
                looks_like_data = any(
                    any(char.isdigit() for char in str(val)) and len(str(val)) > 5 
                    for val in first_row_values[:3]
                )
                
                # If column names look unlabeled OR first row looks like data, handle as headerless
                if looks_like_unlabeled or (looks_like_data and len(df.columns) <= 3):
                    # Re-read file without header
                    try:
                        file_io.seek(0)
                        df = pd.read_csv(file_io, encoding='utf-8', header=None)
                        
                        # Assign standard column names based on number of columns
                        if len(df.columns) >= 3:
                            df.columns = ['Transaction Date', 'Description', 'Amount'][:len(df.columns)]
                        elif len(df.columns) == 2:
                            df.columns = ['Transaction Date', 'Amount']
                        else:
                            df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
                    except Exception as e:
                        # If that fails, keep original df but rename columns if they look unlabeled
                        if looks_like_unlabeled:
                            if len(df.columns) >= 3:
                                df.columns = ['Transaction Date', 'Description', 'Amount'][:len(df.columns)]
                            elif len(df.columns) == 2:
                                df.columns = ['Transaction Date', 'Amount']
                
                # Store original column names before normalization
                original_cols_before = list(df.columns)
                
                # Find and preserve original category column BEFORE normalization
                original_cat_col = None
                for col in original_cols_before:
                    col_lower = col.lower()
                    if 'category' in col_lower or col_lower == 'cat':
                        original_cat_col = col
                        break
                
                # Store original category values if found
                original_cat_values = None
                if original_cat_col:
                    original_cat_values = df[original_cat_col].copy()
                
                # Normalize column names
                df = normalize_column_names(df)
                
                # Add original category column after normalization
                if original_cat_values is not None:
                    df['Original_Category'] = original_cat_values.fillna('Other').astype(str)
                
                # Store original column names for info
                file_info.append({
                    'file_name': file.name,
                    'original_columns': original_cols_before,
                    'row_count': len(df)
                })
                
                dfs.append(df)
                
            except Exception as e:
                st.warning(f"⚠️ Error loading {file.name}: {str(e)}")
                continue
        
        if not dfs:
            st.error("❌ No files could be loaded successfully.")
            return None
        
        # Concatenate all dataframes
        data = pd.concat(dfs, ignore_index=True)
        
        # Standardize column names for processing
        # Find the transaction date column - be more flexible
        date_col = None
        
        # First, try to find date column with various patterns
        for col in data.columns:
            col_lower = col.lower()
            # Look for transaction date first
            if 'transaction date' in col_lower:
                date_col = col
                break
            # Then look for any date column (but not post date)
            elif 'date' in col_lower and 'post' not in col_lower and date_col is None:
                date_col = col
        
        # If still not found, try any column with 'date' in it
        if not date_col:
            for col in data.columns:
                if 'date' in col.lower():
                    date_col = col
                    break
        
        # If still not found, check if any column contains date-like values
        if not date_col:
            for col in data.columns:
                # Sample first few values to see if they look like dates
                try:
                    sample = data[col].dropna().head(5)
                    if len(sample) > 0:
                        # Check if values look like dates (contain / or - and numbers)
                        date_like_count = 0
                        for val in sample:
                            val_str = str(val)
                            if ('/' in val_str or '-' in val_str) and any(c.isdigit() for c in val_str):
                                date_like_count += 1
                        if date_like_count / len(sample) > 0.6:
                            date_col = col
                            st.info(f"ℹ️ Inferred '{col}' as the date column based on data patterns.")
                            break
                except:
                    continue
        
        if date_col:
            data['Transaction Date'] = pd.to_datetime(data[date_col], errors='coerce')
        else:
            st.error("❌ Could not find a date column in the CSV files.")
            st.info(f"**Available columns:** {', '.join(data.columns.tolist())}")
            st.info("""
            **Troubleshooting:**
            - Date columns should contain dates in formats like: MM/DD/YYYY, YYYY-MM-DD, etc.
            - Column names can be: Date, Transaction Date, TransactionDate, etc.
            - The app will try to infer date columns from data patterns
            """)
            
            # Show file info
            with st.expander("📋 File Details"):
                for info in file_info:
                    st.write(f"**{info['file_name']}**: {info['row_count']} rows")
                    st.write(f"Columns: {', '.join(info['original_columns'])}")
            
            return None
        
        # Find amount column - handle Debit/Credit or Credits/Debits columns
        # Also try to infer amount column from data patterns if not explicitly labeled
        amount_col = None
        debit_col = None
        credit_col = None
        
        for col in data.columns:
            col_lower = col.lower()
            if col_lower == 'amount':
                amount_col = col
            elif col_lower == 'debit':
                debit_col = col
            elif col_lower == 'credit':
                credit_col = col
            elif col_lower == 'debits':
                debit_col = col
            elif col_lower == 'credits':
                credit_col = col
        
        # If no explicit amount column found, try to infer from data
        if not amount_col and not debit_col and not credit_col:
            # Look for columns that contain numeric values that could be amounts
            for col in data.columns:
                col_lower = col.lower()
                # Skip date, description, category, type, and memo columns
                skip_keywords = ['date', 'description', 'desc', 'category', 'cat', 'type', 'memo', 'reference', 'ref', 'account', 'card']
                if any(keyword in col_lower for keyword in skip_keywords):
                    continue
                
                # Try to convert column to numeric
                try:
                    sample_values = data[col].dropna().head(20)  # Check more samples
                    if len(sample_values) > 0:
                        # Check if values look like amounts (numeric, possibly with $ or commas)
                        numeric_count = 0
                        total_numeric_value = 0
                        for val in sample_values:
                            val_str = str(val).replace('$', '').replace(',', '').replace('(', '').replace(')', '').strip()
                            try:
                                num_val = float(val_str)
                                numeric_count += 1
                                total_numeric_value += abs(num_val)
                            except:
                                pass
                        
                        # If most values are numeric AND they look like transaction amounts (not too small, not too large)
                        if numeric_count / len(sample_values) > 0.7:
                            avg_value = total_numeric_value / numeric_count if numeric_count > 0 else 0
                            # Amounts should typically be reasonable transaction sizes (between $0.01 and $1,000,000)
                            if 0.01 <= avg_value <= 1000000:
                                amount_col = col
                                st.info(f"ℹ️ Inferred '{col}' as the amount column based on data patterns.")
                                break
                except Exception as e:
                    continue
        
        # Create Amount column from available columns
        if amount_col:
            # Convert amount to numeric, handling currency symbols and commas
            data['Amount'] = pd.to_numeric(
                data[amount_col].astype(str).str.replace('$', '').str.replace(',', '').str.replace('(', '-').str.replace(')', ''),
                errors='coerce'
            )
        elif debit_col and credit_col:
            # Handle Debit/Credit columns (Capital One style)
            debit_values = pd.to_numeric(
                data[debit_col].astype(str).str.replace('$', '').str.replace(',', '').str.replace('(', '-').str.replace(')', ''),
                errors='coerce'
            ).fillna(0)
            credit_values = pd.to_numeric(
                data[credit_col].astype(str).str.replace('$', '').str.replace(',', '').str.replace('(', '-').str.replace(')', ''),
                errors='coerce'
            ).fillna(0)
            # Debits are negative, Credits are positive
            data['Amount'] = credit_values - debit_values
        elif debit_col:
            # Only debit column (expenses)
            data['Amount'] = -pd.to_numeric(
                data[debit_col].astype(str).str.replace('$', '').str.replace(',', '').str.replace('(', '-').str.replace(')', ''),
                errors='coerce'
            )
        elif credit_col:
            # Only credit column (income)
            data['Amount'] = pd.to_numeric(
                data[credit_col].astype(str).str.replace('$', '').str.replace(',', '').str.replace('(', '-').str.replace(')', ''),
                errors='coerce'
            )
        else:
            st.error("❌ Could not find an amount column in the CSV files.")
            st.info(f"**Available columns:** {', '.join(data.columns.tolist())}")
            st.info("""
            **Troubleshooting:**
            - If your CSV has Debit/Credit columns, make sure they're labeled as 'Debit' and 'Credit'
            - If your CSV has unlabeled columns, the app will try to infer which column contains amounts
            - Amount columns should contain numeric values (with or without $ signs)
            - Common amount column names: Amount, Amt, Debit, Credit, Debits, Credits, Transaction Amount
            """)
            
            # Show file info with sample data
            with st.expander("📋 File Details & Sample Data"):
                for info in file_info:
                    st.write(f"**{info['file_name']}**: {info['row_count']} rows")
                    st.write(f"Columns: {', '.join(info['original_columns'])}")
                    # Show sample of first few rows
                    try:
                        file_io = io.BytesIO()
                        # We can't easily show sample data here, but we can list columns
                    except:
                        pass
            
            return None
        
        # Now verify we have both required columns after processing
        if 'Transaction Date' not in data.columns or 'Amount' not in data.columns:
            missing = []
            if 'Transaction Date' not in data.columns:
                missing.append('Transaction Date')
            if 'Amount' not in data.columns:
                missing.append('Amount')
            st.error(f"❌ Could not process required columns: {', '.join(missing)}")
            st.info(f"**Available columns after processing:** {', '.join(data.columns.tolist())}")
            return None
        
        # Handle description and category columns (optional)
        desc_col = None
        for col in data.columns:
            if 'description' in col.lower() or 'desc' in col.lower() or 'details' in col.lower():
                desc_col = col
                break
        
        if desc_col:
            data['Description'] = data[desc_col].fillna('')
        else:
            data['Description'] = ''
        
        # Find and preserve original Category column
        cat_col = None
        for col in data.columns:
            col_lower = col.lower()
            if col_lower == 'category' or col_lower == 'cat':
                cat_col = col
                break
        
        if cat_col:
            # Use normalized category column
            data['Category'] = data[cat_col].fillna('Other').astype(str)
            # If Original_Category doesn't exist, use Category
            if 'Original_Category' not in data.columns:
                data['Original_Category'] = data['Category']
        else:
            data['Category'] = 'Other'
            if 'Original_Category' not in data.columns:
                data['Original_Category'] = 'Other'
        
        # Drop rows with invalid dates or amounts
        initial_count = len(data)
        data = data.dropna(subset=['Transaction Date', 'Amount'])
        dropped_count = initial_count - len(data)
        
        if dropped_count > 0:
            st.info(f"ℹ️ Dropped {dropped_count} rows with invalid dates or amounts.")
        
        if len(data) == 0:
            st.error("❌ No valid data remaining after processing.")
            return None
        
        # Extract Year and Month
        data['Year'] = data['Transaction Date'].dt.year
        data['Month'] = data['Transaction Date'].dt.month
        data['Month_Name'] = data['Transaction Date'].dt.strftime('%B')
        
        # Apply categorization
        data['Processed_Category'] = data.apply(categorize_transaction, axis=1)
        
        # Separate Income and Expenses
        data['Is_Income'] = data['Amount'] > 0
        data['Abs_Amount'] = data['Amount'].abs()
        
        # Show success message with file info
        st.success(f"✅ Successfully loaded {len(data)} transactions from {len(dfs)} file(s)")
        
        return data
    
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
        import traceback
        with st.expander("🔍 Error Details"):
            st.code(traceback.format_exc())
        return None


def calculate_metrics(data, selected_year):
    """Calculate yearly income and expenses"""
    year_data = data[data['Year'] == selected_year]
    
    total_income = year_data[year_data['Is_Income']]['Amount'].sum()
    total_expenses = abs(year_data[~year_data['Is_Income']]['Amount'].sum())
    
    return total_income, total_expenses


def prepare_monthly_expense_data(data, selected_year):
    """Prepare data for monthly expense chart"""
    # Filter for selected year and expenses only
    expense_data = data[(data['Year'] == selected_year) & (~data['Is_Income'])].copy()
    
    # Group by Month and Category
    monthly_expenses = expense_data.groupby(['Month', 'Month_Name', 'Processed_Category'])['Abs_Amount'].sum().reset_index()
    
    # Sort by month number
    monthly_expenses = monthly_expenses.sort_values('Month')
    
    return monthly_expenses


# ============================================================================
# VISUALIZATION
# ============================================================================

def create_monthly_expense_chart(monthly_data):
    """Create stacked bar chart for monthly expenses by category"""
    if monthly_data.empty:
        st.warning("No expense data available for the selected year.")
        return None
    
    fig = px.bar(
        monthly_data,
        x='Month_Name',
        y='Abs_Amount',
        color='Processed_Category',
        title='Monthly Expenses by Category',
        labels={
            'Month_Name': 'Month',
            'Abs_Amount': 'Amount ($)',
            'Processed_Category': 'Category'
        },
        height=500,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Update layout for better readability
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        legend_title='Category',
        hovermode='x unified',
        barmode='stack'
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickprefix='$', tickformat=',.0f')
    
    return fig


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Title
    st.title("💰 Jia's Family Yearly Finance Summary")
    st.markdown("---")
    
    # Sidebar - File Upload
    with st.sidebar:
        st.header("📁 Upload Bank Statements")
        uploaded_files = st.file_uploader(
            "Upload Chase CSV files",
            type=['csv'],
            accept_multiple_files=True,
            help="Upload one or more Chase bank statement CSV files"
        )
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.markdown("""
        This app analyzes bank statements to provide:
        - Total income and expenses
        - Monthly spending breakdown
        - Categorized transactions
        - Flexible CSV column handling
        """)
    
    # Main Content
    if not uploaded_files:
        st.info("👆 Please upload one or more CSV files to get started.")
        
        # Show example of expected format
        with st.expander("ℹ️ CSV Format Requirements"):
            st.markdown("""
            **Required Columns** (case-insensitive, variations accepted):
            - **Transaction Date** (or Date, TransactionDate, Transaction_Date)
            - **Amount** (or Amt, TransactionAmount, Transaction_Amount)
            
            **Optional Columns**:
            - **Description** (or Desc, Details, Merchant, Vendor)
            - **Category** (or Cat)
            - **Type** (or TransactionType)
            - **Post Date** (or PostDate, PostedDate)
            - **Memo** (or Notes, Reference)
            
            **Note**: The app automatically handles variations in column names, 
            so your CSV files don't need to match exactly. Amount can include 
            currency symbols and commas.
            """)
        return
    
    # Load and process data
    with st.spinner("Processing data..."):
        data = load_and_process_data(uploaded_files)
    
    if data is None:
        return
    
    # Year Filter in Sidebar
    with st.sidebar:
        st.markdown("---")
        st.header("🗓️ Filter by Year")
        available_years = sorted(data['Year'].unique())
        
        if len(available_years) == 0:
            st.error("No valid years found in data")
            return
        
        selected_year = st.selectbox(
            "Select Year",
            options=available_years,
            index=len(available_years) - 1  # Default to most recent year
        )
    
    # Calculate metrics
    total_income, total_expenses = calculate_metrics(data, selected_year)
    
    # Display Metrics
    st.header(f"📈 {selected_year} Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💵 Total Income",
            value=f"${total_income:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 Total Expenses",
            value=f"${total_expenses:,.2f}",
            delta=None
        )
    
    with col3:
        net_savings = total_income - total_expenses
        st.metric(
            label="💰 Net Savings",
            value=f"${net_savings:,.2f}",
            delta=None,
            delta_color="normal" if net_savings >= 0 else "inverse"
        )
    
    st.markdown("---")
    
    # Monthly Expense Chart
    st.header("📊 Monthly Expense Breakdown")
    monthly_data = prepare_monthly_expense_data(data, selected_year)
    
    if not monthly_data.empty:
        fig = create_monthly_expense_chart(monthly_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expense data available for the selected year.")
    
    # Additional insights
    st.markdown("---")
    st.header("🔍 Category Breakdown")
    
    # Category summary
    year_expenses = data[(data['Year'] == selected_year) & (~data['Is_Income'])]
    category_summary = year_expenses.groupby('Processed_Category')['Abs_Amount'].sum().sort_values(ascending=False)
    
    if not category_summary.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                values=category_summary.values,
                names=category_summary.index,
                title='Expense Distribution by Category',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("Top Categories")
            # Use container with proper spacing
            for idx, (category, amount) in enumerate(category_summary.head(10).items(), 1):
                percentage = (amount / category_summary.sum()) * 100
                # Use metric or markdown with better spacing
                st.markdown(f"**{idx}. {category}**")
                st.markdown(f"<span style='margin-left: 20px;'>${amount:,.2f} ({percentage:.1f}%)</span>", unsafe_allow_html=True)
                st.markdown("")  # Add spacing between items
    
    # Category Definitions
    st.markdown("---")
    st.header("📚 Category Definitions")
    st.markdown("Understanding what's included in each expense category:")
    
    # Show categories that appear in the data
    categories_in_data = set(category_summary.index) if not category_summary.empty else set()
    all_categories = set(CATEGORY_DEFINITIONS.keys())
    
    # Create columns for better layout with proper spacing
    cols = st.columns(2)
    col_idx = 0
    
    for category in sorted(all_categories):
        if category in CATEGORY_DEFINITIONS:
            info = CATEGORY_DEFINITIONS[category]
            with cols[col_idx % 2]:
                # Highlight if category appears in data
                if category in categories_in_data:
                    st.markdown(f"**{category}** ✅")
                else:
                    st.markdown(f"**{category}**")
                # Use caption for better text wrapping
                st.caption(info['description'])
                st.markdown("<br>", unsafe_allow_html=True)
            col_idx += 1
    
    # Show original categories from CSV files if different
    if 'Original_Category' in data.columns:
        original_cats = data[data['Year'] == selected_year]['Original_Category'].unique()
        processed_cats = set(category_summary.index) if not category_summary.empty else set()
        original_only = [cat for cat in original_cats if cat not in processed_cats and str(cat) != 'Other' and str(cat) != 'nan']
        
        if original_only:
            st.markdown("---")
            st.subheader("📋 Original Categories from CSV Files")
            st.info(f"These categories from your CSV files were mapped to processed categories: {', '.join(sorted(set(original_cats))[:10])}")
    
    # Raw data view (optional)
    with st.expander("🔎 View Raw Transaction Data"):
        year_data = data[data['Year'] == selected_year].sort_values('Transaction Date', ascending=False)
        # Select available columns for display
        display_columns = []
        for col in ['Transaction Date', 'Description', 'Processed_Category', 'Amount', 'Type', 'Category']:
            if col in year_data.columns:
                display_columns.append(col)
        
        if display_columns:
            st.dataframe(
                year_data[display_columns],
                use_container_width=True,
                height=400
            )
        else:
            st.info("No displayable columns found.")


if __name__ == "__main__":
    main()

