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

def categorize_transaction(row):
    """
    Categorize transactions based on priority:
    1. Keyword match in 'Description'
    2. Use existing 'Category' column with mapping
    3. Fallback to original category or 'Other'
    """
    description = str(row.get('Description', '')).upper()
    original_category = str(row.get('Category', 'Other'))
    
    # Priority 1: Keyword Match in Description
    keyword_categories = {
        'Utilities': ['ELECTRIC', 'WATER', 'GAS', 'INTERNET', 'SHELL', 'PHONE'],
        'Entertainment': ['NETFLIX', 'SPOTIFY', 'CINEMA', 'MOVIE', 'DISNEY'],
        'Travel': ['HOTEL', 'AIRLINE', 'UBER', 'LYFT', 'DELTA', 'BOOKING'],
        'Clothes, shoes': ['ZARA', 'NIKE', 'UNIQLO', 'MACY', 'H&M', 'ADIDAS'],
        'Property Tax': ['TAX', 'COUNTY'],
        'Groceries': ['WHOLE FOODS', 'TRADER JOES', 'COSTCO', 'KROGER', 'SAFEWAY']
    }
    
    # Check for keyword matches
    for category, keywords in keyword_categories.items():
        for keyword in keywords:
            if keyword in description:
                return category
    
    # Priority 2: Map existing Category column
    category_mapping = {
        'Bills & Utilities': 'Utilities',
        'Groceries': 'Groceries',
        'Gas': 'Utilities'
    }
    
    if original_category in category_mapping:
        return category_mapping[original_category]
    
    # Priority 3: Fallback to original category
    return original_category if original_category else 'Other'


# ============================================================================
# DATA PROCESSING
# ============================================================================

def load_and_process_data(uploaded_files):
    """
    Load CSV files, process and categorize transactions.
    Returns processed DataFrame or None if error.
    """
    try:
        # Load all uploaded files
        dfs = []
        for file in uploaded_files:
            df = pd.read_csv(file)
            dfs.append(df)
        
        # Concatenate all dataframes
        data = pd.concat(dfs, ignore_index=True)
        
        # Validate required columns
        required_columns = ['Transaction Date', 'Amount']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
            st.info("Expected columns: Transaction Date, Post Date, Description, Category, Type, Amount, Memo")
            return None
        
        # Parse Transaction Date
        data['Transaction Date'] = pd.to_datetime(data['Transaction Date'], errors='coerce')
        
        # Drop rows with invalid dates
        data = data.dropna(subset=['Transaction Date'])
        
        # Extract Year and Month
        data['Year'] = data['Transaction Date'].dt.year
        data['Month'] = data['Transaction Date'].dt.month
        data['Month_Name'] = data['Transaction Date'].dt.strftime('%B')
        
        # Apply categorization
        data['Processed_Category'] = data.apply(categorize_transaction, axis=1)
        
        # Separate Income and Expenses
        data['Is_Income'] = data['Amount'] > 0
        data['Abs_Amount'] = data['Amount'].abs()
        
        return data
    
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}")
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
        This app analyzes Chase bank statements to provide:
        - Total income and expenses
        - Monthly spending breakdown
        - Categorized transactions
        """)
    
    # Main Content
    if not uploaded_files:
        st.info("👆 Please upload one or more CSV files to get started.")
        
        # Show example of expected format
        with st.expander("ℹ️ Expected CSV Format"):
            st.markdown("""
            Your Chase CSV should contain these columns:
            - **Transaction Date**: Date of transaction
            - **Post Date**: Date transaction posted
            - **Description**: Transaction description
            - **Category**: Transaction category
            - **Type**: Transaction type
            - **Amount**: Transaction amount (positive for income, negative for expenses)
            - **Memo**: Additional notes
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
    
    # Raw data view (optional)
    with st.expander("🔎 View Raw Transaction Data"):
        year_data = data[data['Year'] == selected_year].sort_values('Transaction Date', ascending=False)
        display_columns = ['Transaction Date', 'Description', 'Processed_Category', 'Amount', 'Type']
        st.dataframe(
            year_data[display_columns],
            use_container_width=True,
            height=400
        )


if __name__ == "__main__":
    main()

