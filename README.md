# Jia's Family Yearly Finance Summary 💰

A Streamlit application for analyzing and visualizing family finances from Chase bank statements.

## Features

- 📁 **Multi-file Upload**: Upload one or multiple Chase CSV bank statements
- 💵 **Financial Metrics**: View total income, expenses, and net savings
- 📊 **Visual Analytics**: 
  - Monthly expense breakdown (stacked bar chart)
  - Category distribution (pie chart)
  - Top spending categories
- 🏷️ **Smart Categorization**: Automatically categorizes transactions based on:
  - Keyword matching in transaction descriptions
  - Mapping of existing Chase categories
  - Custom categories for better insights

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Usage

1. **Run the application**:
```bash
streamlit run app.py
```

2. **Upload your Chase CSV files** using the sidebar file uploader

3. **Select a year** to analyze from the dropdown

4. **Explore your financial data** through interactive charts and metrics

## Expected CSV Format

Your Chase bank statement CSV should contain these columns:
- `Transaction Date`: Date of transaction
- `Post Date`: Date transaction posted
- `Description`: Transaction description
- `Category`: Transaction category (from Chase)
- `Type`: Transaction type
- `Amount`: Transaction amount (positive for income, negative for expenses)
- `Memo`: Additional notes

## Categories

The app intelligently categorizes transactions into:
- **Utilities**: Electric, Water, Gas, Internet, Phone, Shell
- **Entertainment**: Netflix, Spotify, Cinema, Movie, Disney
- **Travel**: Hotel, Airline, Uber, Lyft, Delta, Booking
- **Clothes, shoes**: Zara, Nike, Uniqlo, Macy's, H&M, Adidas
- **Property Tax**: Tax, County
- **Groceries**: Whole Foods, Trader Joe's, Costco, Kroger, Safeway
- **Other**: Any uncategorized transactions

## Tech Stack

- **Python 3.8+**
- **Streamlit**: Web application framework
- **Pandas**: Data processing and analysis
- **Plotly Express**: Interactive visualizations

## Screenshots

The application displays:
1. Total Income, Total Expenses, and Net Savings metrics
2. Monthly expense breakdown with stacked bars by category
3. Pie chart showing expense distribution
4. Top spending categories list
5. Raw transaction data viewer

## Customization

You can easily customize the categorization logic in the `categorize_transaction()` function by:
- Adding new categories
- Adding new keywords for existing categories
- Modifying the category mapping

## License

This project is open source and available for personal use.

## Deployment to Streamlit Cloud

This app can be easily deployed to Streamlit Cloud for free:

### Prerequisites
- A GitHub account
- Your code pushed to a GitHub repository

### Steps to Deploy

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Finance summary app"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository and branch
   - Set the main file path to: `app.py`
   - Click "Deploy"

3. **Your app will be live** at: `https://YOUR_APP_NAME.streamlit.app`

### Important Notes for Deployment
- ✅ The `requirements.txt` file is already configured
- ✅ The `.streamlit/config.toml` file is included for proper configuration
- ✅ CSV files are excluded from git (via `.gitignore`) for privacy
- ✅ Users can upload their own CSV files through the web interface

## Support

For issues or questions, please create an issue in the repository.

