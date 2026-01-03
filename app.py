import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# Page Configuration
st.set_page_config(
    page_title="Jia's Family Finance Summary",
    page_icon="💰",
    layout="wide"
)

# ============================================================================
# TARGET SCHEMA - All files will be normalized to this structure
# ============================================================================
TARGET_SCHEMA = ['date', 'description', 'amount', 'category', 'source_file']

# Column mapping: maps various bank column names to our target schema
COLUMN_MAPPINGS = {
    'date': [
        'transaction date', 'transactiondate', 'trans date', 'date', 
        'post date', 'postdate', 'posted date', 'posteddate'
    ],
    'description': [
        'description', 'desc', 'details', 'merchant', 'vendor', 
        'name', 'payee', 'memo', 'transaction description'
    ],
    'amount': [
        'amount', 'amt', 'transaction amount', 'transactionamount'
    ],
    'category': [
        'category', 'cat', 'type', 'transaction type', 'transactiontype'
    ],
    'debit': ['debit', 'debits', 'withdrawal', 'withdrawals'],
    'credit': ['credit', 'credits', 'deposit', 'deposits']
}

# ============================================================================
# CATEGORIZATION LOGIC
# ============================================================================
CATEGORY_DEFINITIONS = {
    'Utilities': {
        'keywords': ['ELECTRIC', 'WATER', 'GAS', 'INTERNET', 'PHONE', 'CELLULAR', 'MOBILE',
            'SHELL', 'CHEVRON', 'EXXON', 'BP', 'ARCO', 'VALERO', 'GAS STATION',
            'POWER', 'UTILITY', 'PG&E', 'EDISON', 'CON EDISON', 'DUKE ENERGY',
            'AT&T', 'VERIZON', 'T-MOBILE', 'SPRINT', 'COMCAST', 'XFINITY',
            'SPECTRUM', 'COX', 'OPTIMUM', 'CABLE', 'INTERNET SERVICE'],
        'description': 'Monthly utilities: electricity, water, gas, internet, phone, cable'
    },
    'Entertainment': {
        'keywords': ['NETFLIX', 'SPOTIFY', 'DISNEY', 'HULU', 'AMAZON PRIME', 'APPLE TV',
            'YOUTUBE PREMIUM', 'PARAMOUNT', 'HBO', 'MAX', 'PEACOCK', 'SHOWTIME',
            'CINEMA', 'MOVIE', 'THEATER', 'AMC', 'REGAL', 'CINEMARK',
            'CONCERT', 'TICKETMASTER', 'STUBHUB', 'EVENTBRITE',
            'GAME', 'STEAM', 'PLAYSTATION', 'XBOX', 'NINTENDO',
            'MUSIC', 'APPLE MUSIC', 'PANDORA', 'AUDIBLE', 'BOOKS'],
        'description': 'Streaming, movies, concerts, games, entertainment subscriptions'
    },
    'Travel': {
        'keywords': ['HOTEL', 'MOTEL', 'AIRBNB', 'VRBO', 'RESORT', 'LODGING',
            'AIRLINE', 'DELTA', 'UNITED', 'AMERICAN AIRLINES', 'SOUTHWEST',
            'JETBLUE', 'ALASKA AIR', 'FRONTIER', 'SPIRIT',
            'UBER', 'LYFT', 'TAXI', 'RIDESHARE', 'TRANSPORTATION',
            'BOOKING', 'EXPEDIA', 'TRIVAGO', 'KAYAK', 'PRICELINE',
            'RENTAL CAR', 'HERTZ', 'ENTERPRISE', 'AVIS', 'BUDGET',
            'TRAVEL', 'VACATION', 'TRIP', 'FLIGHT', 'AIRPORT'],
        'description': 'Hotels, flights, car rentals, rideshares, travel expenses'
    },
    'Clothes & Shoes': {
        'keywords': ['ZARA', 'NIKE', 'UNIQLO', 'MACY', "MACY'S", 'H&M', 'ADIDAS',
            'OLD NAVY', 'GAP', 'NORDSTROM', 'BLOOMINGDALE', 'SAKS',
            'FOOT LOCKER', 'FINISH LINE', 'DSW', 'SHOE',
            'CLOTHING', 'APPAREL', 'FASHION', 'OUTFIT',
            'BANANA REPUBLIC', 'J.CREW', 'ABERCROMBIE', 'HOLLISTER',
            'LULULEMON', 'ATHLETA', 'UNDER ARMOUR', 'PUMA', 'REEBOK'],
        'description': 'Clothing, shoes, accessories, fashion purchases'
    },
    'Groceries': {
        'keywords': ['WHOLE FOODS', 'TRADER JOE', "TRADER JOE'S", 'COSTCO', 'KROGER',
            'SAFEWAY', 'ALBERTSONS', 'VONS', 'RALPHS', 'FOOD LION',
            'PUBLIX', 'WEGMANS', 'H-E-B', 'WINN-DIXIE', 'GIANT',
            'STOP & SHOP', 'SHOPRITE', 'MEIJER', 'HY-VEE',
            'GROCERY', 'SUPERMARKET', 'MARKET', 'FOOD STORE',
            'SPROUTS', 'FRESH MARKET', 'WHOLE FOODS MARKET', 'ALDI', 'LIDL'],
        'description': 'Grocery shopping, food purchases, household essentials'
    },
    'Dining': {
        'keywords': ['RESTAURANT', 'CAFE', 'COFFEE', 'STARBUCKS', 'DUNKIN',
            'MCDONALD', 'BURGER KING', 'WENDY', 'TACO BELL',
            'CHIPOTLE', 'PANERA', 'SUBWAY', 'DOMINO', 'PIZZA',
            'DINING', 'EAT', 'FOOD', 'LUNCH', 'DINNER', 'BREAKFAST',
            'GRUBHUB', 'DOORDASH', 'UBER EATS', 'POSTMATES',
            'BAKERY', 'DELI', 'FAST FOOD'],
        'description': 'Restaurant meals, coffee shops, fast food, food delivery'
    },
    'Healthcare': {
        'keywords': ['PHARMACY', 'CVS', 'WALGREENS', 'RITE AID',
            'DOCTOR', 'HOSPITAL', 'MEDICAL', 'HEALTH', 'CLINIC',
            'DENTIST', 'DENTAL', 'VISION', 'OPTICAL', 'EYE',
            'INSURANCE', 'HEALTH INSURANCE', 'MEDICAL BILL',
            'PRESCRIPTION', 'MEDICATION', 'DRUG STORE'],
        'description': 'Medical expenses, prescriptions, doctor visits, dental, vision'
    },
    'Home & Garden': {
        'keywords': ['HOME DEPOT', 'LOWE', "LOWE'S", 'HARDWARE', 'HOME IMPROVEMENT',
            'IKEA', 'WAYFAIR', 'OVERSTOCK', 'BED BATH',
            'FURNITURE', 'DECOR', 'GARDEN', 'LANDSCAPING', 'LAWN',
            'PAINT', 'TOOL', 'APPLIANCE'],
        'description': 'Home improvement, furniture, appliances, gardening'
    },
    'Shopping': {
        'keywords': ['AMAZON', 'EBAY', 'ETSY', 'ONLINE', 'SHOPPING',
            'TARGET', 'WALMART', 'DEPARTMENT STORE', 'RETAIL', 'STORE'],
        'description': 'General shopping and retail purchases'
    },
    'Transportation': {
        'keywords': ['METRO', 'SUBWAY', 'BUS', 'TRANSIT', 'PUBLIC TRANSPORT',
            'PARKING', 'TOLL', 'EZPASS', 'FASTRAK',
            'CAR WASH', 'AUTO REPAIR', 'MECHANIC', 'OIL CHANGE',
            'TIRE', 'AUTO PARTS', 'NAPA', 'AUTOZONE'],
        'description': 'Public transit, parking, tolls, car maintenance'
    }
}

