# Expense Tracker Application

A web-based expense tracking application built with Flask, MySQL, and Jinja2 templating.

## Features
- User Authentication (Signup/Login)
- Add and Manage Expenses
- View Expense List with Date Range Filtering
- Dashboard with:
  - Total Expenses
  - Current Expenses
  - Total Earnings
  - Earning to Expense Ratio

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MySQL database:
- Create a database named 'expense_tracker'
- Update the database configuration in .env file

4. Run the application:
```bash
python app.py
```

5. Access the application at http://localhost:5000

## Environment Variables
Create a .env file with the following variables:
```
SECRET_KEY=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DB=expense_tracker
``` 