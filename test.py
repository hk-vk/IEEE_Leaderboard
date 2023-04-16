import base64

# Input password to log in
passwd = input("Enter password to log in...")

# Initialize storage list and count variable
storage = []
count = 0

# Store each character of the password in the storage list
for i in passwd:
    storage.append(i)

# Extract 2nd and 7th characters and decode using base64
a1 = str(storage[1])
a2 = a1.encode("ascii")
a = str(base64.b64decode(a2)).strip("b'")

b1 = str(storage[6])
b2 = b1.encode("ascii")
b = str(base64.b64decode(b2)).strip("b'")

# Compare specific character values and update count
if len(passwd) != 8:
    print("Login Unsuccessful (length requirement not met)")
else:
    if ord(storage[0]) == 112 and ord(storage[7]) == 100:
        count += 2
    if a == "b'1'" and b == "b'0'":
        count += 2
    if ord(storage[2]) == 36 and ord(storage[3]) == 36:
        count += 2
    if ord(storage[4]) == 119 and storage[5] == "0":
        count += 2

# Check if password is correct based on count value
if count == 8:
    print("Login Successful with password : " + ''.join(storage))
else:
    print("Login Unsuccessful (Password Incorrect) ") decrpyt this script to find the password