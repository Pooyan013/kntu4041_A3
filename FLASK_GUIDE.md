# Flask Learning Guide

This guide provides detailed explanations and examples for learning Flask from scratch.

---

## Table of Contents

1. [What is Flask?](#what-is-flask)
2. [Installation](#installation)
3. [Basic Flask Application](#basic-flask-application)
4. [Routing](#routing)
5. [Templates](#templates)
6. [Static Files](#static-files)
7. [Handling Forms](#handling-forms)
8. [Cookies](#cookies)
9. [Redirects](#redirects)
10. [Complete Example: Login System](#complete-example-login-system)

---

## What is Flask?

Flask is a lightweight Python web framework that allows you to build web applications quickly. It's called a "microframework" because it doesn't require particular tools or libraries, but you can add extensions as needed.

**Key Features:**

- Simple and flexible
- Easy to learn
- Great for small to medium applications
- Extensive documentation

---

## Installation

### Step 1: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Flask

```bash
pip install Flask
```

### Step 3: Verify Installation

```python
import flask
print(flask.__version__)
```

---

## Basic Flask Application

### Minimal Example

Create a file `app.py`:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Hello World!</h1>'

if __name__ == '__main__':
    app.run(debug=True)
```

**Run it:**

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

**Explanation:**

- `Flask(__name__)` - Creates Flask application instance
- `@app.route('/')` - Decorator that defines URL route
- `def home()` - Function that handles the request
- `return` - Returns response to browser
- `app.run(debug=True)` - Starts development server (debug mode shows errors)

---

## Routing

### Basic Routes

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Home Page'

@app.route('/about')
def about():
    return 'About Page'

@app.route('/user/<username>')
def show_user(username):
    return f'User: {username}'
```

**URL Examples:**

- `http://127.0.0.1:5000/` → "Home Page"
- `http://127.0.0.1:5000/about` → "About Page"
- `http://127.0.0.1:5000/user/john` → "User: john"

### HTTP Methods (GET, POST)

```python
from flask import Flask, request

app = Flask(__name__)

# Default is GET only
@app.route('/login', methods=['GET'])
def login_form():
    return '''
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username">
        <input type="password" name="password" placeholder="Password">
        <button type="submit">Login</button>
    </form>
    '''

# Handle POST request
@app.route('/login', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']
    return f'Username: {username}, Password: {password}'

# Handle both GET and POST
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle form submission
        username = request.form.get('username')
        return f'Registered: {username}'
    else:
        # Show registration form
        return '''
        <form method="POST">
            <input type="text" name="username" placeholder="Username">
            <button type="submit">Register</button>
        </form>
        '''
```

**Key Points:**

- `methods=['GET', 'POST']` - Specifies which HTTP methods the route accepts
- `request.method` - Check which method was used
- `request.form` - Access form data from POST requests
- `request.form.get('key')` - Safer way to get form data (returns None if missing)

---

## Templates

Instead of returning HTML strings, use template files.

### Project Structure

```
myapp/
├── app.py
└── templates/
    └── index.html
```

### Basic Template

**templates/index.html:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>My App</title>
  </head>
  <body>
    <h1>Welcome!</h1>
    <p>Hello, {{ name }}!</p>
  </body>
</html>
```

**app.py:**

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', name='John')
```

**Explanation:**

- `templates/` folder - Flask automatically looks here for HTML files
- `render_template('file.html', variable=value)` - Renders template with variables
- `{{ variable }}` - Jinja2 syntax to display variables in templates

### Template with Conditions and Loops

**templates/users.html:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Users</title>
  </head>
  <body>
    <h1>Users List</h1>
    {% if users %}
    <ul>
      {% for user in users %}
      <li>{{ user }}</li>
      {% endfor %}
    </ul>
    {% else %}
    <p>No users found.</p>
    {% endif %}
  </body>
</html>
```

**app.py:**

```python
@app.route('/users')
def show_users():
    users = ['Alice', 'Bob', 'Charlie']
    return render_template('users.html', users=users)
```

**Jinja2 Syntax:**

- `{{ variable }}` - Display variable
- `{% if condition %}` - Conditional statements
- `{% for item in list %}` - Loops
- `{% endif %}` - End if
- `{% endfor %}` - End for

### Template Inheritance

**templates/base.html:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}My App{% endblock %}</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='style.css') }}"
    />
  </head>
  <body>
    <nav>
      <a href="/">Home</a>
      <a href="/about">About</a>
    </nav>

    {% block content %}{% endblock %}

    <footer>© 2024 My App</footer>
  </body>
</html>
```

**templates/index.html:**

```html
{% extends "base.html" %} {% block title %}Home - My App{% endblock %} {% block
content %}
<h1>Welcome to Home Page</h1>
<p>This is the home page content.</p>
{% endblock %}
```

**Explanation:**

- `{% extends "base.html" %}` - Inherit from base template
- `{% block name %}` - Define a block that can be overridden
- `url_for('static', filename='style.css')` - Generate URL for static files

---

## Static Files

Static files (CSS, JavaScript, images) go in the `static/` folder.

### Project Structure

```
myapp/
├── app.py
├── templates/
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

### Using Static Files

**templates/index.html:**

```html
<!DOCTYPE html>
<html>
  <head>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/style.css') }}"
    />
  </head>
  <body>
    <h1>Styled Page</h1>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
  </body>
</html>
```

**static/css/style.css:**

```css
body {
  font-family: Arial, sans-serif;
  background-color: #f0f0f0;
}

h1 {
  color: #333;
}
```

---

## Handling Forms

### Complete Form Example

**templates/register.html:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Register</title>
  </head>
  <body>
    <h1>Register</h1>

    {% if error %}
    <p style="color: red;">{{ error }}</p>
    {% endif %}

    <form method="POST" action="/register">
      <label>Username:</label>
      <input type="text" name="username" required /><br /><br />

      <label>Email:</label>
      <input type="email" name="email" required /><br /><br />

      <label>Password:</label>
      <input type="password" name="password" required /><br /><br />

      <label>Confirm Password:</label>
      <input type="password" name="confirm_password" required /><br /><br />

      <button type="submit">Register</button>
    </form>

    <a href="/login">Already have an account? Login</a>
  </body>
</html>
```

**app.py:**

```python
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Store users (in real app, use database)
users = {}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not username or not email or not password:
            return render_template('register.html', error='All fields required')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        if username in users:
            return render_template('register.html', error='Username already exists')

        # Store user (in real app, hash password!)
        users[username] = {
            'email': email,
            'password': password  # DON'T DO THIS IN PRODUCTION!
        }

        return redirect(url_for('login'))

    return render_template('register.html')
```

---

## Cookies

Cookies are small pieces of data stored in the user's browser.

### Setting Cookies

```python
from flask import Flask, make_response, redirect

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    # Validate credentials (simplified)
    username = request.form.get('username')

    if username == 'admin':  # Simple check
        # Create response
        response = make_response(redirect('/map'))

        # Set cookie
        response.set_cookie(
            'auth_token',
            value='logged_in',
            max_age=3600,      # Cookie expires in 1 hour (seconds)
            httponly=True,     # JavaScript cannot access (security)
            secure=False       # Set True for HTTPS only
        )

        return response
    else:
        return 'Invalid credentials'
```

### Reading Cookies

```python
from flask import Flask, request, redirect

app = Flask(__name__)

@app.route('/map')
def map():
    # Check if user is logged in
    auth_token = request.cookies.get('auth_token')

    if auth_token == 'logged_in':
        return render_template('map.html')
    else:
        return redirect('/login')
```

### Clearing Cookies (Logout)

```python
@app.route('/logout')
def logout():
    response = make_response(redirect('/login'))
    response.set_cookie('auth_token', '', expires=0)  # Delete cookie
    return response
```

**Cookie Parameters:**

- `value` - Cookie value
- `max_age` - Expiration time in seconds
- `httponly=True` - Prevents JavaScript access (security)
- `secure=True` - Only send over HTTPS
- `expires=0` - Delete cookie immediately

---

## Redirects

Redirect users to different pages.

```python
from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    # Check if logged in
    auth_token = request.cookies.get('auth_token')

    if auth_token:
        return redirect('/map')  # Redirect to map
    else:
        return redirect('/login')  # Redirect to login

# Using url_for (better practice)
@app.route('/register')
def register():
    # ... registration logic ...
    return redirect(url_for('login'))  # Redirects to login route
```

**Methods:**

- `redirect('/path')` - Redirect to URL path
- `redirect(url_for('function_name'))` - Redirect using function name (better)

---

## Password Hashing

**NEVER store plain text passwords!**

### Using Werkzeug (comes with Flask)

```python
from werkzeug.security import generate_password_hash, check_password_hash

# When registering user
password = request.form.get('password')
hashed_password = generate_password_hash(password)

# Store hashed_password in database/file

# When logging in
stored_hash = users[username]['password']  # Get from storage
if check_password_hash(stored_hash, entered_password):
    # Password correct
    return redirect('/map')
else:
    # Password incorrect
    return 'Invalid password'
```

**Example:**

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hash a password
password = "mypassword123"
hashed = generate_password_hash(password)
print(hashed)  # Something like: pbkdf2:sha256:260000$...

# Check password
is_correct = check_password_hash(hashed, "mypassword123")  # True
is_wrong = check_password_hash(hashed, "wrongpassword")    # False
```

---

## Complete Example: Login System

Here's a complete working example:

### Project Structure

```
login_app/
├── app.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── map.html
└── static/
    └── css/
        └── style.css
```

### app.py

```python
from flask import Flask, render_template, request, redirect, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)

# File to store users
USERS_FILE = 'users.json'

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def is_logged_in():
    """Check if user is logged in"""
    auth_token = request.cookies.get('auth_token')
    return auth_token == 'authenticated'

@app.route('/')
def home():
    if is_logged_in():
        return redirect(url_for('map'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()

        if username in users:
            # Check password
            if check_password_hash(users[username]['password'], password):
                # Login successful - set cookie
                response = make_response(redirect(url_for('map')))
                response.set_cookie('auth_token', 'authenticated', max_age=3600, httponly=True)
                return response

        # Login failed
        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not username or not email or not password:
            return render_template('register.html', error='All fields required')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        users = load_users()

        if username in users:
            return render_template('register.html', error='Username already exists')

        # Hash password and save user
        hashed_password = generate_password_hash(password)
        users[username] = {
            'email': email,
            'password': hashed_password
        }
        save_users(users)

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/map')
def map():
    if not is_logged_in():
        return redirect(url_for('login'))

    return render_template('map.html')

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie('auth_token', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(debug=True)
```

### templates/base.html

```html
<!DOCTYPE html>
<html>
  <head>
    <title>{% block title %}My App{% endblock %}</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/style.css') }}"
    />
  </head>
  <body>
    <nav>
      <h1>WebGIS App</h1>
      {% if request.cookies.get('auth_token') %}
      <a href="{{ url_for('logout') }}">Logout</a>
      {% endif %}
    </nav>

    {% block content %}{% endblock %}
  </body>
</html>
```

### templates/login.html

```html
{% extends "base.html" %} {% block title %}Login{% endblock %} {% block content
%}
<div class="form-container">
  <h2>Login</h2>

  {% if error %}
  <p class="error">{{ error }}</p>
  {% endif %}

  <form method="POST">
    <label>Username:</label>
    <input type="text" name="username" required />

    <label>Password:</label>
    <input type="password" name="password" required />

    <button type="submit">Login</button>
  </form>

  <p>Don't have an account? <a href="{{ url_for('register') }}">Register</a></p>
</div>
{% endblock %}
```

### templates/register.html

```html
{% extends "base.html" %} {% block title %}Register{% endblock %} {% block
content %}
<div class="form-container">
  <h2>Register</h2>

  {% if error %}
  <p class="error">{{ error }}</p>
  {% endif %}

  <form method="POST">
    <label>Username:</label>
    <input type="text" name="username" required />

    <label>Email:</label>
    <input type="email" name="email" required />

    <label>Password:</label>
    <input type="password" name="password" required />

    <label>Confirm Password:</label>
    <input type="password" name="confirm_password" required />

    <button type="submit">Register</button>
  </form>

  <p>Already have an account? <a href="{{ url_for('login') }}">Login</a></p>
</div>
{% endblock %}
```

### templates/map.html

```html
{% extends "base.html" %} {% block title %}Map{% endblock %} {% block content %}
<div class="map-container">
  <h2>Map Page</h2>
  <p>This is the protected map page. Only logged-in users can see this.</p>
  <div id="map" style="width: 100%; height: 500px;"></div>
</div>
{% endblock %}
```

### static/css/style.css

```css
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
}

nav {
  background-color: #333;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

nav a {
  color: white;
  text-decoration: none;
}

.form-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.form-container label {
  display: block;
  margin-top: 10px;
}

.form-container input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  box-sizing: border-box;
}

.form-container button {
  width: 100%;
  padding: 10px;
  margin-top: 15px;
  background-color: #333;
  color: white;
  border: none;
  cursor: pointer;
}

.error {
  color: red;
  background-color: #ffe6e6;
  padding: 10px;
  border-radius: 3px;
}

.map-container {
  padding: 20px;
}
```

---

## Common Flask Imports

```python
from flask import (
    Flask,              # Main Flask class
    render_template,    # Render HTML templates
    request,            # Access request data
    redirect,           # Redirect to another route
    url_for,            # Generate URLs for routes
    make_response,      # Create response object (for cookies)
    jsonify,            # Return JSON responses
    flash,              # Flash messages
    session             # Server-side sessions
)
```

---

## Tips for Your Project

1. **Always hash passwords** - Use `generate_password_hash()` and `check_password_hash()`

2. **Validate input** - Check that forms are filled correctly

3. **Use cookies securely** - Set `httponly=True` for authentication cookies

4. **Organize your code** - Keep routes clean, use functions for repeated logic

5. **Error handling** - Show user-friendly error messages

6. **Debug mode** - Use `debug=True` during development, but turn it off in production

---

## Next Steps

1. Practice with the examples above
2. Read Flask official documentation: https://flask.palletsprojects.com/
3. Try building a simple app (calculator, todo list, etc.)
4. Then start on your WebGIS project

**Good luck learning Flask!**
