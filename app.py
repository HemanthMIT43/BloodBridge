from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages and session management

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Valan@2005',
    'database': 'bloodbank'
}

# Create a connection pool
try:
    cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)
except Error as e:
    print(f"Error creating connection pool: {e}")

# Function to get a database connection
def get_db_connection():
    try:
        return cnxpool.get_connection()
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        return None

# ------------------ Routes ------------------

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Route for Emergency Blood Request
@app.route("/emergency-request", methods=["GET", "POST"])
def emergency_request():
    if request.method == "POST":
        blood_type = request.form["blood_type"]
        quantity = request.form["quantity"]
        requester_name = request.form["requester_name"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO emergency_requests (blood_type, quantity, requester_name, request_date)
                VALUES (%s, %s, %s, %s)
            """, (blood_type, quantity, requester_name, datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Emergency blood request submitted successfully!", "success")
            return redirect(url_for("home"))
        except Error as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for("emergency_request"))
    
    return render_template("emergency_request.html")

# Route for Regular Donor Management
@app.route("/donor-dashboard", methods=["GET", "POST"])
def donor_dashboard():
    if request.method == "POST":
        donor_name = request.form["donor_name"]
        blood_type = request.form["blood_type"]
        last_donation = request.form["last_donation"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO donors (name, blood_type, last_donation)
                VALUES (%s, %s, %s)
            """, (donor_name, blood_type, last_donation))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Donor information updated successfully!", "success")
            return redirect(url_for("home"))
        except Error as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for("donor_dashboard"))

    return render_template("donor_dashboard.html")

# Route for Blood Bank Inventory Update
@app.route("/inventory-update", methods=["GET", "POST"])
def inventory_update():
    if request.method == "POST":
        blood_type = request.form["blood_type"]
        stock_quantity = request.form["stock_quantity"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO inventory (blood_type, stock_quantity, last_updated)
                VALUES (%s, %s, %s)
            """, (blood_type, stock_quantity, datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Inventory updated successfully!", "success")
            return redirect(url_for("home"))
        except Error as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for("inventory_update"))

    return render_template("inventory_update.html")

# Route to test the database connection
@app.route("/test-db-connection")
def test_db_connection():
    try:
        conn = get_db_connection()
        if conn is None:
            return "Error: Could not establish a database connection."
        
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return f"Connected to the database: {db_name[0]}"
    except Error as e:
        return f"Error: {e}"

# Route for Donor List (if needed)
@app.route("/donor-list")
def donor_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM donors")
        donors = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("donor_list.html", donors=donors)
    except Error as e:
        return f"Error: {e}"

# Route to view emergency requests
@app.route("/emergency-request-list")
def emergency_request_list():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emergency_requests")
        requests = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("emergency_request_list.html", requests=requests)
    except Error as e:
        return f"Error: {e}"

# ------------------ Run the Flask App ------------------
if __name__ == "__main__":
    app.run(debug=True)
