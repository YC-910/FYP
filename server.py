import pyodbc
from flask import Flask, jsonify, send_from_directory, redirect, request
import os
import pickle
import pandas as pd

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_sql_server_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=YCLAPTOP\\SQLSERVEREXPRESS;'
        'DATABASE=FYP;'
        'UID=sa;'
        'PWD=pengbin04;'
    )

# Load the pre-trained Logistic Regression model
MODEL_PATH = r"C:\\Users\\ycong\\Documents\\FYP\\FYP_Code\\log_reg_model_tuned1.pkl"
with open(MODEL_PATH, "rb") as f:
    data = pickle.load(f)
    log_reg = data['model']         # your logistic regression model
    symptom_cols = data['symptom_cols']

print("Logistic Regression model loaded successfully.")

# Redirect root to /Welcome
@app.route('/')
def redirect_to_welcome():
    return redirect('/Welcome')

@app.route('/index')
def index_page():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/Hospital')
def add_page():
    return send_from_directory(BASE_DIR, 'Hospital.html')

@app.route('/Department')
def depart_page():
    return send_from_directory(BASE_DIR, 'Department.html')

@app.route('/Login')
def login_page():
    return send_from_directory(BASE_DIR, 'Login.html')

@app.route('/Patient')
def patient_page():
    return send_from_directory(BASE_DIR, 'Patient.html')

@app.route('/Welcome')
def welcome_page():
    return send_from_directory(BASE_DIR, 'Healthcare Portal.html')

@app.route('/Labotary')
def labotary_page():
    return send_from_directory(BASE_DIR, 'Public Health Labotary.html')

@app.route('/Dental')
def dental_page():
    return send_from_directory(BASE_DIR, 'Dental Clinic.html')

@app.route('/Clinic')
def clinic_page():
    return send_from_directory(BASE_DIR, 'Health Clinic.html')

@app.route('/Predictive')
def predictive_page():
    return send_from_directory(BASE_DIR,'Predictive.html')

@app.route('/api/diseases')
def get_diseases():
    try:
        conn = get_sql_server_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT diseases
            FROM [Hospital_Facilities].[dbo].[Transformed_Dataset]
            ORDER BY diseases
        """)
        rows = cursor.fetchall()
        # Skip the first column 'diseases'
        diseases = [{'diseases': row[0]} for row in rows if row[0].lower() != 'diseases']
        cursor.close()
        conn.close()
        return jsonify(diseases)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/symptoms')
def get_symptoms():
    try:
        conn = get_sql_server_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT diseases
            FROM [Hospital_Facilities].[dbo].[Merged_Dataset]
            ORDER BY diseases
        """)
        rows = cursor.fetchall()
        # Skip the first column 'diseases'
        diseases = [{'diseases': row[0]} for row in rows if row[0].lower() != 'diseases']
        cursor.close()
        conn.close()
        return jsonify(diseases)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/states')
def get_states():
    try:
        conn = get_sql_server_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT State FROM [Hospital_Facilities].[dbo].[Hospital] ORDER BY State')
        rows = cursor.fetchall()
        states = [row[0] for row in rows]
        cursor.close()
        conn.close()
        return jsonify(states)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cities/<state>')