def categorize_transaction(description: str, original_category: str = '') -> str:
    """Categorize a transaction based on description keywords."""
    desc_upper = str(description).upper()
    
    # Priority 1: Keyword match in description
    for category, info in CATEGORY_DEFINITIONS.items():
        for keyword in info['keywords']:
            if keyword in desc_upper:
                return category
    
    # Priority 2: Map original category if provided
    category_mapping = {
        'BILLS & UTILITIES': 'Utilities', 'UTILITIES': 'Utilities',
        'GROCERIES': 'Groceries', 'GROCERY': 'Groceries',
        'GAS': 'Utilities', 'GAS & FUEL': 'Utilities',
        'ENTERTAINMENT': 'Entertainment', 'TRAVEL': 'Travel',
        'SHOPPING': 'Shopping', 'DINING': 'Dining',
        'FOOD & DINING': 'Dining', 'HEALTHCARE': 'Healthcare',
        'MEDICAL': 'Healthcare', 'HOME & GARDEN': 'Home & Garden',
        'TRANSPORTATION': 'Transportation', 'AUTO & TRANSPORT': 'Transportation'
    }
    
    orig_upper = str(original_category).upper().strip()
    if orig_upper in category_mapping:
        return category_mapping[orig_upper]
    
    # Priority 3: Return original if valid, else 'Other'
    if original_category and original_category.strip() and original_category.lower() != 'nan':
        return original_category.strip().title()
    
    return 'Other'


