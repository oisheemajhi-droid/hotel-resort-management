from flask import Flask, render_template, request, redirect
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


# Connect to MySQL
db = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "hotel_resort_management"),
    port=int(os.getenv("DB_PORT", "3306"))
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/customers")
def customers():

    search = request.args.get("search", "").strip()

    cursor = db.cursor()

    if search:
        query = """
            SELECT * FROM customers
            WHERE CAST(customer_id AS CHAR) LIKE %s
            OR first_name LIKE %s
            OR last_name LIKE %s
        """

        search_value = "%" + search + "%"

        cursor.execute(
            query,
            (search_value, search_value, search_value)
        )

    else:
        cursor.execute("SELECT * FROM customers")

    customers_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "customers.html",
        customers=customers_data
    )


@app.route("/rooms")
def rooms():

    search = request.args.get("search", "").strip()

    cursor = db.cursor()

    if search:

        query = """
            SELECT * FROM rooms
            WHERE room_number LIKE %s
            OR room_status LIKE %s
        """

        search_value = "%" + search + "%"

        cursor.execute(
            query,
            (search_value, search_value)
        )

    else:

        cursor.execute("SELECT * FROM rooms")

    rooms_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "rooms.html",
        rooms=rooms_data
    )


@app.route("/bookings")
def bookings():

    search = request.args.get("search", "").strip()

    cursor = db.cursor()

    if search:

        query = """
            SELECT * FROM bookings
            WHERE CAST(booking_id AS CHAR) LIKE %s
            OR CAST(customer_id AS CHAR) LIKE %s
        """

        search_value = "%" + search + "%"

        cursor.execute(
            query,
            (search_value, search_value)
        )

    else:

        cursor.execute("SELECT * FROM bookings")

    bookings_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "bookings.html",
        bookings=bookings_data
    )

@app.route("/services")
def services():

    cursor = db.cursor()

    cursor.execute("SELECT * FROM services")

    services_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "services.html",
        services=services_data
    )
@app.route("/add_service", methods=["POST"])
def add_service():

    service_name = request.form["service_name"]
    service_description = request.form["service_description"]
    service_price = request.form["service_price"]

    cursor = db.cursor()

    cursor.execute("SELECT MAX(service_id) FROM services")

    max_id = cursor.fetchone()[0]

    if max_id is None:
        service_id = 401
    else:
        service_id = max_id + 1

    query = """
        INSERT INTO services
        (service_id, service_name, service_description, service_price)
        VALUES (%s, %s, %s, %s)
    """

    values = (
        service_id,
        service_name,
        service_description,
        service_price
    )

    cursor.execute(query, values)

    db.commit()

    cursor.close()

    return redirect("/services")
@app.route("/update_service/<int:service_id>", methods=["GET", "POST"])
def update_service(service_id):

    cursor = db.cursor()

    if request.method == "POST":

        service_name = request.form["service_name"]
        service_description = request.form["service_description"]
        service_price = request.form["service_price"]

        query = """
            UPDATE services
            SET service_name = %s,
                service_description = %s,
                service_price = %s
            WHERE service_id = %s
        """

        values = (
            service_name,
            service_description,
            service_price,
            service_id
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return redirect("/services")


    cursor.execute(
        "SELECT * FROM services WHERE service_id = %s",
        (service_id,)
    )

    service = cursor.fetchone()

    cursor.close()

    return render_template(
        "update_service.html",
        service=service
    )
@app.route("/delete_service/<int:service_id>")
def delete_service(service_id):

    cursor = db.cursor()

    try:

        cursor.execute(
            "DELETE FROM services WHERE service_id = %s",
            (service_id,)
        )

        db.commit()

    except mysql.connector.IntegrityError:

        db.rollback()

        cursor.close()

        return """
        <script>
            alert("Cannot delete this service because it is linked to another record.");
            window.location.href="/services";
        </script>
        """

    cursor.close()

    return redirect("/services")

@app.route("/billing")
def billing():

    cursor = db.cursor()

    cursor.execute("SELECT * FROM payments")

    payments_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "billing.html",
        payments=payments_data
    )