def get_cities(state):
    try:
        conn = get_sql_server_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT DISTINCT City FROM [Hospital_Facilities].[dbo].[Hospital] WHERE State = ?',
            (state,)
        )
        rows = cursor.fetchall()
        cities = [row[0] for row in rows]
        cursor.close()
        conn.close()
        return jsonify(cities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search_by_disease')
def search_by_disease():
    try:
        disease = request.args.get('disease')
        if not disease:
            return jsonify({'error': 'Missing disease parameter'}), 400

        conn = get_sql_server_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT *
            FROM [Hospital_Facilities].[dbo].[Merged_Dataset]
            WHERE LOWER(diseases) = LOWER(?)
        ''', (disease,))

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

        if not rows:
            cursor.close()
            conn.close()
            return jsonify({"disease": disease, "symptoms": []})

        row = dict(zip(columns, rows[0]))

        symptom_columns = columns[1:]
        found_symptoms = [col for col in symptom_columns if str(row.get(col)).strip() == "1"]

        cursor.close()
        conn.close()

        return jsonify({
            "disease": row["diseases"],
            "symptoms": found_symptoms
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ New tte to add hospital
@app.route('/api/add-hospital', methods=['POST'])
def add_hospital():
    try:
        data = request.get_json()

        name = data.get('name')
        city = data.get('city')
        state = data.get('state')
        address = data.get('address')
        phone_no = data.get('phone_no')
        location = data.get('location')

        if not all([name, city, state, address, phone_no, location]):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_sql_server_connection()
        cursor = conn.cursor()

        # Check if hospital already exists
        cursor.execute("""
            SELECT COUNT(*) FROM [Hospital_Facilities].[dbo].[Hospital]
            WHERE Name = ? AND City = ? AND State = ?
        """, (name, city, state))
        exists = cursor.fetchone()[0]

        if exists > 0:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Data already saved'}), 409

        # Insert new hospital
        cursor.execute("""
            INSERT INTO [Hospital_Facilities].[dbo].[Hospital]
            (Name, City, State, Address, Phone_No, Location)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, city, state, address, phone_no, location))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Data has saved'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ New route to add department
@app.route('/api/add-department', methods=['POST'])
def add_department():
    try:
        data = request.get_json()

        name = data.get('name')
        state = data.get('state')
        address = data.get('address')
        phone_no = data.get('phone_no')
        location = data.get('location')
        website = data.get('website')

        if not all([name, state, address, phone_no, location, website]):
            return jsonify({'error': 'Missing required fields, website'}), 400

        conn = get_sql_server_connection()
        cursor = conn.cursor()

        # Check if department already exists
        cursor.execute("""
            SELECT COUNT(*) FROM [Hospital_Facilities].[dbo].[State_Health_Department]
            WHERE Name = ? AND State = ?
        """, (name, state))
        exists = cursor.fetchone()[0]

        if exists > 0:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Data already saved'}), 409

        # Insert new department
        cursor.execute("""
            INSERT INTO [Hospital_Facilities].[dbo].[State_Health_Department]
            (Name, State, Address, Phone_No, Location, Website)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, state, address, phone_no, location, website))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Data has saved'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ✅ New route to add Labotaty
@app.route('/api/add-labotary', methods=['POST'])
def add_labotary():
    try:
        data = request.get_json()

        name = data.get('name')
        city = data.get('city')
        state = data.get('state')
        address = data.get('address')
        phone_no = data.get('phone_no')
        location = data.get('location')

        if not all([name, city, state, address, phone_no, location]):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_sql_server_connection()
        cursor = conn.cursor()

        # Check if labotary already exists
        cursor.execute("""
            SELECT COUNT(*) FROM [Hospital_Facilities].[dbo].[Public_Health_Labotary]
            WHERE Name = ? AND City = ? AND State = ?
        """, (name, city, state))
        exists = cursor.fetchone()[0]

        if exists > 0:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Data already saved'}), 409

        # Insert new labotary
        cursor.execute("""
            INSERT INTO [Hospital_Facilities].[dbo].[Public_Health_Labotary]
            (Name, City, State, Address, Phone_No, Location)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, city, state, address, phone_no, location))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Data has saved'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ✅ New route to add dental clinic
@app.route('/api/add-dental', methods=['POST'])
def add_dental():
    try:
        data = request.get_json()

        name = data.get('name')
        city = data.get('city')
        state = data.get('state')
        address = data.get('address')
        phone_no = data.get('phone_no')
        location = data.get('location')

        if not all([name, city, state, address, phone_no, location]):
            return jsonify({'error': 'Missing required fields'}), 400

        conn = get_sql_server_connection()
        cursor = conn.cursor()

        # Check if labotary already exists
        cursor.execute("""
            SELECT COUNT(*) FROM [Hospital_Facilities].[dbo].[Dental_Clinic]
            WHERE Name = ? AND City = ? AND State = ?
        """, (name, city, state))
        exists = cursor.fetchone()[0]

        if exists > 0:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Data already saved'}), 409

        # Insert new labotary
        cursor.execute("""
            INSERT INTO [Hospital_Facilities].[dbo].[Dental_Clinic]
            (Name, City, State, Address, Phone_No, Location)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, city, state, address, phone_no, location))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Data has saved'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Signup route
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        hospitalist_id = data.get('hospitalist_id')
        role = data.get('role')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        conn = get_sql_server_connection()
        cursor = conn.cursor()

        # ✅ Check for existing username
        cursor.execute("""
            SELECT COUNT(*) FROM [Hospital_Facilities].[dbo].[Users]
            WHERE username = ?
        """, (username,))
        username_exists = cursor.fetchone()[0]

        if username_exists > 0:
            cursor.close()
            conn.close()
            return jsonify({'error': 'username duplicate'}), 409

        # ✅ Check for existing hospitalist_id (only if not empty)
        if hospitalist_id:
            cursor.execute("""
                SELECT COUNT(*) FROM [Hospital_Facilities].[dbo].[Users]
                WHERE hospitalist_id = ?
            """, (hospitalist_id,))
            hospitalist_exists = cursor.fetchone()[0]

            if hospitalist_exists > 0:
                cursor.close()
                conn.close()
                return jsonify({'error': 'hospitalist_id duplicate'}), 409

        # ✅ Insert user if no duplicates
        cursor.execute("""
            INSERT INTO [Hospital_Facilities].[dbo].[Users] (username, password, hospitalist_id, role)
            VALUES (?, ?, ?, ?)
        """, (username, password, hospitalist_id, role))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'Signup successful'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ Login route (returns role for redirect)
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        conn = get_sql_server_connection()
        cursor = conn.cursor()

        # Check credentials and fetch role
        cursor.execute("""
            SELECT role FROM [Hospital_Facilities].[dbo].[Users]
            WHERE username = ? AND password = ?
        """, (username, password))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            role = user[0]  # Extract role
            return jsonify({
                'message': 'Login successful',
                'role': role
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#route for search
@app.route('/api/search')
def search_hospitals():
    try:
        state = request.args.get('state')
        city = request.args.get('city')

        conn = get_sql_server_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                ID, 
                Name, 
                State, 
                Address, 
                Phone_No, 
                Location, 
                City
            FROM [Hospital_Facilities].[dbo].[Hospital]
            WHERE State = ? AND City = ?
        ''', (state, city))

        rows = cursor.fetchall()

        # Convert SQL results into a list of dictionaries
        hospitals = []
        for row in rows:
            hospitals.append({
                'ID': row[0],
                'Name': row[1],
                'State': row[2],
                'Address': row[3],
                'Phone_No': row[4],
                'Location': row[5],
                'City': row[6]
            })

        cursor.close()
        conn.close()

        return jsonify(hospitals)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict_disease():
    try:
        data = request.get_json()
        selected_symptoms = data.get('symptoms', [])

        if not selected_symptoms:
            return jsonify({'error': 'No symptoms provided'}), 400

        # Transform symptoms into model input
        input_vector = pd.DataFrame([{symptom: 1 if symptom in selected_symptoms else 0
                                      for symptom in symptom_cols}])

        # Predict probabilities using Logistic Regression
        probs = log_reg.predict_proba(input_vector)[0]
        disease_probs = dict(zip(log_reg.classes_, probs))

        # Sort diseases by probability descending
        sorted_diseases = dict(sorted(disease_probs.items(), key=lambda x: x[1], reverse=True))

        # Return probabilities as decimals (0 to 1)
        probabilities = [float(prob) for prob in sorted_diseases.values()]

        return jsonify({
            "predicted_diseases": list(sorted_diseases.keys()),
            "probabilities": probabilities
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)