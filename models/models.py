from main.extensions import db

class LiveSession(db.Model):
    __tablename__ = "live_sessions"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    __table_args__ = {'extend_existing': True}

    def __init__(self, session_id, data, created_at):
        self.session_id = session_id
        self.data = data
        self.created_at = created_at

    def __repr__(self):
        return f"<LiveSession {self.session_id}>"
    

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    __table_args__ = {'extend_existing': True}

    def __init__(self, username, created_at):
        self.username = username
        self.created_at = created_at

    def __repr__(self):
        return f"<LiveSession {self.username}>"