@app.route("/add_payment", methods=["POST"])
def add_payment():

    booking_id = request.form["booking_id"]
    payment_date = request.form["payment_date"]
    room_charge = request.form["room_charge"]
    service_charge = request.form["service_charge"]
    total_amount = request.form["total_amount"]
    payment_method = request.form["payment_method"]
    payment_status = request.form["payment_status"]

    cursor = db.cursor()

    cursor.execute("SELECT MAX(payment_id) FROM payments")

    max_id = cursor.fetchone()[0]

    if max_id is None:
        payment_id = 501
    else:
        payment_id = max_id + 1

    query = """
        INSERT INTO payments
        (payment_id, booking_id, payment_date,
         room_charge, service_charge, total_amount,
         payment_method, payment_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        payment_id,
        booking_id,
        payment_date,
        room_charge,
        service_charge,
        total_amount,
        payment_method,
        payment_status
    )

    cursor.execute(query, values)

    db.commit()

    cursor.close()

    return redirect("/billing")
@app.route("/update_payment/<int:payment_id>", methods=["GET", "POST"])
def update_payment(payment_id):

    cursor = db.cursor()

    if request.method == "POST":

        booking_id = request.form["booking_id"]
        payment_date = request.form["payment_date"]
        room_charge = request.form["room_charge"]
        service_charge = request.form["service_charge"]
        total_amount = request.form["total_amount"]
        payment_method = request.form["payment_method"]
        payment_status = request.form["payment_status"]

        query = """
            UPDATE payments
            SET booking_id = %s,
                payment_date = %s,
                room_charge = %s,
                service_charge = %s,
                total_amount = %s,
                payment_method = %s,
                payment_status = %s
            WHERE payment_id = %s
        """

        values = (
            booking_id,
            payment_date,
            room_charge,
            service_charge,
            total_amount,
            payment_method,
            payment_status,
            payment_id
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return redirect("/billing")


    cursor.execute(
        "SELECT * FROM payments WHERE payment_id = %s",
        (payment_id,)
    )

    payment = cursor.fetchone()

    cursor.close()

    return render_template(
        "update_payment.html",
        payment=payment
    )
@app.route("/delete_payment/<int:payment_id>")
def delete_payment(payment_id):

    cursor = db.cursor()

    try:

        cursor.execute(
            "DELETE FROM payments WHERE payment_id = %s",
            (payment_id,)
        )

        db.commit()

    except mysql.connector.IntegrityError:

        db.rollback()

        cursor.close()

        return """
        <script>
            alert("Cannot delete this payment because it is linked to another record.");
            window.location.href="/billing";
        </script>
        """

    cursor.close()

    return redirect("/billing")

@app.route("/reports")
def reports():

    cursor = db.cursor()

    # Total Customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]

    # Total Rooms
    cursor.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cursor.fetchone()[0]

    # Total Bookings
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    # Total Payments
    cursor.execute("SELECT COUNT(*) FROM payments")
    total_payments = cursor.fetchone()[0]

    # Total Revenue
    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0)
        FROM payments
        WHERE payment_status = 'Paid'
    """)

    total_revenue = cursor.fetchone()[0]

    # Available Rooms
    cursor.execute("""
        SELECT COUNT(*)
        FROM rooms
        WHERE room_status = 'Available'
    """)

    available_rooms = cursor.fetchone()[0]

    # Occupied Rooms
    cursor.execute("""
        SELECT COUNT(*)
        FROM rooms
        WHERE room_status = 'Occupied'
    """)

    occupied_rooms = cursor.fetchone()[0]

    # Booking Details Report
    cursor.execute("SELECT * FROM booking_details_view")

    reports_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "reports.html",
        total_customers=total_customers,
        total_rooms=total_rooms,
        total_bookings=total_bookings,
        total_payments=total_payments,
        total_revenue=total_revenue,
        available_rooms=available_rooms,
        occupied_rooms=occupied_rooms,
        reports=reports_data
    )


