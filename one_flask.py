import subprocess
import requests
import time
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import atexit
from dotenv import load_dotenv, set_key

# Load existing environment variables
load_dotenv()

# Set up path for the .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')

app = Flask(__name__)

# List of microservice Flask apps with their expected ports
microservices = [
    {"name": "Chatbot", "path": r"C:\Users\srija\OneDrive\Desktop\dbms_fitness_project\Backend\Fitness_chatbot\app.py", "port": 3001},
    {"name": "OpenCV", "path": r"C:\Users\srija\OneDrive\Desktop\dbms_fitness_project\Backend\opencv\app.py", "port": 3030},
    {"name": "Challenges", "path": r"C:\Users\srija\OneDrive\Desktop\dbms_fitness_project\Backend\challenges\app.py", "port": 3009},
    {"name": "Injury", "path": r"C:\Users\srija\OneDrive\Desktop\dbms_fitness_project\Backend\injury\injury_app.py", "port": 5002},
    {"name": "Nutrition", "path": r"C:\Users\srija\OneDrive\Desktop\dbms_fitness_project\Backend\Nutrition_plan\app.py", "port": 3012},
    {"name": "Mental_wellness", "path": r"C:\Users\srija\OneDrive\Desktop\dbms_fitness_project\Backend\MentalWellness\well_app.py", "port": 5001},
]

running_processes = []

def launch_microservices():
    for service in microservices:
        print(f"Launching {service['name']} on port {service['port']}...")
        try:
            # Normalize the path
            normalized_path = os.path.normpath(service["path"])
            directory = os.path.dirname(normalized_path)
            filename = os.path.basename(normalized_path)
            
            if not os.path.exists(normalized_path):
                print(f"❌ Error: File not found - {normalized_path}")
                continue
            
            # Start the service
            process = subprocess.Popen(
                ["python", filename],
                cwd=directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            running_processes.append({"process": process, "service": service})
            print(f"✅ Started {service['name']}")
        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {str(e)}")

def cleanup_processes():
    print("\nTerminating microservices...")
    for proc in running_processes:
        try:
            proc["process"].terminate()
        except:
            pass
    time.sleep(2)
    print("All microservices terminated.")

# Register cleanup function
atexit.register(cleanup_processes)

# Launch microservices on startup
launch_microservices()

app.secret_key = 'cd0df92f92f997d5492f59872add022bf6c4473f1fee51ebacd4a76fa38c82ef'

# Helper function to get a DB connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Srijan@2004",
        database="posefit"
    )

# Function to update the User_id in .env file
def update_user_id_in_env(user_id):
    # Create the .env file if it doesn't exist
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write(f"USER_ID={user_id}\n")
    else:
        # Update existing .env file
        set_key(env_path, "USER_ID", str(user_id))
    
    print(f"Updated USER_ID in .env to: {user_id}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')
        password = request.form.get('password')
        weight = request.form.get('weight')

        # Simple validation
        if not all([name, email, age, gender, password, weight]):
            flash('Please fill out all fields')
            return redirect(url_for('signup'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if email already exists
            cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already exists')
                return redirect(url_for('signup'))

            # Insert new user
            query = """
                INSERT INTO users (name, email, age, gender, password, weight)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, email, age, gender, password, weight))
            conn.commit()
            
            # Get the newly created user ID
            cursor.execute("SELECT User_id FROM users WHERE email = %s", (email,))
            user_id = cursor.fetchone()[0]
            
            # Update the User_id in .env file
            update_user_id_in_env(user_id)
            
            flash('Sign up successful! Please login.')
            return redirect(url_for('index'))

        except mysql.connector.Error as err:
            flash(f'Error: {err}')
            return redirect(url_for('signup'))

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch user details based on email
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user and user['password'] == password:
            # Update the User_id in .env file
            update_user_id_in_env(user['User_id'])
            
            return jsonify({
                "success": True, 
                "message": "Login successful",
                "user": {
                    "id": user['User_id'],
                    "name": user['name'],
                    "email": user['email']
                }
            })
        else:
            return jsonify({"success": False, "message": "Invalid email or password"})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Database error: {err}"})

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Route to get current logged-in user ID
@app.route('/get-current-user', methods=['GET'])
def get_current_user():
    user_id = os.getenv('USER_ID')
    if user_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT User_id, name, email FROM users WHERE User_id = %s", (user_id,))
            user = cursor.fetchone()
            
            if user:
                return jsonify({
                    "success": True,
                    "user": user
                })
            else:
                return jsonify({"success": False, "message": "User not found"})
        except mysql.connector.Error as err:
            return jsonify({"success": False, "message": f"Database error: {err}"})
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    else:
        return jsonify({"success": False, "message": "No user is currently logged in"})

if __name__ == '__main__':
    try:
        app.run(debug=True, port=5000, host='0.0.0.0')
    finally:
        cleanup_processes()