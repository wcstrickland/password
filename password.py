#!/bin/python3

import getpass
import psycopg2
from Crypto.Cipher import AES
import hashlib



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
            clear_pass = decrypt_pass(master_password, bytes(row[2]))
            clear_pass = clear_pass.decode('UTF-8')
            print(f"service: {row[0]} username: {row[1]}\nPASSWORD: {clear_pass}")
    except (Exception, psycopg2.DatabaseError) as error:
        print("error retrieving password table: ", error)


def add_password():
    service = input("What is the name of the service? ")
    username = input("What is the username associated with the service? ")
    password = encrypt_pass()
    
    try:
        cur.execute("insert into password(service, username, password) values (%s, %s, %s)", (service, username, password ))
        conn.commit()
        print("\nPassword inserted successfully!\n")
    except (Exception, psycopg2.DatabaseError) as error:
        print("error adding new passord: ", error)
    
def encrypt_pass():
    encrypted_password = getpass.getpass("Please enter the password associated with this service: ")
    return encryptor.encrypt(encrypted_password)

def decrypt_pass(master_password, password):
    decryptor = AES.new(master_password, AES.MODE_CFB, 'This is an IV456') 
    clear_text = decryptor.decrypt(password)
    return clear_text
    
    


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

    if not first_time:
        master_password = getpass.getpass("\nEnter your master password: ")
    else:
        master_password = getpass.getpass("\nEnter the master password you will use from now on : ")

    hassher = hashlib.sha256()
    bytes_passwd = master_password.encode('UTF-8')
    hassher.update(bytes_passwd)
    hashed_passwd = hassher.digest()
    encryptor = AES.new(hashed_passwd, AES.MODE_CFB, 'This is an IV456')

    first_time = False

    try:
        cur.execute("select * from password")
    except:
        first_time = True
        pass

    conn.commit()

    try:
        cur.execute("create table password (service varchar(255), username varchar(255), password bytea )")
        sanity_check = ciphertext = encryptor.encrypt("sanity_check")
        cur.execute("insert into password (service, username, password) values (%s, %s, %s)", ("1d8c21bb-eba2-45bc-b3c0-f790c3c0c334", "1d8c21bb-eba2-45bc-b3c0-f790c3c0c334", sanity_check))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        pass
    
    conn.commit()

    cur.execute("select * from password")
    first_row_check = cur.fetchone()
    check_sanity = decrypt_pass(hashed_passwd, bytes(first_row_check[2]))
    if check_sanity != b'sanity_check':
        print("*"*40)
        print("\nThat is not the password!\n")
        print("*"*40)
        quit()
    else:
        print("\nSuccess!!!\n")
    

    

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
            desired_service = input("what service do you want the password for? ") 
            get_password(hashed_passwd, desired_service)
        if user_input == "3":
            add_password()
            
    cur.close()
    conn.close()
