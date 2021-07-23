import cryptocode
import getpass

master_pass = getpass.getpass("enter master password: ")

plain_text = input("enter text for encodiing: ")

encoded = cryptocode.encrypt(plain_text, master_pass)
print(type(encoded))
print("\n", encoded, "\n")

decoded = cryptocode.decrypt(encoded, master_pass)

print('\n', decoded, '\n')
