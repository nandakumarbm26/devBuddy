from flask import Flask, request
from dotenv import load_dotenv
import os
load_dotenv() 


LOG_FILE = os.getenv("LOG_FILE", "request_log.txt")

app = Flask(__name__)

@app.route('/print-body', methods=['POST'])
def print_body():
    data = request.get_data(as_text=True)  # Read raw body as text

    # Log to console
    print(f"Request Body:\n{data}")

    # Log to file
    with open(LOG_FILE, "a") as f:  # "a" means append mode
        f.write(f"New Request:\n{data}\n{'-'*40}\n")

    return "Body received and logged!", 200

if __name__ == '__main__':
    app.run(debug=True)