@app.route("/update_customer/<int:customer_id>", methods=["GET", "POST"])
def update_customer(customer_id):

    cursor = db.cursor()

    if request.method == "POST":

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        contact_number = request.form["contact_number"]
        city = request.form["city"]
        registration_date = request.form["registration_date"]
        gender = request.form["gender"]

        query = """
            UPDATE customers
            SET first_name = %s,
                last_name = %s,
                email = %s,
                contact_number = %s,
                city = %s,
                registration_date = %s,
                gender = %s
            WHERE customer_id = %s
        """

        values = (
            first_name,
            last_name,
            email,
            contact_number,
            city,
            registration_date,
            gender,
            customer_id
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return redirect("/customers")

    cursor.execute(
        "SELECT * FROM customers WHERE customer_id = %s",
        (customer_id,)
    )

    customer = cursor.fetchone()

    cursor.close()

    return render_template(
        "update_customer.html",
        customer=customer
    )
@app.route("/delete_customer/<int:customer_id>")
def delete_customer(customer_id):

    cursor = db.cursor()

    try:

        cursor.execute(
            "DELETE FROM customers WHERE customer_id = %s",
            (customer_id,)
        )

        db.commit()

        message = "Customer deleted successfully."

    except mysql.connector.IntegrityError:

        db.rollback()

        message = "Customer cannot be deleted because they have existing bookings."

    cursor.close()

    return f"""
    <script>
        alert("{message}");
        window.location.href = "/customers";
    </script>
    """
@app.route("/update_room/<int:room_id>", methods=["GET", "POST"])
def update_room(room_id):

    cursor = db.cursor()

    if request.method == "POST":

        room_number = request.form["room_number"]
        room_type_id = request.form["room_type_id"]
        floor_number = request.form["floor_number"]
        room_status = request.form["room_status"]
        maintenance_status = request.form["maintenance_status"]

        query = """
            UPDATE rooms
            SET room_number = %s,
                room_type_id = %s,
                floor_number = %s,
                room_status = %s,
                maintenance_status = %s
            WHERE room_id = %s
        """

        values = (
            room_number,
            room_type_id,
            floor_number,
            room_status,
            maintenance_status,
            room_id
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return redirect("/rooms")

    cursor.execute(
        "SELECT * FROM rooms WHERE room_id = %s",
        (room_id,)
    )

    room = cursor.fetchone()

    cursor.close()

    return render_template(
        "update_room.html",
        room=room
    )
@app.route("/delete_room/<int:room_id>")
def delete_room(room_id):

    cursor = db.cursor()

    try:

        cursor.execute(
            "DELETE FROM rooms WHERE room_id = %s",
            (room_id,)
        )

        db.commit()

        message = "Room deleted successfully."

    except mysql.connector.IntegrityError:

        db.rollback()

        message = "Room cannot be deleted because it has an existing booking."

    cursor.close()

    return f"""
    <script>
        alert("{message}");
        window.location.href = "/rooms";
    </script>
    """
@app.route("/add_room", methods=["POST"])
def add_room():

    room_number = request.form["room_number"]
    room_type_id = request.form["room_type_id"]
    floor_number = request.form["floor_number"]
    room_status = request.form["room_status"]
    maintenance_status = request.form["maintenance_status"]

    cursor = db.cursor()

    # Generate the next Room ID
    cursor.execute("SELECT MAX(room_id) FROM rooms")
    max_id = cursor.fetchone()[0]

    room_id = max_id + 1

    query = """
        INSERT INTO rooms
        (room_id, room_number, room_type_id, floor_number,
         room_status, maintenance_status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    values = (
        room_id,
        room_number,
        room_type_id,
        floor_number,
        room_status,
        maintenance_status
    )

    cursor.execute(query, values)

    db.commit()

    cursor.close()

    return redirect("/rooms")
@app.route("/add_customer", methods=["POST"])
def add_customer():

    customer_id = 113

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    contact_number = request.form["contact_number"]
    city = request.form["city"]
    registration_date = request.form["registration_date"]
    gender = request.form["gender"]

    cursor = db.cursor()

    query = """
        INSERT INTO customers
        (customer_id, first_name, last_name, email, contact_number, city, registration_date, gender)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        customer_id,
        first_name,
        last_name,
        email,
        contact_number,
        city,
        registration_date,
        gender
    )

    cursor.execute(query, values)

    db.commit()

    cursor.close()

    return redirect("/customers")
    return redirect("/customers")


@app.route("/add_booking", methods=["POST"])
def add_booking():

    customer_id = request.form["customer_id"]
    room_id = request.form["room_id"]
    booking_date = request.form["booking_date"]
    check_in = request.form["check_in"]
    check_out = request.form["check_out"]
    number_of_guests = request.form["number_of_guests"]
    booking_status = request.form["booking_status"]

    cursor = db.cursor()

    cursor.execute("SELECT MAX(booking_id) FROM bookings")

    max_id = cursor.fetchone()[0]

    if max_id is None:
        booking_id = 301
    else:
        booking_id = max_id + 1

    query = """
        INSERT INTO bookings
        (booking_id, customer_id, room_id, booking_date,
         check_in, check_out, number_of_guests, booking_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        booking_id,
        customer_id,
        room_id,
        booking_date,
        check_in,
        check_out,
        number_of_guests,
        booking_status
    )

    cursor.execute(query, values)

    db.commit()

    cursor.close()

    return redirect("/bookings")
@app.route("/update_booking/<int:booking_id>", methods=["GET", "POST"])
def update_booking(booking_id):

    cursor = db.cursor()

    if request.method == "POST":

        customer_id = request.form["customer_id"]
        room_id = request.form["room_id"]
        booking_date = request.form["booking_date"]
        check_in = request.form["check_in"]
        check_out = request.form["check_out"]
        number_of_guests = request.form["number_of_guests"]
        booking_status = request.form["booking_status"]

        query = """
            UPDATE bookings
            SET customer_id = %s,
                room_id = %s,
                booking_date = %s,
                check_in = %s,
                check_out = %s,
                number_of_guests = %s,
                booking_status = %s
            WHERE booking_id = %s
        """

        values = (
            customer_id,
            room_id,
            booking_date,
            check_in,
            check_out,
            number_of_guests,
            booking_status,
            booking_id
        )

        cursor.execute(query, values)

        db.commit()

        cursor.close()

        return redirect("/bookings")


    cursor.execute(
        "SELECT * FROM bookings WHERE booking_id = %s",
        (booking_id,)
    )

    booking = cursor.fetchone()

    cursor.close()

    return render_template(
        "update_booking.html",
        booking=booking
    )


@app.route("/delete_booking/<int:booking_id>")
def delete_booking(booking_id):

    cursor = db.cursor()

    try:

        cursor.execute(
            "DELETE FROM bookings WHERE booking_id = %s",
            (booking_id,)
        )

        db.commit()

    except mysql.connector.IntegrityError:

        db.rollback()

        cursor.close()

        return """
        <script>
            alert("Cannot delete this booking because it is linked to another record.");
            window.location.href="/bookings";
        </script>
        """

    cursor.close()

    return redirect("/bookings")



if __name__ == "__main__":
    app.run(debug=True)
