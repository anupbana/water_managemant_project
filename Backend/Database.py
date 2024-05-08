# Database.py
import mysql.connector
import pandas as pd

class SQLDatabase:
    def __init__(self, host, username, password, database):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                passwd=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print("Connected to MySQL database.")

        except mysql.connector.Error as error:
            print("Error connecting to MySQL database:", error)

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from MySQL database.")
        else:
            print("Not connected to any MySQL database.")

    def read_data(self, sql_query, params=None):
        try:
            self.cursor.execute(sql_query, params)
            rows = self.cursor.fetchall()
            column_names = [desc[0] for desc in self.cursor.description]
            df = pd.DataFrame(rows, columns=column_names)
            return df

        except mysql.connector.Error as error:
            print("Failed to fetch data from MySQL table:", error)

    def insert_data(self, df, table_name):
        try:
            insert_query = f"INSERT IGNORE INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s']*len(df.columns))})"
            for i, row in df.iterrows():
                self.cursor.execute(insert_query, tuple(row))
            self.connection.commit()
            print("DataFrame successfully written to MySQL table.")
            return True

        except mysql.connector.Error as error:
            print("Error writing DataFrame to MySQL table:", error)
            return False
        
    def delete_data(self, delete_query):
        try:
            self.cursor.execute(delete_query)
            self.connection.commit()
            print("Data successfully deleted from MySQL table.")
            return True

        except mysql.connector.Error as error:
            print("Error deleting data from MySQL table:", error)
            return False
