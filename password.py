#!/bin/python3

import random
from uuid import uuid4
import sqlite3
import getpass
import cryptocode
from tkinter import Tk

def list_all():
    try:
        print("\n","*"*40,"\n")
        rows = []
        cur.execute("select service, username from password")
        cur.fetchone()
        while True:
            row = cur.fetchone()
            if row:
                rows.append(row)
            else:
                break
        if len(rows)>0:
            for row in rows:
                pad = 22 - len(row[0])
                spacer = " "*pad
                print(f"SERVICE: {row[0]} {spacer} USERNAME: {row[1]}")
        print("\n","*"*40)
        input("press any key to continue: ")
    except (Exception) as error:
        print("error retrieving password table: ", error)


def get_password(master_password, service):
    try:
        print()
        cur.execute("select * from password where service=:service", {"service":service})
        rows = cur.fetchall()
        for row in rows:
            clear_pass = cryptocode.decrypt(row[2], master_password)
            pad = 22 - len(row[0])
            spacer = " "*pad
            print(f"service: {row[0]}\nusername: {row[1]}\n\nPASSWORD: {clear_pass}")
            r = Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(clear_pass)
            r.update() # now it stays on the clipboard after the window is closed
            print("\nThis password has been copied to your clipboard \n")
            input("press any key to continue: ")
    except (Exception) as error:
        print("error retrieving password table: ", error)


def add_password():
    service = input("\nPress 0 to go back.\nWhat is the name of the service? ")
    if service == "0":
        return
    username = input("\nPress 0 to go back.\nWhat is the username associated with the service? ")
    if username == "0":
        return
    password = encrypt_pass()
    
    try:
        cur.execute("insert into password(service, username, password) values (?, ?, ?)", (service, username, password ))
        conn.commit()
        print("\nPassword inserted successfully!\n")
        input("press any key to continue: ")
    except (Exception) as error:
        print("error adding new password: ", error)

def remove_password():
    service = input("\nPress 0 to go back.\nWhat is the name of the service you want to delete? ")
    if service == "0":
        return
    try:
        cur.execute("delete from password where service=:service", {"service":service})
    except (Exception) as error:
        print("error removing password: ", error)
    conn.commit()
    print("\nPassword removed\n")
    input("press any key to continue: ")
    
def encrypt_pass():
    symbol_choices = ["#", "!", "$", "_"]
    while True:
        generate_password = input("\nDo you want a unique generated password? y or n :")
        if generate_password == "n":
            clear_password = getpass.getpass("\nPlease enter the password associated with this service: ")
            break
        elif generate_password == "y":
            clear_password = str(uuid4())
            clear_password = clear_password[:11]
            clear_password = clear_password.replace("-", random.choice(symbol_choices))
            clear_password = [char for char in clear_password]
            random_number = random.randint(0,7)
            clear_password[random_number] = clear_password[random_number].upper()
            random_number = random.randint(0,7)
            clear_password[random_number] = clear_password[random_number].upper()
            clear_password = "".join(clear_password)
            print(f"\nYour password will be {clear_password}")
            break

    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(clear_password)
    r.update() # now it stays on the clipboard after the window is closed
    print("\n\nYour password has been copied to the clipboard\n")
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
    

valid_choices = ["0", "1", "2", "3", "4"]

if __name__ == '__main__':


    conn = sqlite3.connect('password.db')
    cur = conn.cursor()

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
            cur.execute("create table password (service text, username text, password text )")
            conn.commit()
        except (Exception) as error:
            pass

    conn.commit()

    if first_time:
        try:
            sanity_check = cryptocode.encrypt("1d8c21bb-eba2-45bc-b3c0-f790c3c0c334", master_password)
            cur.execute("insert into password (service, username, password) values (?, ?, ?)", ("1d8c21bb-eba2-45bc-b3c0-f790c3c0c334", "1d8c21bb-eba2-45bc-b3c0-f790c3c0c334", sanity_check))
            conn.commit()
            print("\nSuccess!!\n")
        except (Exception) as error:
            pass

    
    conn.commit()

    

    while True:
        print("""
    Please select an option:
    list all accounts : 1
    retrieve a password: 2
    add a new password: 3
    remove a password: 4
    quit: 0
    """)
        user_input = input("\t: ")
        if user_input not in valid_choices:
            print("\nThat is not valid input\n")
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
        if user_input == "4":
            remove_password()
            
    cur.close()
    conn.close()
