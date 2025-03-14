from flask import Flask, request, jsonify
import redis
import json
import datetime

app = Flask(__name__)

# Connect to Redis using the service name 'redis'
r = redis.Redis(host='redis', port=6379, decode_responses=True)

# Receives sensor data from ESP and stores it in Redis
@app.route("/sensor", methods=["POST"])
def receive_data():
    data = request.json  # Expecting JSON data
    if not data or "sensor_id" not in data or "value" not in data:
        return jsonify({"error": "Invalid data"}), 400

    sensor_id = data["sensor_id"]
    value = data["value"]

    if sensor_id == "potentiometer":
        # Increment counter to get a new record ID (starting from 1)
        record_id = r.incr("potentiometer_counter")
        # Get the current time in a readable format
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Create a reading record
        reading = {
            "record_id": record_id,
            "value": value,
            "time": current_time
        }
        # Append the reading to the list (maintaining all records)
        r.rpush("potentiometer_readings", json.dumps(reading))
    else:
        # For other sensor types, store them as a simple key-value pair.
        r.set(sensor_id, json.dumps({"value": value}))

    return jsonify({"message": "Data stored successfully"})

@app.route("/sensor/<sensor_id>", methods=["GET"])
def get_data(sensor_id):
    if sensor_id == "potentiometer":
        data_list = r.lrange("potentiometer_readings", 0, -1)
        readings = [json.loads(item) for item in data_list]
        return jsonify(readings)
    else:
        data = r.get(sensor_id)
        if data:
            return jsonify(json.loads(data))
        return jsonify({"error": "Sensor data not found"}), 404

@app.route("/", methods=["GET"])
def index():
    data_list = r.lrange("potentiometer_readings", 0, -1)
    readings = [json.loads(item) for item in data_list] if data_list else []

    # Build HTML table rows for each reading
    table_rows = ""
    for reading in readings:
        table_rows += f"<tr><td>{reading['record_id']}</td><td>{reading['value']}</td><td>{reading['time']}</td></tr>"
    # HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>Potentiometer Readings</title>
        <script>
          function refreshData() {{
            fetch("/sensor/potentiometer")
              .then(response => response.json())
              .then(data => {{
                let tableBody = document.getElementById("data-table-body");
                tableBody.innerHTML = "";
                data.forEach(reading => {{
                  let row = `<tr><td>${{reading.record_id}}</td><td>${{reading.value}}</td><td>${{reading.time}}</td></tr>`;
                  tableBody.innerHTML += row;
                }});
              }});
          }}
          setInterval(refreshData, 5000);
        </script>
        <style>
          body {{
            background-color: white;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
          }}
          .container {{
            width: 80%;
            margin: 0 auto;
            text-align: center;
          }}
          table {{
            margin: 0 auto;
            border-collapse: collapse;
            width: 60%;
          }}
          th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: center;
          }}
          th {{
            background-color: #f2f2f2;
          }}
        </style>
      </head>
      <body onload="refreshData()">
        <div class="container">
          <h1>Potentiometer Readings</h1>
          <table>
            <thead>
              <tr>
                <th>Record ID</th>
                <th>Value</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody id="data-table-body">
              {table_rows if table_rows else "<tr><td colspan='3'>No Data</td></tr>"}
            </tbody>
          </table>
        </div>
      </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
