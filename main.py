import getpass
import psycopg2


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
        print("Database connected:")
    except (Exception, psycopg2.DatabaseError) as error:
        print("error connecting to db : ", error)
    return cur, conn


def list_all():
    try:
        cur.execute("select (service, username) from password")
        rows = cur.fetchall()
        for row in rows:
            print(f"service: {row[0]} username: {row[1]}")
    except (Exception, psycopg2.DatabaseError) as error:
        print("error retrieving password table: ", error)


def get_password(service):
    try:
        cur.execute(f"select * from password where service='{service}'")
        rows = cur.fetchall()
        for row in rows:
            print(f"service: {row[0]} username: {row[1]}")
    except (Exception, psycopg2.DatabaseError) as error:
        print("error retrieving password table: ", error)


def add_password():
    service = input("What is the name of the service? ")
    username = input("What is the username associated with the service? ")
    password = getpass.getpass("Please enter the password associated with this service: ")
    try:
        cur.execute("insert into password(service, username, password) values (%s, %s, %s)", (service, username, password))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("error adding new passord: ", error)
    
    



opts = {
    "host":"localhost",
    "database":"password",
    "user":"postgres"
}

valid_choices = ["0", "1", "2", "3"]

opts["password"] = getpass.getpass("Enter master password: ")

cur, conn = db_connect(opts)

try:
    cur.execute("create table if not exists passwords (service varchar(255), username varchar(255), password varchar(255))")
    conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print("error creating password table: ", error)

while True:
    print("""
Please select an option:
list all accounts : 1
retrieve a password: 2
add a new password: 3
quit: 0
""")
    user_input = input()
    if user_input not in valid_choices:
        print("That is not valid input")
        continue
    if user_input == "0":
        break
    if user_input == "1":
        list_all()
    if user_input == "2":
        desired_service = input("what account do you want the password for? ") 
        get_password(desired_service)
    if user_input == "3":
        add_password()
        
    
