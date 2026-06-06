# import database
# conn = database.get_connection()
# conn.cursor().execute("DELETE FROM users")
# conn.commit()
# print("User cleared. You can now re-register with the new security.")


import database

# Connect and clear the users table
conn = database.get_connection()
cursor = conn.cursor()
cursor.execute("DELETE FROM users")
conn.commit()
conn.close()

print("User database cleared. Now run ui_login.py again.")