import os
import sqlite3
import traceback

dir_path = os.path.join(os.environ['APPDATA'], 'Curtains')
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
FILEPATH = os.path.join(dir_path, 'config.db')


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(FILEPATH, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS processes (proc_path TEXT PRIMARY KEY, hidden BOOL, icon BLOB)")
        self.conn.commit()

    def get_row(self, proc_path):
        # Execute the SELECT statement
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM processes WHERE proc_path=?", (proc_path,))
        # Fetch the row
        row = cursor.fetchone()
        if row:
            return row
        else:
            return None

    def add_row(self, proc_path, hidden, icon):
        try:
            # Execute the INSERT statement
            self.conn.execute("INSERT OR IGNORE INTO processes (proc_path, hidden, icon) VALUES (?, ?, ?)",
                              (proc_path, hidden, icon))
        except Exception:
            print(traceback.format_exc())
        # Commit the changes
        self.conn.commit()

    def delete_row(self, proc_path):
        # Execute the DELETE statement
        self.conn.execute("DELETE FROM processes WHERE proc_path=?", (proc_path,))

        # Commit the changes
        self.conn.commit()

    def update_hidden(self, proc_path, hidden):
        # Update the row
        self.conn.execute("UPDATE processes SET hidden = ? WHERE proc_path = ?", (hidden, proc_path))

        # Commit the changes
        self.conn.commit()

    def close(self, ):
        self.conn.close()
