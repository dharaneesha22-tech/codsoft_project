# app.py

from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

app = Flask(__name__)

app.secret_key = "secretkey"

# ======================================================
# DATABASE
# ======================================================

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = conn.cursor()

# USERS TABLE

cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    password TEXT

)

""")

# HISTORY TABLE

cursor.execute("""

CREATE TABLE IF NOT EXISTS history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    message TEXT,

    result TEXT,

    probability REAL,

    time TEXT

)

""")

conn.commit()

# ======================================================
# DATASET
# ======================================================

data = {

    "message":[

        "Congratulations you won lottery",
        "Claim free iphone now",
        "Win money instantly",
        "Limited offer click now",
        "Free recharge available",
        "Urgent your bank account blocked",

        "Hello how are you",
        "Meeting at 5 PM",
        "Dinner tonight",
        "Project submission tomorrow",
        "Can we talk later",
        "Good morning friend"

    ],

    "label":[

        "spam",
        "spam",
        "spam",
        "spam",
        "spam",
        "spam",

        "ham",
        "ham",
        "ham",
        "ham",
        "ham",
        "ham"

    ]
}

df = pd.DataFrame(data)

df['label_num'] = df.label.map({

    'ham':0,
    'spam':1

})

# ======================================================
# MACHINE LEARNING
# ======================================================

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(df['message'])

y = df['label_num']

model = MultinomialNB()

model.fit(X, y)

# ======================================================
# HOME
# ======================================================

@app.route('/')
def home():

    return render_template('login.html')

# ======================================================
# REGISTER PAGE
# ======================================================

@app.route('/register')
def register():

    return render_template('register.html')

# ======================================================
# REGISTER USER
# ======================================================

@app.route('/register_user', methods=['POST'])
def register_user():

    username = request.form['username']

    password = request.form['password']

    cursor.execute(

        "SELECT * FROM users WHERE username=?",

        (username,)

    )

    existing_user = cursor.fetchone()

    if existing_user:

        return render_template(

            'register.html',

            error="Username Already Exists"

        )

    cursor.execute("""

    INSERT INTO users
    (username, password)

    VALUES (?, ?)

    """, (

        username,
        password

    ))

    conn.commit()

    return redirect('/')

# ======================================================
# LOGIN
# ======================================================

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']

    password = request.form['password']

    cursor.execute("""

    SELECT * FROM users

    WHERE username=? AND password=?

    """, (

        username,
        password

    ))

    user = cursor.fetchone()

    if user:

        session['user'] = username

        return redirect('/dashboard')

    else:

        return render_template(

            'login.html',

            error="Invalid Username or Password"

        )

# ======================================================
# DASHBOARD
# ======================================================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:

        return redirect('/')

    username = session['user']

    cursor.execute("""

    SELECT * FROM history
    WHERE username=?
    ORDER BY id DESC

    """, (

        username,

    ))

    history = cursor.fetchall()

    total = len(history)

    spam = len([

        item for item in history
        if item[3] == "SPAM"

    ])

    safe = len([

        item for item in history
        if item[3] == "SAFE"

    ])

    return render_template(

        'dashboard.html',

        username=username,

        history=history,

        total=total,

        spam=spam,

        safe=safe

    )

# ======================================================
# PREDICT
# ======================================================

@app.route('/predict', methods=['POST'])
def predict():

    if 'user' not in session:

        return redirect('/')

    username = session['user']

    message = request.form['message']

    transformed = vectorizer.transform([message])

    prediction = model.predict(transformed)[0]

    probability = model.predict_proba(transformed)[0]

    spam_probability = round(
        probability[1] * 100,
        2
    )

    if prediction == 1:

        result = "SPAM"

    else:

        result = "SAFE"

    current_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    cursor.execute("""

    INSERT INTO history
    (username, message, result, probability, time)

    VALUES (?, ?, ?, ?, ?)

    """, (

        username,
        message,
        result,
        spam_probability,
        current_time

    ))

    conn.commit()

    return redirect('/dashboard')

# ======================================================
# LOGOUT
# ======================================================

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/')

# ======================================================
# RUN
# ======================================================

if __name__ == '__main__':

    app.run(debug=True)