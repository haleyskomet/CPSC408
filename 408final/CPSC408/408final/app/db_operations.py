import mysql.connector
from helper import helper

class db_operations():
    # constructor with connection path to DB
    def __init__(self):
        self.connection = mysql.connector.connect(host="localhost",
            user="root",
            password="CPSC408!",
            database='sportsLetterboxd')
        self.cursor = self.connection.cursor()
        self.in_transaction = False
        #print("connection made..")
        

    def begin_transaction(self):
        if self.in_transaction:
            raise Exception("Transaction already in progress")
        self.connection.start_transaction()
        self.in_transaction = True

    def commit_transaction(self):
        self.connection.commit()
        self.in_transaction = False

    def rollback_transaction(self):
        self.connection.rollback()
        self.in_transaction = False

    # function to simply execute a DDL or DML query.
    # commits query, returns no results. 
    # best used for insert/update/delete queries with no parameters
    def modify_query(self, query):
        self.cursor.execute(query)
        if not self.in_transaction:
            self.connection.commit()

    # function to simply execute a DDL or DML query with parameters
    # commits query, returns no results. 
    # best used for insert/update/delete queries with named placeholders
    def modify_query_params(self, query, params):
        self.cursor.execute(query, params)
        if not self.in_transaction:
            self.connection.commit()

    # function to simply execute a DQL query
    # does not commit, returns results
    # best used for select queries with no parameters
    def select_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    # function to simply execute a DQL query with parameters
    # does not commit, returns results
    # best used for select queries with named placeholders
    def select_query_params(self, query, dictionary):
        self.cursor.execute(query, dictionary)
        return self.cursor.fetchall()

    # function to return the value of the first row's 
    # first attribute of some select query.
    # best used for querying a single aggregate select 
    # query with no parameters
    def single_record(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]
    
    # function to return the value of the first row's 
    # first attribute of some select query.
    # best used for querying a single aggregate select 
    # query with named placeholders
    def single_record_params(self, query, dictionary):
        self.cursor.execute(query, dictionary)
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    # function to return a single attribute for all records 
    # from some table.
    # best used for select statements with no parameters
    def single_attribute(self, query):
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        results = [i[0] for i in results]
        results.remove(None)
        return results
    
    # function to return a single attribute for all records 
    # from some table.
    # best used for select statements with named placeholders
    def single_attribute_params(self, query, dictionary):
        self.cursor.execute(query,dictionary)
        results = self.cursor.fetchall()
        results = [i[0] for i in results]
        return results
    
    
    # function for bulk inserting records
    # best used for inserting many records with parameters
    def bulk_insert(self, query, data):
        self.cursor.executemany(query, data)
        self.connection.commit()

    # destructor that closes connection with DB
    def destructor(self):
        self.cursor.close()
        self.connection.close()