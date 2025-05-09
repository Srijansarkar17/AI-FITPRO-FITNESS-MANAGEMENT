from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__, static_folder="static", template_folder="templates")

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'Srijan@2004',  # Replace with your MySQL password
    'database': 'posefit'  # Replace with your database name
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        preferred_date = request.form.get('date')
        preferred_time = request.form.get('time')
        topic = request.form.get('topic')
        
        # Connect to MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Insert data into wellness_appointments table
        insert_query = """
        INSERT INTO wellness_appointments 
        (full_name, email_address, phone_number, preferred_date, preferred_time, discussion_topic) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            name, 
            email, 
            phone, 
            preferred_date, 
            preferred_time, 
            topic
        ))
        
        # Commit the transaction
        conn.commit()
        
        # Close connection
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Booking submitted successfully!"})
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)