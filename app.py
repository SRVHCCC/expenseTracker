from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import func

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    expenses = db.relationship('Expense', backref='user', lazy=True)
    earnings = db.relationship('Earning', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Earning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validate email
        try:
            # Validate and normalize the email
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            flash('Invalid email address')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    earnings = Earning.query.filter_by(user_id=current_user.id).all()
    
    total_expense = sum(expense.amount for expense in expenses)
    total_earning = sum(earning.amount for earning in earnings)
    ratio = (total_earning / total_expense) if total_expense > 0 else 0
    
    return render_template('dashboard.html',
                         total_expense=total_expense,
                         total_earning=total_earning,
                         ratio=ratio,
                         expenses=expenses,
                         now=datetime.now())

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        
        expense = Expense(amount=amount, description=description, date=date, user_id=current_user.id)
        db.session.add(expense)
        db.session.commit()
        
        flash('Expense added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('add_expense.html')

@app.route('/add_earning', methods=['GET', 'POST'])
@login_required
def add_earning():
    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        
        earning = Earning(amount=amount, description=description, date=date, user_id=current_user.id)
        db.session.add(earning)
        db.session.commit()
        
        flash('Earning added successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('add_earning.html')

@app.route('/expenses')
@login_required
def expenses():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Expense.query.filter_by(user_id=current_user.id)
    
    if start_date:
        query = query.filter(Expense.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Expense.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    expenses = query.order_by(Expense.date.desc()).all()
    return render_template('expenses.html', expenses=expenses)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    # Ensure user can only delete their own expenses
    if expense.user_id != current_user.id:
        flash('You are not authorized to delete this expense')
        return redirect(url_for('expenses'))
    
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!')
    return redirect(url_for('expenses'))

@app.route('/visualize')
@login_required
def visualize():
    # Get last 6 months of data
    six_months_ago = datetime.now() - timedelta(days=180)
    
    # Get monthly expenses
    expenses = db.session.query(
        func.strftime('%Y-%m', Expense.date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.date >= six_months_ago
    ).group_by('month').order_by('month').all()
    
    # Get monthly earnings
    earnings = db.session.query(
        func.strftime('%Y-%m', Earning.date).label('month'),
        func.sum(Earning.amount).label('total')
    ).filter(
        Earning.user_id == current_user.id,
        Earning.date >= six_months_ago
    ).group_by('month').order_by('month').all()
    
    # Prepare data for charts
    months = [e.month for e in expenses]
    expense_data = [float(e.total) for e in expenses]
    earning_data = [float(e.total) for e in earnings]
    
    return render_template('visualize.html', 
                         months=months,
                         expense_data=expense_data,
                         earning_data=earning_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
