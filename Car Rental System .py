import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3
import os
import json

# Database Initialization
CAR_DB = "cars.db"
CUSTOMER_DB = "customers.db"
JSON_BACKUP = "backup.json"

# Function to initialize the databases
def initialize_databases():
    # Initialize cars database
    conn = sqlite3.connect(CAR_DB)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cars (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        price_per_day INTEGER,
                        specs TEXT,
                        status TEXT,
                        image TEXT,
                        driver_name TEXT,
                        driver_reviews TEXT
                    )''')

    # Initialize customers database
    conn = sqlite3.connect(CUSTOMER_DB)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        contact TEXT,
                        car_id INTEGER,
                        rental_days INTEGER,
                        total_cost INTEGER,
                        experience_review TEXT,
                        FOREIGN KEY (car_id) REFERENCES cars (id)
                    )''')
    conn.commit()
    conn.close()

# Backup database to JSON file
def backup_to_json():
    data = {}

    # Backup cars database
    conn = sqlite3.connect(CAR_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars")
    cars = cursor.fetchall()
    data["cars"] = [
        {
            "id": car[0],
            "name": car[1],
            "price_per_day": car[2],
            "specs": car[3],
            "status": car[4],
            "image": car[5],
            "driver_name": car[6],
            "driver_reviews": car[7],
        }
        for car in cars
    ]
    conn.close()

    # Backup customers database
    conn = sqlite3.connect(CUSTOMER_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    data["customers"] = [
        {
            "id": customer[0],
            "name": customer[1],
            "contact": customer[2],
            "car_id": customer[3],
            "rental_days": customer[4],
            "total_cost": customer[5],
            "experience_review": customer[6],
        }
        for customer in customers
    ]
    conn.close()

    # Write to JSON file
    with open(JSON_BACKUP, "w") as f:
        json.dump(data, f, indent=4)

# Restore database from JSON file
def restore_from_json():
    if not os.path.exists(JSON_BACKUP):
        return

    with open(JSON_BACKUP, "r") as f:
        data = json.load(f)

    # Restore cars database
    conn = sqlite3.connect(CAR_DB)
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR REPLACE INTO cars (id, name, price_per_day, specs, status, image, driver_name, driver_reviews)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                car["id"],
                car["name"],
                car["price_per_day"],
                car["specs"],
                car["status"],
                car["image"],
                car["driver_name"],
                car["driver_reviews"],
            )
            for car in data["cars"]
        ],
    )
    conn.commit()
    conn.close()

    # Restore customers database
    conn = sqlite3.connect(CUSTOMER_DB)
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR REPLACE INTO customers (id, name, contact, car_id, rental_days, total_cost, experience_review)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                customer["id"],
                customer["name"],
                customer["contact"],
                customer["car_id"],
                customer["rental_days"],
                customer["total_cost"],
                customer["experience_review"],
            )
            for customer in data["customers"]
        ],
    )
    conn.commit()
    conn.close()

# Initialize the databases and restore data from JSON
initialize_databases()
restore_from_json()

