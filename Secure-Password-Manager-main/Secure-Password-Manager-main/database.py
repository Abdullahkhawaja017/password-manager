import sqlite3

# ---------------------------------------
# Helper function to connect to database
# ---------------------------------------
def get_connection():
    return sqlite3.connect("passwords.db")


# ---------------------------------------
# Create Tables (run once)
# ---------------------------------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        master_password TEXT NOT NULL
    )
    """)

    # Create Passwords table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        notes TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------
# Add new password entry
# ---------------------------------------
def add_password(service, username, password, notes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO passwords (service, username, password, notes)
        VALUES (?, ?, ?, ?)
    """, (service, username, password, notes))

    conn.commit()
    conn.close()


# ---------------------------------------
# Get all saved passwords
# ---------------------------------------
def get_all_passwords():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM passwords")
    rows = cursor.fetchall()

    conn.close()
    return rows


# ---------------------------------------
# Search passwords by service name
# ---------------------------------------
def search_passwords(service_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM passwords WHERE service LIKE ?", ("%" + service_name + "%",))
    rows = cursor.fetchall()

    conn.close()
    return rows


# ---------------------------------------
# Update a password entry by ID
# ---------------------------------------
def update_password(id, new_service, new_username, new_password, new_notes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE passwords
        SET service = ?, username = ?, password = ?, notes = ?
        WHERE id = ?
    """, (new_service, new_username, new_password, new_notes, id))

    conn.commit()
    conn.close()


# ---------------------------------------
# Delete a password entry by ID
# ---------------------------------------
def delete_password(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM passwords WHERE id = ?", (id,))

    conn.commit()
    conn.close()


# ---------------------------------------
# Get all users
# ---------------------------------------
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------------------------------------
# Update master password for a user
# ---------------------------------------
def update_master_password(user_id, new_hashed_pw):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET master_password = ? WHERE id = ?", (new_hashed_pw, user_id))
    conn.commit()
    conn.close()



# ---------------------------------------
# Run table creation when file starts
# ---------------------------------------
if __name__ == "__main__":
    create_tables()
    print("Database and tables ready!")
