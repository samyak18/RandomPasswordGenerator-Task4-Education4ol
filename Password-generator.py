import random
import string
import mysql.connector
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta
import openpyxl

# Initialize password history
password_history = []

def generate_password(words):
    combined_words = ''.join(words)
    password_list = random.sample(combined_words, len(combined_words))
    password = ''.join(password_list)
    return password

def generate_password_from_choices(choices, length):
    characters = ''
    if 'uppercase' in choices:
        characters += string.ascii_uppercase
    if 'lowercase' in choices:
        characters += string.ascii_lowercase
    if 'digits' in choices:
        characters += string.digits
    if 'special' in choices:
        characters += string.punctuation
    if not characters:
        return None
    
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def check_password_strength(password):
    if len(password) >= 8 and any(c.islower() for c in password) and any(c.isupper() for c in password) and any(c.isdigit() for c in password):
        return "strong"
    elif len(password) >= 6:
        return "moderate"
    else:
        return "weak"

def save_to_text_file(password):
    with open('generated_password.txt', 'w') as file:
        file.write(password)

def save_to_database(words, password, strength, expiry_date):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='Samyak',   
            password='SamyakKumar@200418',  
            database='password'   
        )

        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
                          (id INT AUTO_INCREMENT PRIMARY KEY,
                          words TEXT,
                          generated_password TEXT,
                          strength TEXT,
                          expiry_date DATE)''')
        cursor.execute('''INSERT INTO passwords (words, generated_password, strength, expiry_date)
                          VALUES (%s, %s, %s, %s)''', (', '.join(words), password, strength, expiry_date))
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        messagebox.showerror("Database Error", f"An error occurred while connecting to the database:\n{err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def save_to_excel(words, password, strength, expiry_date):
    try:
        workbook = openpyxl.load_workbook('passwords.xlsx')
        sheet = workbook.active
    except FileNotFoundError:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["Words", "Generated Password", "Strength", "Expiry Date"])

    sheet.append([', '.join(words), password, strength, expiry_date.strftime('%Y-%m-%d')])
    workbook.save('passwords.xlsx')

def add_to_password_history(password, expiry_date):
    password_history.append((password, expiry_date))

def generate_password_and_show():
    choices = []
    if simpledialog.askstring("Input", "Include uppercase letters? (yes/no)").lower() == "yes":
        choices.append("uppercase")
    if simpledialog.askstring("Input", "Include lowercase letters? (yes/no)").lower() == "yes":
        choices.append("lowercase")
    if simpledialog.askstring("Input", "Include numbers? (yes/no)").lower() == "yes":
        choices.append("digits")
    if simpledialog.askstring("Input", "Include special characters? (yes/no)").lower() == "yes":
        choices.append("special")
    
    words = entry_words.get().split()
    length = simpledialog.askinteger("Input", "Enter the length of the password")
    password = generate_password_from_choices(choices, length)
    
    if password is None:
        messagebox.showerror("Error", "No characters selected for password generation.")
        return
    
    strength = check_password_strength(password)
    save_to_text_file(password)
    
    expiry_days = simpledialog.askinteger("Input", "Enter the number of days before the password expires")
    expiry_date = (datetime.now() + timedelta(days=expiry_days)).date()

    save_to_database(words, password, strength, expiry_date)
    save_to_excel(words, password, strength, expiry_date)
    add_to_password_history(password, expiry_date)
    
    display_window = tk.Toplevel(root)
    display_window.title("Generated Password")
    display_window.geometry("300x200")
    
    label_password = tk.Label(display_window, text=f"Generated password: {password}")
    label_password.pack(pady=10)
    
    label_strength = tk.Label(display_window, text=f"Password strength: {strength}")
    label_strength.pack(pady=5)
    
    label_expiry = tk.Label(display_window, text=f"Password expiry date: {expiry_date}")
    label_expiry.pack(pady=5)

    button_close = tk.Button(display_window, text="Close", command=display_window.destroy)
    button_close.pack(pady=10)

    entry_words.delete(0, tk.END)

def show_password_history():
    history_window = tk.Toplevel(root)
    history_window.title("Password History")
    history_window.geometry("300x200")
    
    for password, expiry_date in password_history:
        label = tk.Label(history_window, text=f"Password: {password} (Expires on: {expiry_date})")
        label.pack(pady=5)
    
    button_close = tk.Button(history_window, text="Close", command=history_window.destroy)
    button_close.pack(pady=10)

root = tk.Tk()
root.title("Password Generator")

label_instructions = tk.Label(root, text="Enter some words separated by spaces:")
label_instructions.pack(pady=10)

entry_words = tk.Entry(root, width=50)
entry_words.pack(pady=10)

button_generate = tk.Button(root, text="Generate Password", command=generate_password_and_show)
button_generate.pack(pady=10)

button_history = tk.Button(root, text="Show Password History", command=show_password_history)
button_history.pack(pady=10)

root.mainloop()
