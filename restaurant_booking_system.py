import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime

class Restaurant:
    def __init__(self, restaurant_id, name, cuisine_type, rating, location, total_tables, table_configuration, opening_hours, closing_hours):
        self.restaurant_id = restaurant_id
        self.name = name
        self.cuisine_type = cuisine_type
        self.rating = float(rating)
        self.location = location
        self.total_tables = int(total_tables)
        self.table_configuration = table_configuration
        self.opening_hours = opening_hours
        self.closing_hours = closing_hours

    def get_available_tables(self, date, time, party_size):
        with open('bookings.csv', 'r') as file:
            bookings = list(csv.reader(file))
            available_tables = self.total_tables
            for booking in bookings[1:]:  # Skip header
                if (booking[2] == self.restaurant_id and
                        booking[4] == date and
                        booking[5] == time):
                    available_tables -= 1
            return max(0, available_tables)

    def check_valid_booking_time(self, time):
        booking_time = datetime.strptime(time, "%H:%M")
        opening_time = datetime.strptime(self.opening_hours, "%H:%M")
        closing_time = datetime.strptime(self.closing_hours, "%H:%M")
        return opening_time <= booking_time <= closing_time

    def display_restaurant_info(self):
        return f"{self.name} - {self.cuisine_type} - Rating: {self.rating}/5 - Location: {self.location}"

