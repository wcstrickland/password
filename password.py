#!/bin/python3

import getpass
import psycopg2
from Crypto.Cipher import AES
import hashlib
import cryptocode



def db_connect(params):
    """ 
    params dictionary {
        "host":"*******",
        "database":"*******",
        "user":"*******"
    }

    """
    print("Connecting to Postgres DB")    
    try:
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        print(cur.fetchone())
        print("\nDatabase connected!\n")
    except (Exception, psycopg2.DatabaseError) as error:
        print("error connecting to db : ", error)
    return cur, conn


def list_all():
    try:
        print()
        print("*"*40,"\n")
        rows = []
        cur.execute("select (service, username) from password")
        cur.fetchone()
        while True:
            row = cur.fetchone()
            if row:
                rows.append(row)
            else:
                break
        for row in rows:
            fields = row[0].strip("()").split(",")
            print(f"SERVICE: {fields[0]} \t USERNAME: {fields[1]}")
        print()
        print("*"*40)
    except (Exception, psycopg2.DatabaseError) as error:
        print("error retrieving password table: ", error)


def get_password(master_password, service):
    try:
        print()
        cur.execute(f"select * from password where service='{service}'")
        rows = cur.fetchall()
        for row in rows:
            clear_pass = cryptocode.decrypt(row[2], master_password)
            print(f"service: {row[0]} username: {row[1]}\nPASSWORD: {clear_pass}")
    except (Exception, psycopg2.DatabaseError) as error:
        print("error retrieving password table: ", error)


def add_password():
    service = input("\nPress 0 to go back.\nWhat is the name of the service? ")
    if service == "0":
        return
    username = input("\nPress 0 to go back.\nWhat is the username associated with the service? ")
    if username == "0":
        add_password()
    password = encrypt_pass()
    
    try:
        cur.execute("insert into password(service, username, password) values (%s, %s, %s)", (service, username, password ))
        conn.commit()
        print("\nPassword inserted successfully!\n")
    except (Exception, psycopg2.DatabaseError) as error:
        print("error adding new password: ", error)
    
def encrypt_pass():
    clear_password = getpass.getpass("Please enter the password associated with this service: ")
    return cryptocode.encrypt(clear_password, master_password)

def decrypt_pass(password):
    return cryptocode.decrypt(password, master_password)

def sanity_check():
    while True:
        master_password = getpass.getpass("\nEnter your master password: ")
        cur.execute("select * from password")
        first_row_check = cur.fetchone()
        check_sanity = cryptocode.decrypt(first_row_check[2], master_password)
        if check_sanity != "1d8c21bb-eba2-45bc-b3c0-f790c3c0c334":
            print("*"*40)
            print("\nThat is not the password!\n")
            print("*"*40)
        else:
            print("\nSuccess!!!\n")
            return master_password
    
    


db_opts = {
    "host":"localhost",
    "database":"password",
    "user":"postgres"
}

valid_choices = ["0", "1", "2", "3"]

if __name__ == '__main__':

    db_opts["password"] = getpass.getpass("Enter database password: ")
    cur, conn = db_connect(db_opts)

    first_time = False

    try:
        cur.execute("select * from password")
    except:
        first_time = True
        pass

    conn.commit()

    if not first_time:
        master_password = sanity_check()
    else:
        master_password = getpass.getpass("\nEnter the master password you will use from now on : ")
        try:
            cur.execute("create table password (service varchar(255), username varchar(255), password varchar(255))")
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            pass

    conn.commit()

    try:
        sanity_check = cryptocode.encrypt("1d8c21bb-eba2-45bc-b3c0-f790c3c0c334", master_password)
        cur.execute("insert into password (service, username, password) values (%s, %s, %s)", ("1d8c21bb-eba2-45bc-b3c0-f790c3c0c334", "1d8c21bb-eba2-45bc-b3c0-f790c3c0c334", sanity_check))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        pass

    
    conn.commit()

    

    while True:
        print("""
    Please select an option:
    list all accounts : 1
    retrieve a password: 2
    add a new password: 3
    quit: 0
    """)
        user_input = input("\t: ")
        if user_input not in valid_choices:
            print("That is not valid input\n")
            continue
        if user_input == "0":
            break
        if user_input == "1":
            list_all()
        if user_input == "2":
            desired_service = input("\nEnter 0 to go back.\nwhat service do you want the password for? ") 
            if desired_service == "0":
                continue
            get_password(master_password, desired_service)
        if user_input == "3":
            add_password()
            
    cur.close()
    conn.close()
