from flask import Flask, request, jsonify
from flask_cors import CORS
from Database import SQLDatabase
from datetime import datetime
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def prepare_data(df_data):
    # Convert DataFrame to dictionary
    data_dict = df_data.to_dict(orient='records')
    
    # Handle Timedelta objects
    for record in data_dict:
        for key, value in record.items():
            if isinstance(value, pd.Timedelta):
                record[key] = value.seconds // 3600
    ready_data = data_dict

    return ready_data

def fetch_users(HouseNO, month, year):
    try:
        db_manager = SQLDatabase("localhost", "root", "", "water_management_system")
        db_manager.connect()
        query_consumption = f"SELECT Date, SUM(Quantity) AS sum_quantity FROM `consumption` WHERE HouseNO = '{HouseNO}' AND YEAR(Date) = '{year}' AND MONTH(Date) = '{month}' GROUP BY Date;"
        data_consumption = db_manager.read_data(query_consumption)

        get_rate_query = f"SELECT u1.rate, u2.HouseNO, u2.UserName FROM users u1 JOIN users u2 ON u1.HouseNO = '0' AND u2.HouseNO = '{HouseNO}';"
        get_rate_data = db_manager.read_data(get_rate_query)
        ready_data = prepare_data(data_consumption)
        ready_rate = prepare_data(get_rate_data)
        db_manager.disconnect()
        return(ready_data, True, ready_rate)
    except Exception as e:
        db_manager.disconnect()
        # print(f"An error occurred: {e}")
        return (None, False, None)
    
def verify_login(email, hashed_password, month, year):
    try:
        db_manager = SQLDatabase("localhost", "root", "", "water_management_system")
        db_manager.connect()
        query_users = f"SELECT * FROM users WHERE email = '{email}';"
        data_users = db_manager.read_data(query_users)
        
        if data_users['PasswordHash'][0] == hashed_password:
            if data_users['HouseNO'][0] == 0: #if admin initially send all users data from users table
                query_users = '''SELECT c.HouseNO, 
                                SUM(c.Quantity) AS total_consumption,
                                u.UserName,
                                u.HeadCount
                                FROM consumption c
                                JOIN users u ON c.HouseNO = u.HouseNO
                                WHERE MONTH(c.date) = %s
                                AND YEAR(c.date) = %s
                                AND u.HouseNO != '0'
                                GROUP BY c.HouseNO, u.UserName, u.HeadCount;'''
                data_users = db_manager.read_data(query_users, (month,year))
                ready_data = prepare_data(data_users)
                
                get_rate_query = f"SELECT rate FROM users WHERE HouseNO = '0';"
                get_rate_data = db_manager.read_data(get_rate_query)
                ready_rate = prepare_data(get_rate_data)
                db_manager.disconnect()
                return(ready_data, True, ready_rate)
            
            else: #if regular users send all their data with the rate 
                users_data = fetch_users(data_users['HouseNO'][0], month, year)
                return(users_data)
        else:
            db_manager.disconnect()
            return (None, False, None)
    except Exception as e:
        db_manager.disconnect()
        # print(f"An error occurred: {e}")
        return (None, False, None)

def create_user(HouseNO, UserName, PhoneNumber, HeadCount, email, hashed_password):
    try:
        db_manager = SQLDatabase("localhost", "root", "", "water_management_system")
        db_manager.connect()
        
        data = {
            'HouseNO': [HouseNO],
            'UserName': [UserName],
            'PhoneNumber': [PhoneNumber],
            'HeadCount': [HeadCount],
            'email': [email],
            'PasswordHash': [hashed_password]
        }
        data_df = pd.DataFrame(data) 

        return (db_manager.insert_data(data_df,'users'))
    
    except Exception as e:
        db_manager.disconnect()
        return (False) 

def delete_user(email):
    # Implement logic to delete a user
    pass

# API to verify login information
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    hashed_password = data.get('password')
    # Get the current date; month and year
    current_date = datetime.now()
    month = current_date.month
    year = current_date.year

    consumption_data = verify_login(email, hashed_password, month, year)
    if consumption_data[1]:
        return jsonify({'consumption_data': consumption_data[0], 'Auth':consumption_data[1], 'other_data':consumption_data[2]})
    else:
        return jsonify({'error': 'Invalid login credentials', 'Auth':consumption_data[1]}), 401

# API accessible only by admin to read, write, and delete from the users table
@app.route('/admin/users', methods=['GET', 'POST', 'DELETE'])
def manage_users():
    # Implement authentication to ensure only admin can access this API
    # Example: Check if the request is made by an admin user
    
    if request.method == 'GET':
        # Implement logic to retrieve all users
        data = request.json
        HouseNO = data.get('HouseNO')
        month = data.get('month')
        year = data.get('year')
        
        users_data = fetch_users(HouseNO, month, year)
        return jsonify({'consumption_data': users_data[0], 'other_data':users_data[2]})

    elif request.method == 'POST':
        data = request.json
        HouseNO = data.get('HouseNO')
        UserName = data.get('UserName')
        PhoneNumber = data.get('PhoneNumber')
        HeadCount = data.get('HeadCount')
        email = data.get('email')
        hashed_password = data.get('hashed_password')
    
        response = create_user(HouseNO, UserName, PhoneNumber, HeadCount, email, hashed_password)
        return jsonify({'response': response})

    elif request.method == 'DELETE':
        data = request.json
        email = data.get('email')
        delete_user(email)
        return jsonify({'message': 'delete option not available'})

if __name__ == '__main__':
    app.run(debug=True)
