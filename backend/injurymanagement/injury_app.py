from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# DB connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Srijan@2004",
        database="posefit"
    )

@app.route('/')
def index():
    return render_template('index.html')  # Serve the index.html form

# POST route for adding injury records
@app.route('/add_injury', methods=['POST'])
def add_injury():
    data = request.get_json()

    user_id = data.get('user_id')
    injury_type = data.get('injury_type')
    recovery_status = data.get('recovery_status')

    if not injury_type or not recovery_status:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO INJURY_HISTORY (user_id, injury_type, recovery_status)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_id, injury_type, recovery_status))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Injury record added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/get_injuries/<int:user_id>', methods=['GET'])
def get_injuries(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT injury_id, injury_type, recovery_status
            FROM INJURY_HISTORY
            WHERE user_id = %s
        """, (user_id,))
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(records)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
