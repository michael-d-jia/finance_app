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
        'MEMO': 'Memo',
        'NOTES': 'Memo',
        'REFERENCE': 'Memo'
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
                # Try different encodings
                try:
                    df = pd.read_csv(file, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(file, encoding='latin-1')
                    except:
                        df = pd.read_csv(file, encoding='cp1252')
                
                # Normalize column names
                df = normalize_column_names(df)
                
                # Store original column names for info
                file_info.append({
                    'file_name': file.name,
                    'original_columns': list(df.columns),
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
        
        # Check for required columns (case-insensitive)
        required_columns_lower = ['transaction date', 'amount']
        available_columns_lower = [col.lower() for col in data.columns]
        
        missing_columns = []
        for req_col in required_columns_lower:
            if req_col not in available_columns_lower:
                missing_columns.append(req_col)
        
        if missing_columns:
            st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
            st.info(f"**Available columns in your CSV:** {', '.join(data.columns.tolist())}")
            st.info("""
            **Expected column names (case-insensitive, variations accepted):**
            - Transaction Date (or Date, TransactionDate, Transaction_Date)
            - Amount (or Amt, TransactionAmount, Transaction_Amount)
            - Description (or Desc, Details, Merchant, Vendor) - Optional
            - Category (or Cat) - Optional
            - Type - Optional
            - Post Date - Optional
            - Memo - Optional
            """)
            
            # Show file info
            with st.expander("📋 File Details"):
                for info in file_info:
                    st.write(f"**{info['file_name']}**: {info['row_count']} rows")
                    st.write(f"Columns: {', '.join(info['original_columns'])}")
            
            return None
        
        # Standardize column names for processing
        # Find the transaction date column
        date_col = None
        for col in data.columns:
            if 'transaction date' in col.lower() or ('date' in col.lower() and 'post' not in col.lower()):
                date_col = col
                break
        
        if not date_col:
            date_col = [col for col in data.columns if 'date' in col.lower()][0] if any('date' in col.lower() for col in data.columns) else None
        
        if date_col:
            data['Transaction Date'] = pd.to_datetime(data[date_col], errors='coerce')
        else:
            st.error("❌ Could not find a date column in the CSV files.")
            return None
        
        # Find amount column
        amount_col = None
        for col in data.columns:
            if col.lower() == 'amount' or 'amount' in col.lower():
                amount_col = col
                break
        
        if amount_col:
            # Convert amount to numeric, handling currency symbols and commas
            data['Amount'] = pd.to_numeric(
                data[amount_col].astype(str).str.replace('$', '').str.replace(',', '').str.replace('(', '-').str.replace(')', ''),
                errors='coerce'
            )
        else:
            st.error("❌ Could not find an amount column in the CSV files.")
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
        
        cat_col = None
        for col in data.columns:
            if col.lower() == 'category' or 'category' in col.lower():
                cat_col = col
                break
        
        if cat_col:
            data['Category'] = data[cat_col].fillna('Other')
        else:
            data['Category'] = 'Other'
        
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
            for idx, (category, amount) in enumerate(category_summary.head(10).items(), 1):
                percentage = (amount / category_summary.sum()) * 100
                st.markdown(f"**{idx}. {category}**")
                st.markdown(f"   ${amount:,.2f} ({percentage:.1f}%)")
    
    # Category Definitions
    st.markdown("---")
    st.header("📚 Category Definitions")
    st.markdown("Understanding what's included in each expense category:")
    
    # Show categories that appear in the data
    categories_in_data = set(category_summary.index) if not category_summary.empty else set()
    all_categories = set(CATEGORY_DEFINITIONS.keys())
    
    # Create columns for better layout
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
                st.markdown(f"*{info['description']}*")
                st.markdown("")
            col_idx += 1
    
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

