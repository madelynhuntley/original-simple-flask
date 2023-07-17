from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request

db = SQLAlchemy()

app = Flask(__name__)

conn = psycopg2.connect("dbname='madelyn' user='madelynhuntley' host='localhost'")

cursor = conn.cursor()

cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            user_id SERIAL PRIMARY KEY,
            first_name VARCHAR NOT NULL,
            last_name VARCHAR,
            email VARCHAR NOT NULL UNIQUE,
            phone VARCHAR,
            city VARCHAR,
            state VARCHAR,
            active BOOLEAN NOT NULL DEFAULT TRUE
        );
        ''')

conn.commit()

@app.route('/user/add', methods=['POST'])
def add_user():
    data = request.json

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email') #None
    
    if not email:
        return "Email must not be an empty str", 400
    phone = data.get('phone')

    if len(phone) > 10: 
        return "Your phone number should only be 10 characters", 400
    city = data.get('city')
    state= data.get('state')


    cursor.execute('''
        INSERT INTO users (first_name, last_name, email, phone, city, state)
        VALUES (%s, %s, %s,%s, %s, %s)
        ''', (first_name, last_name, email, phone, city, state))
    conn.commit()
    
    return("user added"), 201


#CRUDDA
# Create - INSERT
# Read - SELECT (read all active, read)
# Update - UPDATE
# Delete - DELETE
# Deactivate - UPDATE
# Activate - UPDATE 

@app.route('/users/get', methods=['GET'])
def get_all_active_users():
    cursor.execute("SELECT * FROM users WHERE active='t';")
    results = cursor.fetchall()

    if results:
        users = []
        for u in results:
            user_record = {
                'user_id':u[0],
                'first_name':u[1],
                'last_name':u[2],
                'email':u[3],
                'phone':u[4],
                'city':u[5],
                'state':u[6],
                'active':u[7]
            }

            users.append(user_record)
        return jsonify(users), 200

    return 'No users found', 404

@app.route('/user/deactivate/<user_id>', methods=['POST', 'PUT', 'PATCH'])
def deactivate_user_by_id(user_id):
    if not user_id.isnumeric(): 
        return (f"Invalid user_id: {user_id}")
    
    cursor.execute("SELECT * FROM users WHERE user_id=%s;", (user_id,))
    results = cursor.fetchall()

    if not results: 
        return (f"User {user_id} not found"), 404

    cursor.execute("UPDATE users SET active='f' WHERE user_id=%s", (user_id,))
    conn.commit()
    
    return('user deactiveated'), 200

 


if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=8086)