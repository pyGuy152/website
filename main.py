from flask import Flask, request, jsonify, render_template
import json
import os
import matplotlib
matplotlib.use('Agg')  # Add this line before importing pyplot
import matplotlib.pyplot as plt
import io
import base64
import random
app = Flask(__name__)

DATA_FILE = "data.json"

API_PASSWORD = "-8556072034411574859"

def generate_graph_base64(name):
    """Generates a simple line graph and returns its base64 encoding."""
    try:
        with open("data.json", "r") as f:
            y = json.load(f)
        for i in y:
            if i['name'] == name:
                y = i
        x = []
        for i in range(len(y['price'])):
            x.append(i)

        plt.plot(x, y['price'])
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.title(y['name'])

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close()

        return img_base64
    except:
        return "no"


def save_data(y):
    """Saves data to the JSON file."""
    with open("data.json", "r") as f:
        x = json.load(f)
    with open("data.json", "r") as f:
        check = json.load(f)
    for i in range(len(x)):
        if x[i]['name'] == y['name']:
            x[i]['price'] += y['price']
    if check == x:
        x.append(y)
    with open("data.json", "w") as f:
        json.dump(x, f) 

@app.route('/api/data', methods=['POST'])
def process_data():
    """Processes data received in a POST request and saves it to a file."""
    try:
        password = request.headers.get('API-Password') # Get password from header
        if not password:
            password_json = request.get_json()
            if password_json and 'password' in password_json:
                password = password_json['password'] #get password from json body
        if not password or password != API_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        save_data(data)

        return jsonify({"message": "Data received and saved successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/<path_parameter>')
def index(path_parameter):
    """Renders the index page with the graph."""
    print(path_parameter)
    graph_base64 = generate_graph_base64(path_parameter.upper())
    if graph_base64 == 'no':
        return jsonify({"error": "Not a Clan in database"}), 404
    return render_template('index.html', graph_base64=graph_base64)

@app.route('/graph_update/<clan_name>')
def graph_update(clan_name):
    """API endpoint to get the updated graph."""
    graph_base64 = generate_graph_base64(clan_name.upper())
    if graph_base64 == 'no':
        return jsonify({"error": "Not a Clan in database"}), 404
    return jsonify({'graph_base64': graph_base64})

if __name__ == '__main__':
    app.run(debug=True)