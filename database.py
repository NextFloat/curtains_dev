import sqlite3
import os


database_name = os.getcwd() + 'config.db'
# Connect to the database
conn = sqlite3.connect(database_name, check_same_thread=False)


# Create a cursor
cursor = conn.cursor()

# Create the table with the PRIMARY KEY constraint
cursor.execute("CREATE TABLE IF NOT EXISTS locked_procs (proc_path TEXT PRIMARY KEY, hidden BOOL, icon BLOB)")
# Commit the changes
conn.commit()


def get_row(proc_path):
    # Execute the SELECT statement
    cursor.execute("SELECT * FROM locked_procs WHERE proc_path=?", (proc_path,))

    # Fetch the row
    row = cursor.fetchone()
    locked_proc = {row[0]:{'hidden':row[1], 'icon':row[2]}}
    return locked_proc

def add_row(proc_path, hidden, icon):
    # Execute the INSERT statement
    cursor.execute("INSERT INTO locked_procs (proc_path, hidden, icon) VALUES (?, ?, ?)", (proc_path, hidden, icon))

    # Commit the changes
    conn.commit()

def delete_row(proc_path):
    # Execute the DELETE statement
    cursor.execute("DELETE FROM locked_procs WHERE proc_path=?", (proc_path,))

    # Commit the changes
    conn.commit()

def update_hidden(proc_path, hidden):
    # Update the row
    cursor.execute("UPDATE locked_procs SET hidden = ? WHERE proc_path = ?", (hidden, proc_path))

    # Commit the changes
    conn.commit()

def read_table():
    cursor.execute("SELECT * FROM locked_procs")

    # Fetch all rows
    rows = cursor.fetchall()

    locked_procs = {}
    for row in rows:
        locked_procs[row[0]] = {'hidden':bool(row[1]), 'icon':row[2]}
    return locked_procs