class User:
    def __init__(self, user_id, name, email, phone_number, current_bookings=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.current_bookings = current_bookings if current_bookings else []

    def make_reservation(self, restaurant_id, date, time, table_id, party_size):
        with open('bookings.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            booking_id = len(self.current_bookings) + 1
            writer.writerow([booking_id, self.user_id, restaurant_id, table_id, date, time, party_size])
            self.current_bookings.append((booking_id, restaurant_id, date, time, table_id, party_size))

    def cancel_reservation(self, booking_id):
        with open('bookings.csv', 'r') as file:
            bookings = list(csv.reader(file))

        with open('bookings.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["booking_id", "user_id", "restaurant", "table_id", "date", "time", "party_size"])
            for booking in bookings[1:]:  # Skip header
                if booking[0] != str(booking_id):
                    writer.writerow(booking)
                else:
                    self.current_bookings = [b for b in self.current_bookings if b[0] != booking_id]

    def view_booking_history(self):
        with open('bookings.csv', 'r') as file:
            bookings = list(csv.reader(file))
            return [booking for booking in bookings[1:] if booking[1] == self.user_id]  # Skip header

class RestaurantBookingApp:
    def __init__(self, master):
        self.master = master
        master.title("Restaurant Booking System")

        self.restaurants = self.load_restaurants()
        self.users = self.load_users()
        self.current_user = None  # Placeholder for the logged-in user
        self.create_widgets()

    def load_restaurants(self):
        restaurants = []
        with open('restaurants.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                restaurants.append(Restaurant(
                    row['restaurant_id'],  # restaurant_id
                    row['name'],
                    row['cuisine_type'],
                    row['rating'],
                    row['location'],
                    row['total_tables'],
                    eval(row['table_configuration']),  # Convert string representation to list
                    row['opening_hours'],
                    row['closing_hours']
                ))
        return restaurants

    def load_users(self):
        users = []
        with open('users.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users.append(User(
                    row['user_id'],
                    row['name'],
                    row['email'],
                    row['phone_number'],
                    eval(row['current_bookings'])  # Convert string representation to list
                ))
        return users

    def login_user(self):
        login_window = tk.Toplevel(self.master)
        login_window.title("User Login")

        tk.Label(login_window, text="User ID:").pack()
        user_id_entry = tk.Entry(login_window)
        user_id_entry.pack()

        def confirm_login():
            user_id = user_id_entry.get()
            self.current_user = next((user for user in self.users if user.user_id == user_id), None)
            if self.current_user:
                messagebox.showinfo("Login Success", f"Welcome {self.current_user.name}!")
                login_window.destroy()
            else:
                messagebox.showerror("Login Error", "Invalid User ID.")

        tk.Button(login_window, text="Login", command=confirm_login).pack(pady=10)

    def create_widgets(self):
        # Main label
        self.label = tk.Label(self.master, text="Welcome to the Restaurant Booking System", font=("Arial", 16))
        self.label.pack(pady=10)

        # Login button
        self.login_button = tk.Button(self.master, text="Login", command=self.login_user)
        self.login_button.pack(pady=10)

        # Restaurant list section
        self.restaurant_list = ttk.Treeview(self.master, columns=("Cuisine", "Rating", "Location"), show='headings')
        self.restaurant_list.heading("Cuisine", text="Cuisine Type")
        self.restaurant_list.heading("Rating", text="Rating")
        self.restaurant_list.heading("Location", text="Location")
        self.restaurant_list.pack(fill=tk.BOTH, expand=True, pady=10)

        for restaurant in self.restaurants:
            self.restaurant_list.insert("", "end", values=(
                restaurant.name, restaurant.cuisine_type, restaurant.rating, restaurant.location
            ))

        # Booking button
        self.booking_button = tk.Button(self.master, text="Make a Reservation", command=self.make_reservation)
        self.booking_button.pack(pady=10)

        # Cancellation button
        self.cancellation_button = tk.Button(self.master, text="Cancel Reservation", command=self.show_cancellation_page)
        self.cancellation_button.pack(pady=10)

    def make_reservation(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please log in to make a reservation.")
            return

        selected_item = self.restaurant_list.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a restaurant to make a reservation.")
            return

        selected_restaurant = self.restaurant_list.item(selected_item)['values']
        reservation_window = tk.Toplevel(self.master)
        reservation_window.title(f"Reserve at {selected_restaurant[0]}")

        tk.Label(reservation_window, text="Date (YYYY-MM-DD):").pack()
        date_entry = tk.Entry(reservation_window)
        date_entry.pack()

        tk.Label(reservation_window, text="Time (HH:MM):").pack()
        time_entry = tk.Entry(reservation_window)
        time_entry.pack()

        tk.Label(reservation_window, text="Party Size:").pack()
        party_size_entry = tk.Entry(reservation_window)
        party_size_entry.pack()

        def confirm_booking():
            date = date_entry.get()
            time = time_entry.get()
            party_size = party_size_entry.get()

            try:
                restaurant = next(r for r in self.restaurants if r.name == selected_restaurant[0])
                if not restaurant.check_valid_booking_time(time):
                    raise ValueError("Invalid booking time.")

                available_tables = restaurant.get_available_tables(date, time, int(party_size))
                if available_tables <= 0:
                    raise ValueError("No tables available for the selected time.")

                self.current_user.make_reservation(restaurant.restaurant_id, date, time, 1, party_size)  # Example table ID
                messagebox.showinfo("Success", "Reservation made successfully!")
                reservation_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(reservation_window, text="Confirm", command=confirm_booking).pack(pady=10)

    def show_cancellation_page(self):
        # Create a new frame for cancellation
        cancellation_frame = tk.Frame(self.master)
        cancellation_frame.pack(pady=20)

        # Cancellation message
        cancellation_label = tk.Label(cancellation_frame, text="Your reservation has been cancelled.")
        cancellation_label.pack(pady=10)

        # Confirm cancellation button
        confirm_button = tk.Button(cancellation_frame, text="Confirm", command=self.confirm_cancellation)
        confirm_button.pack(pady=5)

        # Back button
        back_button = tk.Button(cancellation_frame, text="Back to Main Menu", command=self.show_main_menu)
        back_button.pack(pady=5)

        # Hide other frames
        self.hide_all_frames()
        cancellation_frame.pack()

    def confirm_cancellation(self):
        # Logic to confirm cancellation
        messagebox.showinfo("Cancellation", "Your reservation has been confirmed as cancelled.")

    def show_main_menu(self):
        # Logic to show the main menu
        messagebox.showinfo("Main Menu", "Returning to the main menu.")

    def hide_all_frames(self):
        for widget in self.master.winfo_children():
            widget.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantBookingApp(root)
    root.mainloop()