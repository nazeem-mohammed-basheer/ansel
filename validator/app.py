# Import necessary modules from Flask
from flask import Flask, request, jsonify
# Import re for regular expressions
import re

# Create a Flask application instance
app = Flask(__name__)

# Define the regular expression for email validation
# This is a common and reasonably robust regex.
# It checks for:
# 1. Characters before @: alphanumeric, dots, underscores, percents, plus, hyphens
# 2. @ symbol
# 3. Characters after @ (domain): alphanumeric, dots, hyphens
# 4. A dot
# 5. Top-level domain (TLD): 2 to 6 characters, letters only
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$")

@app.route('/validate-email', methods=['POST'])
def validate_email_api():
    """
    API endpoint to validate an email address.
    Expects a JSON payload with an 'email' field.
    Example request body: {"email": "test@example.com"}
    """
    # Check if the request body is JSON
    if not request.is_json:
        # Return an error if content type is not JSON
        return jsonify({"error": "Request must be JSON"}), 400

    # Get the JSON data from the request
    data = request.get_json()
    # Extract the 'email' field from the JSON data
    email = data.get('email')

    # Check if the 'email' field is missing
    if not email:
        # Return an error if email is not provided
        return jsonify({"error": "Email field is required"}), 400

    # Strip leading/trailing whitespace from the email
    email = email.strip()

    # Perform email validation using the regex
    if EMAIL_REGEX.match(email):
        # If valid, return a success response
        return jsonify({"email": email, "is_valid": True, "message": "Email is valid"}), 200
    else:
        # If invalid, return an error response
        return jsonify({"email": email, "is_valid": False, "message": "Email is not valid"}), 200

# Run the Flask application
# This ensures the server starts only when the script is executed directly
if __name__ == '__main__':
    # You can specify host='0.0.0.0' to make it accessible from other machines on your network
    # For local development, host='127.0.0.1' (localhost) is fine.
    # debug=True enables debug mode, which provides helpful error messages and reloads the server on code changes.
    app.run(debug=True, host='127.0.0.1', port=5000)
