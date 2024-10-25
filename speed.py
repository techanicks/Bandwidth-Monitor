from flask import Flask, jsonify, send_file, render_template
import speedtest
import csv
import os
from datetime import datetime
import geocoder

app = Flask(__name__)

# Set the path for the CSV file
csv_file_path = os.path.join(os.getcwd(), 'speedtest_results.csv')

# Create the CSV file if it doesn't exist and write headers
if not os.path.isfile(csv_file_path):
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Time', 'Location', 'Download Speed (Mbps)', 'Upload Speed (Mbps)', 'Ping (ms)'])

@app.route('/')
def index():
    return render_template('speedtest.html')

@app.route('/speedtest', methods=['GET'])
def run_speedtest():
    try:
        # Get user's geolocation based on IP
        user_location = geocoder.ip('me')
        location = f"{user_location.city}, {user_location.country}" if user_location.city else 'Unknown Location'

        # Initialize Speedtest
        st = speedtest.Speedtest()
        st.get_best_server()

        # Run the speed test
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000      # Convert to Mbps
        ping = st.results.ping
        test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save the result to CSV
        with open(csv_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([test_time, location, round(download_speed, 2), round(upload_speed, 2), ping])

        # Return the result as JSON
        return jsonify({
            'time': test_time,
            'location': location,
            'download_speed': round(download_speed, 2),
            'upload_speed': round(upload_speed, 2),
            'ping': ping
        })

    except Exception as e:
        print(f"Error during speed test: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-results', methods=['GET'])
def download_results():
    try:
        if not os.path.isfile(csv_file_path):
            return jsonify({'error': 'CSV file does not exist'}), 404
        
        return send_file(csv_file_path, as_attachment=True)

    except Exception as e:
        print(f"Error downloading results: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Bind to the PORT environment variable if available, otherwise use port 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
