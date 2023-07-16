import threading
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog  
import pygame
import tkinter.ttk as ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from geopy.geocoders import Nominatim
import requests
from firebase_admin import firestore
from firebase_admin import auth, messaging, initialize_app
from firebase_admin.credentials import Certificate 
import googlemap
import googlemaps


class AlertSystem:
  
    def __init__(self, check_interval=60):
        self.check_interval = check_interval
        self.is_baby_checked_in = False
        self.last_location = None
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.api_endpoint = 'https://baby-bud-default-rtdb.firebaseio.com'
        self.api_key = "AIzaSyDtfyPTvTjD-vdRE8PC6S4O22krd_Us5tM"
        self.car_stop_time = None

    def start(self):
        self.is_baby_checked_in = False 
        self.last_location = self.get_current_location()
        self.check_in_api()  # Call the check-in API
        self.thread.start()

    def run(self):
        while self.is_baby_checked_in:
            current_location = self.get_current_location()
            if current_location == self.last_location:
                if not self.car_stop_time:
                    self.car_stop_time = time.time()
                elif time.time() - self.car_stop_time >= 180:  # 3 minutes in seconds
                    self.alert_user()
                    self.car_stop_time = None
            else:
                self.car_stop_time = None

            self.last_location = current_location
            time.sleep(self.check_interval)

    def get_current_location(self):
        geolocator = Nominatim(user_agent="baby_bud_app")
        location = geolocator.geocode(" Lawrenceville, GA 30045 , USA ")

        if location:
            return location.latitude, location.longitude
        return None

    def alert_user(self):
        message = messaging.Message(
            notification=messaging.Notification(
                title='Baby Alert',
                body='Your baby is in the same location.',
            ),
            token='AAAAkcbBUA0:APA91bG4_dwCW1lb5nHj33Ztc0NF1yjjBiPSJUp1VulZUa15Kp7-HNTNg7jyKiyXcj4Q2CnIE5DZFBrM_V7N1SJptTbDXq_OsXA5rSB3bugBGBwuW1UnDVKoPSGrZSKF1hu9Dtm8G644',
        )

        response = messaging.send(message)
        print('Successfully sent message:', response)

    def check_out_baby(self):
        self.is_baby_checked_in = False 
        self.check_out_api()  # Call the check-out API

    def check_in_api(self):
        data = {
            'baby_id': '<YOUR_BABY_ID>',
            'timestamp': int(time.time())
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        response = requests.post(self.api_endpoint, json=data, headers=headers)
        if response.status_code == 200:
            print('Baby checked in successfully.')
        else:
            print('Failed to check in baby.')

    def check_out_api(self):
        data = {
            'baby_id': '1:626104815629:web:07ab777f4a4b8ab26b4544',
            'timestamp': int(time.time())
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        response = requests.post(self.api_endpoint, json=data, headers=headers)
        if response.status_code == 200:
            print('Baby checked out successfully.')
        else:
            print('Failed to check out baby.')

class BabyTracker:
    def __init__(self):
        self.logged_in = False

    def update_login_status(self, status):
        self.logged_in = status

    def check_in_baby(self, baby):
        if not self.logged_in:
            raise ValueError("Failed to check in baby. Please log in first.")
        # ... logic for checking in a baby...

    def check_out_baby(self, baby):
        if not self.logged_in:
            raise ValueError("Failed to check out baby. Please log in first.")
        # ... logic for checking out a baby...

class BabyInfoWindow(tk.Toplevel):
    def __init__(self, root, baby_tracker):
        super().__init__(root)
        self.title("Baby Information")
        self.configure(bg='turquoise')
        self.font = ("Arial", 12, "bold")
        self.baby_tracker = baby_tracker

        image_path = 'baby/one.png'
        image = Image.open(image_path)
        image = image.resize((220, 220))
        self.image_tk = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(self, image=self.image_tk, bg='turquoise')
        self.image_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.name_label = tk.Label(self, text='Baby Name:', fg='black', bg='turquoise', font=self.font)
        self.name_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.name_entry = tk.Entry(self, fg='black', bg='white', font=self.font)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)
        self.birthday_label = tk.Label(self, text='Baby Birthday:', fg='black', bg='turquoise', font=self.font)
        self.birthday_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.birthday_entry = DateEntry(self, fg='black', bg='white', font=self.font)
        self.birthday_entry.grid(row=2, column=1, padx=10, pady=10)
        self.date_label = tk.Label(self, text='Alarm Date:', fg='black', bg='turquoise', font=self.font)
        self.date_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.date_entry = DateEntry(self, fg='black', bg='white', font=self.font)
        self.date_entry.grid(row=3, column=1, padx=10, pady=10)
        self.time_label = tk.Label(self, text='Alarm Time:', fg='black', bg='turquoise', font=self.font)
        self.time_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.time_combo = ttk.Combobox(self, values=self.get_time_values(), font=self.font, state='readonly')
        self.time_combo.grid(row=4, column=1, padx=10, pady=10)
        self.sound_label = tk.Label(self, text='Alarm Sound:', fg='black', bg='turquoise', font=self.font)
        self.sound_label.grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.sound_button = tk.Button(self, text='Select Sound', fg='white', bg='blue', font=self.font,
                                      command=self.select_sound)
        self.sound_button.grid(row=5, column=1, padx=10, pady=10)
        self.picture_label = tk.Label(self, text='Baby Picture:', fg='black', bg='turquoise', font=self.font)
        self.picture_label.grid(row=6, column=0, padx=10, pady=10, sticky="e")
        self.picture_button = tk.Button(self, text='Select Picture', fg='white', bg='blue', font=self.font,
                                        command=self.select_picture)
        self.picture_button.grid(row=6, column=1, padx=10, pady=10)
        self.set_alarm_button = tk.Button(self, text='Set Alarm', fg='white', bg='blue', font=self.font,
                                          command=self.set_alarm)
        self.set_alarm_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
        self.back_button = tk.Button(self, text='Back', fg='white', bg='blue', font=self.font, command=self.destroy)
        self.back_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)
        self.check_out_button = tk.Button(self, text='Check out baby', fg='white', bg='red', font=self.font,
                                           command=self.check_out_baby)     
        self.check_out_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10)


    def check_out_baby(self):
        try:
            self.baby_tracker.check_out_baby()  # Call the check_out_baby method of the BabyTracker
            messagebox.showinfo("Check Out Successful", "Baby has been checked out.")
        except ValueError as e:
            messagebox.showerror("Check Out Failed", str(e))
    
    def check_in_baby(self):
        self.alert_system.check_in_baby()
        messagebox.showinfo("Check in", "Baby checked in. You will receive alerts.")
      
    def get_time_values(self):
        times = []
        for hour in range(24):
            for minute in range(0, 60, 15):
                time_str = f'{hour:02d}:{minute:02d}'
                times.append(time_str)
        return times

    def select_sound(self):
        sound_path = filedialog.askopenfilename(filetypes=[('Sound Files', '*.mp3')])
        self.sound_path = sound_path

    def select_picture(self):
        picture_path = filedialog.askopenfilename(filetypes=[('Image Files', '*.png;*.jpg;*.jpeg')])
        self.picture_path = picture_path

    def set_alarm(self):
        baby_name = self.name_entry.get()
        baby_birthday = self.birthday_entry.get()
        alarm_date = self.date_entry.get()
        alarm_time = self.time_combo.get()

        if not baby_name or not baby_birthday or not alarm_date or not alarm_time:
            messagebox.showwarning("Missing Information", "Please enter all the required information.")
            return

        if hasattr(self, 'sound_path') and self.sound_path:
            self.play_alarm_sound(self.sound_path)

        self.name_entry.delete(0, tk.END)
        self.birthday_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_combo.set('')

        messagebox.showinfo("Alarm Set", f"Alarm set for {baby_name} on {alarm_date} at {alarm_time}.")

    def play_alarm_sound(self, sound_path):
        pygame.mixer.init()
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()

