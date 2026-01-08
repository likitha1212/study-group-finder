from flask_socketio import SocketIO
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"
socketio = SocketIO(app)

def get_db():
    return sqlite3.connect("database.db")

socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM groups")
    groups = cur.fetchall()
    conn.close()
    return render_template("index.html", groups=groups)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (u,p))
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = cur.fetchone()
        conn.close()
        if user:
            session["user"] = u
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/create_group", methods=["GET","POST"])
def create_group():
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form["description"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO groups (name,description) VALUES (?,?)",(name,desc))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("create_group.html")

@app.route("/group/<int:group_id>")
def group_chat(group_id):
    return render_template("group_chat.html", group_id=group_id, user=session["user"])

@socketio.on("join")
def on_join(data):
    join_room(data["room"])

@socketio.on("send_message")
def handle_message(data):
    emit("receive_message", data, room=data["room"])

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)