# ============================================================================
# CORE DATA LOADING - NORMALIZE EACH FILE INDEPENDENTLY
# ============================================================================

def find_column(df_columns: list, target_names: list) -> str | None:
    """Find a column matching any of the target names (case-insensitive)."""
    df_cols_lower = {col.lower().strip(): col for col in df_columns}
    for target in target_names:
        if target.lower() in df_cols_lower:
            return df_cols_lower[target.lower()]
    return None


def clean_amount(value) -> float:
    """Convert amount string to float, handling currency symbols and parentheses."""
    if pd.isna(value):
        return 0.0
    val_str = str(value).strip()
    # Remove currency symbols and commas
    val_str = val_str.replace('$', '').replace(',', '').strip()
    # Handle parentheses as negative (accounting format)
    if val_str.startswith('(') and val_str.endswith(')'):
        val_str = '-' + val_str[1:-1]
    try:
        return float(val_str)
    except ValueError:
        return 0.0


def normalize_single_file(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    """
    Normalize a single dataframe to the target schema.
    This is the CRITICAL function that ensures all files have identical columns.
    """
    normalized = pd.DataFrame()
    
    # --- 1. Find and normalize DATE column ---
    date_col = find_column(df.columns, COLUMN_MAPPINGS['date'])
    if date_col:
        # Try multiple date formats
        date_formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y', 
                       '%m/%d/%y', '%Y/%m/%d', '%m/%d/%Y %H:%M:%S']
        parsed = None
        for fmt in date_formats:
            try:
                parsed = pd.to_datetime(df[date_col], format=fmt, errors='coerce')
                if parsed.notna().sum() > len(df) * 0.5:  # >50% success
                    break
            except:
                continue
        if parsed is None or parsed.isna().all():
            parsed = pd.to_datetime(df[date_col], errors='coerce')
        normalized['date'] = parsed
    else:
        # Try to infer date column from data patterns
        for col in df.columns:
            sample = df[col].dropna().head(10).astype(str)
            if sample.str.contains(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}').mean() > 0.5:
                normalized['date'] = pd.to_datetime(df[col], errors='coerce')
                break
        if 'date' not in normalized.columns:
            normalized['date'] = pd.NaT  # Fill with NaT if no date found
    
    # --- 2. Find and normalize DESCRIPTION column ---
    desc_col = find_column(df.columns, COLUMN_MAPPINGS['description'])
    if desc_col:
        normalized['description'] = df[desc_col].fillna('').astype(str)
    else:
        normalized['description'] = 'Unknown'
    
    # --- 3. Find and normalize AMOUNT column ---
    amount_col = find_column(df.columns, COLUMN_MAPPINGS['amount'])
    debit_col = find_column(df.columns, COLUMN_MAPPINGS['debit'])
    credit_col = find_column(df.columns, COLUMN_MAPPINGS['credit'])
    
    if amount_col:
        normalized['amount'] = df[amount_col].apply(clean_amount)
    elif debit_col and credit_col:
        # Debit/Credit format (Capital One, some banks)
        debits = df[debit_col].apply(clean_amount)
        credits = df[credit_col].apply(clean_amount)
        normalized['amount'] = credits - debits  # Credits positive, debits negative
    elif debit_col:
        normalized['amount'] = -df[debit_col].apply(clean_amount)  # Debits as negative
    elif credit_col:
        normalized['amount'] = df[credit_col].apply(clean_amount)
    else:
        # Try to find any numeric column that looks like amounts
        for col in df.columns:
            if col.lower() in ['date', 'description', 'category', 'type', 'memo']:
                continue
            sample = df[col].dropna().head(20)
            try:
                cleaned = sample.apply(clean_amount)
                if cleaned.abs().mean() > 0.01 and cleaned.abs().mean() < 1000000:
                    normalized['amount'] = df[col].apply(clean_amount)
                    break
            except:
                continue
        if 'amount' not in normalized.columns:
            normalized['amount'] = 0.0
    
    # --- 4. Find and normalize CATEGORY column ---
    cat_col = find_column(df.columns, COLUMN_MAPPINGS['category'])
    if cat_col:
        normalized['category'] = df[cat_col].fillna('Other').astype(str)
    else:
        normalized['category'] = 'Other'
    
    # --- 5. Add source file tracking ---
    normalized['source_file'] = filename
    
    # --- 6. Apply smart categorization ---
    normalized['processed_category'] = normalized.apply(
        lambda row: categorize_transaction(row['description'], row['category']), axis=1
    )
    
    return normalized