class RegistrationWindow(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title("Registration Window")
        self.configure(bg='turquoise')
        self.font = ("Arial", 12, "bold")
        self.logo = tk.PhotoImage(file='baby/two.png')
        self.logo_label = tk.Label(self, image=self.logo, bg='turquoise')
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.email_label = tk.Label(self, text='Email:', fg='white', bg='black', font=self.font)
        self.email_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.email_entry = tk.Entry(self, fg='white', bg='gray', font=self.font)
        self.email_entry.grid(row=1, column=1, padx=10, pady=10)
        self.password_label = tk.Label(self, text='Password:', fg='white', bg='black', font=self.font)
        self.password_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = tk.Entry(self, show='*', fg='white', bg='gray', font=self.font)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)
        self.register_button = tk.Button(self, text='Register', fg='white', bg='blue', font=self.font, command=self.register)
        self.register_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.back_button = tk.Button(self, text='Back', fg='white', bg='blue', font=self.font, command=self.destroy)
        self.back_button.grid(row=3, column=1, padx=10, pady=10, sticky="e")

    def register(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            messagebox.showinfo("Registration Successful", f"User registered with UID: {user.uid}")
            self.main_app.open_baby_info_window()
            self.destroy()  # destroy the RegistrationWindow after successful registration
        except Exception as e:
            error_message = str(e)
            messagebox.showerror("Failed Registration", error_message)

class LoginWindow(tk.Toplevel):
    def __init__(self, root, main_app):
        super().__init__(root)
        self.title("Login Window")
        self.configure(bg='turquoise')
        self.font = ("Arial", 12, "bold")
        self.logo = tk.PhotoImage(file='baby/two.png')
        self.logo_label = tk.Label(self, image=self.logo, bg='turquoise')
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.email_label = tk.Label(self, text='Email:', fg='white', bg='black', font=self.font)
        self.email_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.email_entry = tk.Entry(self, fg='white', bg='gray', font=self.font)
        self.email_entry.grid(row=1, column=1, padx=10, pady=10)
        self.password_label = tk.Label(self, text='Password:', fg='white', bg='black', font=self.font)
        self.password_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = tk.Entry(self, show='*', fg='white', bg='gray', font=self.font)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)
        self.login_button = tk.Button(self, text='Login', fg='white', bg='blue', font=self.font, command=self.login)
        self.login_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.back_button = tk.Button(self, text='Back', fg='white', bg='blue', font=self.font, command=self.destroy)
        self.back_button.grid(row=3, column=1, padx=10, pady=10, sticky="e")

        # Reference to the main app
        self.main_app = main_app
        self.main_app.baby_tracker

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        try:
            user = auth.get_user_by_email(email)
            messagebox.showinfo("Login Successful", f"User logged in with UID: {user.uid}")
            self.main_app.baby_tracker.update_login_status(True)  # Update the login status in BabyTracker
            self.main_app.open_baby_info_window()  # use main_app reference to call the function
            self.destroy()  # destroy the LoginWindow after successful login
        except Exception as e:
            error_message = str(e)
            messagebox.showerror("Failed Login", error_message)


            messagebox.showinfo("Registration Successful", "User registered successfully.")
            self.main_app.open_baby_info_window()  # Use main_app reference to call the method
            self.destroy() 

