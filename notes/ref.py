from flask import Flask, session, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ensure you have a secret key for Flask sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sessions.db'  # Example, use a real database URI
db = SQLAlchemy(app)

class UserSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True)
    search_data = db.Column(db.Text)

@app.route('/search', methods=['POST'])
def search():
    # Get search query
    search_query = request.form['search_query']

    # Use session_id to store the search data, ensuring no interference between users
    session_id = session.get('user_id')  # Or use session.sid directly for unique session
    if not session_id:
        session_id = str(uuid.uuid4())  # Generate a unique session ID for the user
        session['user_id'] = session_id

    # Store search query in database with the session ID as the key
    user_search = UserSearch.query.filter_by(session_id=session_id).first()
    if user_search:
        user_search.search_data = search_query
    else:
        user_search = UserSearch(session_id=session_id, search_data=search_query)
        db.session.add(user_search)
    
    db.session.commit()

    return redirect(url_for('search_results'))

@app.route('/search_results')
def search_results():
    session_id = session.get('user_id')
    if session_id:
        user_search = UserSearch.query.filter_by(session_id=session_id).first()
        if user_search:
            return render_template('results.html', search_data=user_search.search_data)
    
    return 'No search data available.'

if __name__ == '__main__':
    db.create_all()  # Create the database if it doesn't exist
    app.run(debug=True)