# GUI Application
class CarRentalSystem:
    def _init_(self, root):
        self.root = root
        self.root.title("Car Rental Management System")
        self.root.geometry("900x600")
        self.root.configure(bg="#f8f9fa")

        # Admin credentials
        self.admin_username = "admin"
        self.admin_password = "password"

        # Title label
        title = tk.Label(
            self.root,
            text="Car Rental Management System",
            font=("Helvetica", 28, "bold"),
            bg="#4CAF50",
            fg="white",
            pady=15
        )
        title.pack(fill=tk.X)

        # Main buttons frame
        button_frame = tk.Frame(self.root, bg="#f8f9fa")
        button_frame.pack(pady=40)

        btn_view = tk.Button(
            button_frame,
            text="View Cars",
            font=("Helvetica", 14, "bold"),
            bg="#2196F3",
            fg="white",
            width=20,
            height=2,
            activebackground="#1976D2",
            activeforeground="white",
            command=self.view_cars
        )
        btn_view.grid(row=0, column=0, padx=30, pady=10)

        btn_admin = tk.Button(
            button_frame,
            text="Admin Portal",
            font=("Helvetica", 14, "bold"),
            bg="#9C27B0",
            fg="white",
            width=20,
            height=2,
            activebackground="#7B1FA2",
            activeforeground="white",
            command=self.admin_login
        )
        btn_admin.grid(row=0, column=1, padx=30, pady=10)

        btn_rent = tk.Button(
            button_frame,
            text="Rent a Car",
            font=("Helvetica", 14, "bold"),
            bg="#FF5722",
            fg="white",
            width=20,
            height=2,
            activebackground="#E64A19",
            activeforeground="white",
            command=self.rent_car
        )
        btn_rent.grid(row=1, column=0, padx=30, pady=10)

        btn_return = tk.Button(
            button_frame,
            text="Return Car",
            font=("Helvetica", 14, "bold"),
            bg="#FFC107",
            fg="black",
            width=20,
            height=2,
            activebackground="#FFB300",
            activeforeground="black",
            command=self.return_car
        )
        btn_return.grid(row=1, column=1, padx=30, pady=10)

        # Footer
        footer = tk.Label(
            self.root,
            text="© 2024 Car Rental Co. All rights reserved.",
            font=("Helvetica", 12, "italic"),
            bg="#4CAF50",
            fg="white",
            pady=10
        )
        footer.pack(side=tk.BOTTOM, fill=tk.X)

    def view_cars(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("Available Cars")
        view_window.geometry("800x400")

        def show_image(event):
            selected_item = tree.selection()
            if selected_item:
                car_id = tree.item(selected_item, "values")[0]
                conn = sqlite3.connect(CAR_DB)
                cursor = conn.cursor()
                cursor.execute("SELECT image FROM cars WHERE id = ?", (car_id,))
                car = cursor.fetchone()
                conn.close()

                if car and car[0] and os.path.exists(car[0]):
                    img = Image.open(car[0])
                    img = img.resize((200, 200), Image.ANTIALIAS)
                    img = ImageTk.PhotoImage(img)
                    image_label.configure(image=img)
                    image_label.image = img
                else:
                    image_label.configure(image="", text="No Image Available")

        tree = ttk.Treeview(view_window, columns=("ID", "Name", "Price/Day", "Specs", "Status", "Driver"), show='headings')
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Name")
        tree.heading("Price/Day", text="Price/Day")
        tree.heading("Specs", text="Specs")
        tree.heading("Status", text="Status")
        tree.heading("Driver", text="Driver")

        tree.column("ID", width=50)
        tree.column("Name", width=150)
        tree.column("Price/Day", width=100)
        tree.column("Specs", width=200)
        tree.column("Status", width=100)
        tree.column("Driver", width=150)

        tree.pack(fill=tk.BOTH, expand=True)

        conn = sqlite3.connect(CAR_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price_per_day, specs, status, driver_name FROM cars")
        cars = cursor.fetchall()
        conn.close()

        for car in cars:
            tree.insert("", tk.END, values=car)

        image_label = tk.Label(view_window, text="", font=("Helvetica", 12))
        image_label.pack(pady=10)

        tree.bind("<<TreeviewSelect>>", show_image)

    def admin_login(self):
        username = simpledialog.askstring("Admin Login", "Enter Username:")
        password = simpledialog.askstring("Admin Login", "Enter Password:", show="*")

        if username == self.admin_username and password == self.admin_password:
            self.admin_portal()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    def admin_portal(self):
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Portal")
        admin_window.geometry("800x400")

        def add_car():
            name = simpledialog.askstring("Add Car", "Car Name:")
            price = simpledialog.askinteger("Add Car", "Price per Day:")
            specs = simpledialog.askstring("Add Car", "Specifications:")
            driver_name = simpledialog.askstring("Add Car", "Driver Name:")

            image_path = filedialog.askopenfilename(title="Select Car Image", filetypes=[("Image Files", ".png;.jpg;*.jpeg")])

            conn = sqlite3.connect(CAR_DB)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cars (name, price_per_day, specs, status, image, driver_name) VALUES (?, ?, ?, ?, ?, ?)",
                           (name, price, specs, "Available", image_path, driver_name))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Car added successfully!")

        def remove_car():
            car_id = simpledialog.askinteger("Remove Car", "Enter Car ID to Remove:")

            conn = sqlite3.connect(CAR_DB)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Car removed successfully!")

        btn_add = tk.Button(admin_window, text="Add Car", font=("Helvetica", 14), bg="#4CAF50", fg="white", command=add_car)
        btn_add.pack(pady=10)

        btn_remove = tk.Button(admin_window, text="Remove Car", font=("Helvetica", 14), bg="#F44336", fg="white", command=remove_car)
        btn_remove.pack(pady=10)

    def rent_car(self):
        rent_window = tk.Toplevel(self.root)
        rent_window.title("Rent a Car")
        rent_window.geometry("400x400")

        name = simpledialog.askstring("Rent Car", "Your Name:")
        contact = simpledialog.askstring("Rent Car", "Your Contact:")
        car_id = simpledialog.askinteger("Rent Car", "Enter Car ID:")
        rental_days = simpledialog.askinteger("Rent Car", "Number of Days:")

        conn = sqlite3.connect(CAR_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT price_per_day, status FROM cars WHERE id = ?", (car_id,))
        car = cursor.fetchone()

        if not car:
            messagebox.showerror("Error", "Car not found!")
            return

        if car[1] != "Available":
            messagebox.showerror("Error", "Car is not available!")
            return

        total_cost = car[0] * rental_days
        cursor.execute("UPDATE cars SET status = ? WHERE id = ?", ("Rented", car_id))
        conn.commit()
        conn.close()

        conn = sqlite3.connect(CUSTOMER_DB)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO customers (name, contact, car_id, rental_days, total_cost) VALUES (?, ?, ?, ?, ?)",
                       (name, contact, car_id, rental_days, total_cost))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Car rented successfully! Total Cost: {total_cost}")

    def return_car(self):
        return_window = tk.Toplevel(self.root)
        return_window.title("Return Car")
        return_window.geometry("400x400")

        customer_id = simpledialog.askinteger("Return Car", "Enter Your Customer ID:")

        conn = sqlite3.connect(CUSTOMER_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT car_id, rental_days, total_cost FROM customers WHERE id = ?", (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            messagebox.showerror("Error", "Customer not found!")
            return

        car_id = customer[0]
        rental_days = customer[1]

        # Update car status to available
        conn = sqlite3.connect(CAR_DB)
        cursor = conn.cursor()
        cursor.execute("UPDATE cars SET status = ? WHERE id = ?", ("Available", car_id))
        conn.commit()
        conn.close()

        # Update customer's review
        review = simpledialog.askstring("Return Car", "Leave a review for the car:")
        cursor.execute("UPDATE customers SET experience_review = ? WHERE id = ?", (review, customer_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Car returned successfully. Thank you for your feedback!")

# Running the application
root = tk.Tk()
app = CarRentalSystem(root)
root.mainloop()