class MyApp(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
       
        self.alert_system = AlertSystem() 
        self.root = root
        self.root.title("Ahmed Alaboodi")
        self.root.configure(bg='turquoise')
        self.font = ("Arial", 12, "normal")
        self.logo = tk.PhotoImage(file='baby/four.png')
        self.logo_label = tk.Label(self.root, image=self.logo, bg='turquoise')
        self.logo_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.email_label = tk.Label(root, text='Email:', fg='white', bg='black', font=self.font)
        self.email_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.email_entry = tk.Entry(root, fg='white', bg='gray', font=self.font)
        self.email_entry.grid(row=1, column=1, padx=10, pady=10)
        self.register_button = tk.Button(root, text='Register', fg='white', bg='blue', font=self.font,
                                          command=self.open_registration_window)
        self.register_button.grid(row=2, column=0, padx=10, pady=10)
        self.login_button = tk.Button(root, text='Login', fg='white', bg='blue', font=self.font,
                                       command=self.open_login_window)
        self.login_button.grid(row=2, column=1, padx=10, pady=10)
        self.baby_info_button = tk.Button(root, text='Baby Information', fg='white', bg='blue', font=self.font,
                                          command=self.open_baby_info_window)
        self.baby_info_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.car_ID_label = tk.Label(root, text='Car Year:', fg='white', bg='black', font=self.font)
        self.car_ID_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.car_ID_entery = tk.Entry(root, fg='white', bg='gray', font=self.font)
        self.car_ID_entery.grid(row=4, column=1, padx=10, pady=10)
        self.make_label = tk.Label(root, text='Make:', fg='white', bg='black', font=self.font)
        self.make_label.grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.make_entry = tk.Entry(root, fg='white', bg='gray', font=self.font)
        self.make_entry.grid(row=5, column=1, padx=10, pady=10)
        self.model_label = tk.Label(root, text='Model:', fg='white', bg='black', font=self.font)  
        self.model_entry = tk.Entry(root, fg='white', bg='gray', font=self.font) 
        self.model_label.grid(row=6, column=0, padx=10, pady=10, sticky="e")  
        self.model_entry.grid(row=6, column=1, padx=10, pady=10)  
        self.add_button = tk.Button(root, text='Add Car', fg='white', bg='blue', font=self.font,
                                    command=self.add_car)
        self.add_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
        self.checkin_button = tk.Button(root, text='Check In', fg='white', bg='red', font=self.font,
                                        command=self.alert_system.start)
        self.checkin_button.grid(row=8, column=0, padx=10, pady=10)
        self.checkout_button = tk.Button(root, text='Check Out', fg='white', bg='red', font=self.font,                                        command=self.alert_system.check_out_baby)
        self.checkout_button.grid(row=8, column=1, padx=10, pady=10)
        self.location_display = tk.Label(root, text='', fg='black', bg='turquoise', font=self.font)
        self.location_display.grid(row=9, column=0, columnspan=2, padx=10, pady=10)
        self.baby_tracker = BabyTracker()
        
      
        
      


        # Begin displaying location
        self.display_location()


        # Begin displaying location
        self.display_location()

        # Begin displaying location
        self.display_location()
        self.add_car_button = tk.Button(self, text="Add Car", command=self.add_car)
        self.add_car_button.pack()
        self.root = root
    def open_registration_window(self):
        registration_window = RegistrationWindow(self.root)

    def open_login_window(self):
        login_window = LoginWindow(self.root, self)

    def open_baby_info_window(self):
        baby_info_window = BabyInfoWindow(self.root, self.alert_system)


    def display_location(self):
        print("Calling display_location...")  # New print statement
        location = self.alert_system.get_current_location()
        print(f"Location find: {location}")  # New print statement
        if location:
           self.location_display.config(text=f'Current Location: {location[0]}, {location[1]}')
        self.after(10000, self.display_location) 

    def get_current_location():
        geolocator = Nominatim(user_agent="baby_bud_app")
        location =geolocator.geocode(" Lawrenceville, GA 30045 , USA ") 

        print(f"Location fetched: {location}")  # New print statement
        if location:
             return location.latitude, location.longitude
        return None

    print(get_current_location())
  
    def add_car(self):
        car_ID = self.car_ID_entery.get()
        make = self.make_entry.get()
        model = self.model_entry.get()
     


        if not car_ID and not make and not model:  # Model checking added
          messagebox.showwarning("Missing Information", "Please enter Car information.")
          return



        db = firestore.client()
        cars_ref = db.collection('cars')
        new_car = cars_ref.document(car_ID)
        new_car.set({'make': make, 'model': model})  # Model added to database

        self.car_ID_entery.delete(0, tk.END)
        self.make_entry.delete(0, tk.END)
        self.model_entry.delete(0, tk.END)  # Model entry clear

        self.create_custom_reminder(car_ID)
        print(f"Reminder for car_ID: {car_ID} has been created.")

        messagebox.showinfo("Car Addition Successful", f"Car with Year {car_ID} was added successfully.")

    def create_custom_reminder(self, car_ID):
      
        print(f"Custom reminder created for car_ID: {car_ID}!")






# Set up Google Maps API client
google_maps_api_key = 'AIzaSyDtfyPTvTjD-vdRE8PC6S4O22krd_Us5tM'  # Replace with your Google Maps API key
gmaps = googlemaps.Client(key=google_maps_api_key)

cred = Certificate('baby-bud-firebase-adminsdk-te561-804b25280c.json')  # Correct instantiation of the Certificate
initialize_app(cred)  # Correct function call

# Instantiate your app
root = tk.Tk()
app = MyApp(master=root)
root.mainloop()