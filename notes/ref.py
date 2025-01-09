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





#########################

let isLocked = false;  // Track the lock state

function getLockedFirmware() {
    let firmwareNameToUpdate = "";

    // If button is already locked, return
    if (isLocked) {
        return firmwareNameToUpdate;
    }

    let pressTimer;

    // Event listener for mouse press (mousedown)
    btnLockFw.addEventListener("mousedown", function() {
        // Add animation class when the button is pressed
        btnLockFw.classList.add("press-animation");

        // Start the 2-second press timer
        pressTimer = setTimeout(function() {
            // Change the text content after 2 seconds
            btnLockFw.textContent = "Lock";
            isLocked = true;  // Button is now locked
            // Remove the animation class after the press action is completed
            btnLockFw.classList.remove("press-animation");
        }, 2000); // Press duration: 2000 ms (2 seconds)
    });

    // Event listener for mouse release (mouseup)
    btnLockFw.addEventListener("mouseup", function() {
        // Clear the press timer if the button is released before 2 seconds
        clearTimeout(pressTimer);

        // If the button is not locked yet, set the text to "Unlock" when mouse is released
        if (!isLocked) {
            btnLockFw.textContent = "Unlock";
        }

        // Remove the animation class when the button is released
        btnLockFw.classList.remove("press-animation");
    });

    // Event listener for mouse leave
    btnLockFw.addEventListener("mouseleave", function() {
        // Clear the press timer if the mouse leaves the button before 2 seconds
        clearTimeout(pressTimer);

        // If the button is not locked yet, set the text to "Unlock" when mouse leaves
        if (!isLocked) {
            btnLockFw.textContent = "Unlock";
        }

        // Remove the animation class when the mouse leaves the button
        btnLockFw.classList.remove("press-animation");
    });

    return firmwareNameToUpdate;
}