@st.cache_data(show_spinner=False)
def load_and_process_data(file_contents: list[tuple[str, bytes]]) -> pd.DataFrame | None:
    """
    Load and process multiple CSV files.
    
    CRITICAL: Each file is normalized INDEPENDENTLY before merging.
    This prevents schema conflicts from causing data loss.
    """
    normalized_dfs = []
    load_errors = []
    
    for filename, content in file_contents:
        try:
            file_io = io.BytesIO(content)
            
            # Try different encodings
            df = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    file_io.seek(0)
                    df = pd.read_csv(file_io, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None or df.empty:
                load_errors.append(f"⚠️ {filename}: Could not read file or file is empty")
                continue
            
            # Check if file has no headers (data in first row)
            first_row = df.iloc[0] if len(df) > 0 else None
            col_names = list(df.columns)
            
            # Heuristic: if column names look like dates or amounts, it's headerless
            looks_headerless = False
            for col in col_names[:3]:
                col_str = str(col)
                if '/' in col_str or col_str.replace('.', '').replace('-', '').isdigit():
                    looks_headerless = True
                    break
            
            if looks_headerless:
                file_io.seek(0)
                df = pd.read_csv(file_io, header=None, encoding=encoding)
                # Assign generic column names
                num_cols = len(df.columns)
                if num_cols >= 3:
                    df.columns = ['Transaction Date', 'Description', 'Amount'] + \
                                [f'Col_{i}' for i in range(3, num_cols)]
                elif num_cols == 2:
                    df.columns = ['Transaction Date', 'Amount']
                else:
                    df.columns = [f'Col_{i}' for i in range(num_cols)]
            
            # NORMALIZE THIS FILE to target schema
            normalized_df = normalize_single_file(df, filename)
            
            # Drop rows with invalid dates or zero amounts
            valid_rows = normalized_df['date'].notna() & (normalized_df['amount'] != 0)
            normalized_df = normalized_df[valid_rows]
            
            if len(normalized_df) > 0:
                normalized_dfs.append(normalized_df)
                st.success(f"✅ {filename}: Loaded {len(normalized_df)} transactions")
            else:
                load_errors.append(f"⚠️ {filename}: No valid transactions found")
                
        except Exception as e:
            load_errors.append(f"❌ {filename}: {str(e)}")
    
    # Show any errors
    for error in load_errors:
        st.warning(error)
    
    if not normalized_dfs:
        st.error("❌ No valid data could be loaded from any file.")
        return None
    
    # MERGE - All dataframes now have identical columns
    combined = pd.concat(normalized_dfs, ignore_index=True)
    
    # Add derived columns for analysis
    combined['year'] = combined['date'].dt.year
    combined['month'] = combined['date'].dt.month
    combined['month_name'] = combined['date'].dt.strftime('%B')
    combined['is_income'] = combined['amount'] > 0
    combined['abs_amount'] = combined['amount'].abs()
    
    return combined


# ============================================================================
# VISUALIZATION
# ============================================================================

def create_monthly_expense_chart(data: pd.DataFrame, year: int):
    """Create stacked bar chart for monthly expenses by category."""
    expense_data = data[(data['year'] == year) & (~data['is_income'])].copy()
    
    if expense_data.empty:
        st.warning("No expense data available for the selected year.")
        return None
    
    monthly = expense_data.groupby(['month', 'month_name', 'processed_category'])['abs_amount'].sum().reset_index()
    monthly = monthly.sort_values('month')
    
    fig = px.bar(
        monthly, x='month_name', y='abs_amount', color='processed_category',
        title='Monthly Expenses by Category',
        labels={'month_name': 'Month', 'abs_amount': 'Amount ($)', 'processed_category': 'Category'},
        height=500, color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(barmode='stack', hovermode='x unified')
    fig.update_yaxes(tickprefix='$', tickformat=',.0f')
    return fig


def create_category_pie_chart(data: pd.DataFrame, year: int):
    """Create pie chart for expense distribution."""
    expense_data = data[(data['year'] == year) & (~data['is_income'])]
    category_totals = expense_data.groupby('processed_category')['abs_amount'].sum().sort_values(ascending=False)
    
    if category_totals.empty:
        return None
    
    fig = px.pie(
        values=category_totals.values, names=category_totals.index,
        title='Expense Distribution by Category', hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    st.title("💰 Jia's Family Yearly Finance Summary")
    st.markdown("---")
    
    # Sidebar - File Upload
    with st.sidebar:
        st.header("📁 Upload Bank Statements")
        
        uploaded_files = st.file_uploader(
            "Upload CSV files", type=['csv'], accept_multiple_files=True,
            help="Upload one or more bank statement CSV files"
        )
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.markdown("""
        This app analyzes bank statements to provide:
        - Total income and expenses
        - Monthly spending breakdown
        - Categorized transactions
        - **Handles multiple CSV formats automatically**
        """)
    
    if not uploaded_files:
        st.info("👆 Please upload one or more CSV files to get started.")
        with st.expander("ℹ️ Supported CSV Formats"):
            st.markdown("""
            **The app automatically handles various bank formats:**
            - Chase, Wells Fargo, Bank of America, Capital One, Amex, etc.
            - Files with different column names (Date vs Transaction Date, etc.)
            - Debit/Credit columns or single Amount columns
            - Files with or without headers
            
            **Columns are automatically mapped to:**
            - `date` - Transaction date
            - `description` - Transaction description  
            - `amount` - Transaction amount
            - `category` - Category (optional, will be auto-categorized)
            """)
        return
    
    # Read file contents for caching
    file_contents = []
    for f in uploaded_files:
        content = f.read()
        file_contents.append((f.name, content))
        f.seek(0)  # Reset for potential re-read
    
    # Load and process data
    with st.spinner("Processing files..."):
        data = load_and_process_data(file_contents)
    
    if data is None:
        return
    
    st.success(f"📊 **Total: {len(data)} transactions loaded from {len(uploaded_files)} file(s)**")
    
    # Year filter
    with st.sidebar:
        st.markdown("---")
        st.header("🗓️ Filter by Year")
        years = sorted(data['year'].dropna().unique().astype(int))
        if not years:
            st.error("No valid years found")
            return
        selected_year = st.selectbox("Select Year", years, index=len(years)-1)
    
    # Calculate metrics
    year_data = data[data['year'] == selected_year]
    total_income = year_data[year_data['is_income']]['amount'].sum()
    total_expenses = year_data[~year_data['is_income']]['abs_amount'].sum()
    net_savings = total_income - total_expenses
    
    # Display metrics
    st.header(f"📈 {selected_year} Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Total Income", f"${total_income:,.2f}")
    col2.metric("💸 Total Expenses", f"${total_expenses:,.2f}")
    col3.metric("💰 Net Savings", f"${net_savings:,.2f}", 
                delta_color="normal" if net_savings >= 0 else "inverse")
    
    st.markdown("---")
    
    # Monthly expense chart
    st.header("📊 Monthly Expense Breakdown")
    fig = create_monthly_expense_chart(data, selected_year)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Category breakdown
    st.header("🔍 Category Breakdown")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        pie_fig = create_category_pie_chart(data, selected_year)
        if pie_fig:
            st.plotly_chart(pie_fig, use_container_width=True)
    
    with col2:
        st.subheader("Top Categories")
        expense_data = data[(data['year'] == selected_year) & (~data['is_income'])]
        category_totals = expense_data.groupby('processed_category')['abs_amount'].sum().sort_values(ascending=False)
        total = category_totals.sum()
        
        for i, (cat, amt) in enumerate(category_totals.head(10).items(), 1):
            pct = (amt / total * 100) if total > 0 else 0
            st.markdown(f"**{i}. {cat}**")
            st.caption(f"${amt:,.2f} ({pct:.1f}%)")
    
    # Source file breakdown
    st.markdown("---")
    with st.expander("📂 Transactions by Source File"):
        source_summary = data[data['year'] == selected_year].groupby('source_file').agg(
            transactions=('amount', 'count'),
            total_amount=('amount', 'sum')
        ).reset_index()
        st.dataframe(source_summary, use_container_width=True)
    
    # Raw data view
    with st.expander("🔎 View Raw Transaction Data"):
        display_cols = ['date', 'description', 'processed_category', 'amount', 'source_file']
        st.dataframe(
            year_data[display_cols].sort_values('date', ascending=False),
            use_container_width=True, height=400
        )


if __name__ == "__main__":
    main()