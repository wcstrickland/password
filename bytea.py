from Crypto.Cipher import AES
from getpass import getpass
import hashlib
import psycopg2
from password import db_connect
from password import opts


hassher = hashlib.sha256()
passwd = getpass("enter the passphrase: ") 
bytes_passwd = passwd.encode('UTF-8')
hassher.update(bytes_passwd)
hashed_passwd = hassher.digest()

encryptor = AES.new(hashed_passwd, AES.MODE_CFB, 'This is an IV456')
message = input("enter the message: ")
ciphertext = encryptor.encrypt(message)
print(ciphertext)
decryptor = AES.new(hashed_passwd, AES.MODE_CFB, 'This is an IV456')
#clear_text = decryptor.decrypt(ciphertext)
#print(clear_text)




nopts = opts
nopts["password"] = "ThirtyFour12"

cur, conn = db_connect(nopts)

try:
    cur.execute("insert into bytess(name, bytess) values (%s, %s)", ("test value", ciphertext))
    conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print("error inserting into bytea  table: ", error)


try:
    cur.execute("select * from bytess")
    row = cur.fetchone()
    print(row)
except (Exception, psycopg2.DatabaseError) as error:
    print("error getting from  bytea  table: ", error)

print(decryptor.decrypt(bytes(row[1])))
