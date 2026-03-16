import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import platform
import sqlite3
import os
import random
import calendar
from datetime import date
import math

# ---------------- FETCH TOYOTA DATA ----------------
response = requests.get("https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformake/toyota?format=json")
data = response.json()
results = data["Results"]
vehicles = [{"Model_ID": v["Model_ID"], "Model_Name": v["Model_Name"]} for v in results]

#Tim: gets data from an API link and stores it in a variable called results
#Cha: It collects the data, converts it into a format Python understands, and saves only the model ID and model name in a list for easier use in the app.
#Juliel: .This code fetches Toyota vehicle model data from an online API using requests. It converts the response to JSON and extracts the results. Then, it creates a list containing each model’s ID and name.
#Barrion: Retrieves Toyota models from the API, parses the JSON response, and creates a list of dictionaries with each model's ID and name.

# ---------------- SYSTEM FONT ----------------
if platform.system() == "Windows":
    BASE_FONT = "Segoe UI"
elif platform.system() == "Darwin":
    BASE_FONT = "SF Pro Text"
else:
    BASE_FONT = "Ubuntu"

SYSTEM_FONT = (BASE_FONT, 12)
TITLE_FONT = (BASE_FONT, 24, "bold")

# ---------------- COLORS ----------------
DARK_BG = "#2E2E2E"
TEXT_COLOR = "white"
BUTTON_RED = "#d53c3c"
CARD_BG = "#656565"
CARD_RADIUS = 20
CARD_PADDING = 16
BUTTON_RADIUS = 20

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Toyota Dealership")
root.geometry("1200x700")

# ---------------- IN-MEMORY SQL DATABASE ----------------
db_conn = sqlite3.connect(":memory:")
db_cursor = db_conn.cursor()
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
""")
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        car_name TEXT NOT NULL,
        booking_date TEXT NOT NULL,
        hours INTEGER NOT NULL,
        price INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")
db_conn.commit()
current_user = None


def create_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)


def rounded_button(parent, text, command, width=170, height=42):
    button_canvas = tk.Canvas(
        parent,
        width=width,
        height=height,
        bg=parent.cget("bg"),
        highlightthickness=0,
        bd=0
    )
    button_shape = create_rounded_rect(
        button_canvas,
        1,
        1,
        width - 1,
        height - 1,
        BUTTON_RADIUS,
        fill=BUTTON_RED,
        outline=BUTTON_RED
    )
    button_text = button_canvas.create_text(
        width // 2,
        height // 2,
        text=text,
        fill="white",
        font=SYSTEM_FONT
    )

    def on_click(_event):
        command()

    button_canvas.bind("<Button-1>", on_click)
    button_canvas.tag_bind(button_shape, "<Button-1>", on_click)
    button_canvas.tag_bind(button_text, "<Button-1>", on_click)
    button_canvas.configure(cursor="hand2")
    return button_canvas


def get_car_photo_paths():
    assets_dir = os.path.join(".", "assets")
    candidate_dirs = [
        os.path.join(assets_dir, "car photos"),
        os.path.join(assets_dir, "car_photos"),
        os.path.join(assets_dir, "car-photos")
    ]
    if os.path.isdir(assets_dir):
        for folder_name in os.listdir(assets_dir):
            folder_path = os.path.join(assets_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue
            lowered = folder_name.lower()
            if "car" in lowered and "photo" in lowered and folder_path not in candidate_dirs:
                candidate_dirs.append(folder_path)

    image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".webp")
    photo_paths = []
    for photo_dir in candidate_dirs:
        if not os.path.isdir(photo_dir):
            continue
        for filename in os.listdir(photo_dir):
            if filename.lower().endswith(image_extensions):
                photo_paths.append(os.path.join(photo_dir, filename))

    return photo_paths


def load_inventory_image_pool():
    photo_paths = get_car_photo_paths()

    if not photo_paths:
        photo_paths = ["./assets/inventory_placeholder.png"]

    image_pool = []
    for path in photo_paths:
        try:
            with Image.open(path) as img:
                image_pool.append(ImageTk.PhotoImage(img.resize((250, 150))))
        except OSError:
            continue

    if not image_pool:
        with Image.open("./assets/inventory_placeholder.png") as img:
            image_pool.append(ImageTk.PhotoImage(img.resize((250, 150))))

    return image_pool


def load_random_detail_images(count=3):
    photo_paths = get_car_photo_paths()
    if not photo_paths:
        photo_paths = ["./assets/car-details_placeholder.png"]

    if len(photo_paths) >= count:
        selected_paths = random.sample(photo_paths, count)
    else:
        selected_paths = [random.choice(photo_paths) for _ in range(count)]

    detail_images = []
    for path in selected_paths:
        try:
            with Image.open(path) as img:
                detail_images.append(ImageTk.PhotoImage(img.resize((300, 200))))
        except OSError:
            continue

    if not detail_images:
        with Image.open("./assets/car-details_placeholder.png") as img:
            detail_images.append(ImageTk.PhotoImage(img.resize((300, 200))))

    while len(detail_images) < count:
        detail_images.append(detail_images[0])

    return detail_images

#Tim: configures the GUI window’s visual settings
#Cha: System_Font is for normal text, and Title_Font is for bigger, bold titles. We set the title of the window to “Toyota Dealership”,
#Juliel: This code sets font styles for the app. It creates the main Tkinter window and sets its title to "Toyota Dealership." It also defines the window size and background color.
#Barrion: Creates the main Tkinter window titled "Toyota Dealership", sets its size to 1200x700 pixels, and applies a light gray background. 

# ---------------- LOGIN PAGE ----------------
def login_page():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="white")

    bg_img = Image.open("./assets/register_img.jpg").resize((1200, 700))
    root.bg_photo = ImageTk.PhotoImage(bg_img)

    bg_label = tk.Label(root, image=root.bg_photo)
    bg_label.place(relwidth=1, relheight=1)

    frame = tk.Frame(root, bg="black", padx=40, pady=30)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="Log In",
             fg="white", bg="black",
             font=TITLE_FONT).pack(pady=10)

    tk.Label(frame, text="Name",
             fg="white", bg="black",
             font=SYSTEM_FONT).pack(anchor="w")
    name_entry = tk.Entry(frame, font=SYSTEM_FONT, width=30)
    name_entry.pack(pady=5)

    tk.Label(frame, text="Email",
             fg="white", bg="black",
             font=SYSTEM_FONT).pack(anchor="w")
    email_entry = tk.Entry(frame, font=SYSTEM_FONT, width=30)
    email_entry.pack(pady=5)

    tk.Label(frame, text="Password",
             fg="white", bg="black",
             font=SYSTEM_FONT).pack(anchor="w")
    password_entry = tk.Entry(frame, show="*", font=SYSTEM_FONT, width=30)
    password_entry.pack(pady=5)

    def login():
        global current_user
        name = name_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()

        if not name or not email or not password:
            messagebox.showerror("Error", "Enter name, email, and password")
            return

        db_cursor.execute(
            "SELECT id, name, email FROM users WHERE name = ? AND email = ? AND password = ?",
            (name, email, password)
        )
        user = db_cursor.fetchone()

        if user is None:
            messagebox.showerror("Not Registered", "Credentials not found. Please register first.")
            return

        current_user = {"id": user[0], "name": user[1], "email": user[2]}
        inventory_page()

    btn_frame = tk.Frame(frame, bg="black")
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text="Log In",
              font=SYSTEM_FONT,
              command=login).pack(side="left", padx=8)

    tk.Button(btn_frame, text="Create Account",
              font=SYSTEM_FONT,
              command=register_page).pack(side="left", padx=8)

# ---------------- REGISTER PAGE ----------------
def register_page():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="white")

    bg_img = Image.open("./assets/register_img.jpg").resize((1200, 700))
    root.bg_photo = ImageTk.PhotoImage(bg_img)

    bg_label = tk.Label(root, image=root.bg_photo)
    bg_label.place(relwidth=1, relheight=1)

    frame = tk.Frame(root, bg="black", padx=40, pady=30)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="Create Account",
             fg="white", bg="black",
             font=TITLE_FONT).pack(pady=10)

    tk.Label(frame, text="Name",
             fg="white", bg="black",
             font=SYSTEM_FONT).pack(anchor="w")
    name_entry = tk.Entry(frame, font=SYSTEM_FONT, width=30)
    name_entry.pack(pady=5)

    tk.Label(frame, text="Email",
             fg="white", bg="black",
             font=SYSTEM_FONT).pack(anchor="w")
    email_entry = tk.Entry(frame, font=SYSTEM_FONT, width=30)
    email_entry.pack(pady=5)

    tk.Label(frame, text="Password",
             fg="white", bg="black",
             font=SYSTEM_FONT).pack(anchor="w")
    password_entry = tk.Entry(frame, show="*", font=SYSTEM_FONT, width=30)
    password_entry.pack(pady=5)

    def register():
        name = name_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()

        if not name or not email or not password:
            messagebox.showerror("Error", "Enter name, email, and password")
            return

        try:
            db_cursor.execute(
                "INSERT INTO users(name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            db_conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already registered. Please log in.")
            return

        messagebox.showinfo("Success", "Account created. Please log in.")
        login_page()

    tk.Button(frame, text="Sign Up",
              font=SYSTEM_FONT,
              command=register).pack(pady=15)
    
#Tim: Function for the Register page. Sets the background image and the textboxes for the register form
#Cha: This section creates the Register Page. It clears the screen, shows a background image, and adds a frame with fields for Name, Email, and Password.
#Juliel: This function creates a registration page with a background image and input fields for name, email, and password. It also adds a Sign Up button. When clicked, it checks if the name is entered before moving to the next page.
#Barrion: Defines the register_page function, which clears the window, sets a background image, creates a centered black frame with entry fields for name, email, and password, and adds a "Sign Up" button that validates input before navigating to the inventory page. 


# ---------------- INVENTORY PAGE ----------------
def inventory_page():
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=DARK_BG)

    tk.Label(root, text="Inventory / Vehicles",
             font=TITLE_FONT,
             bg=DARK_BG,
             fg=TEXT_COLOR).pack(pady=20)

    outer = tk.Frame(root, bg=DARK_BG)
    outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(outer, bg=DARK_BG, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    container = tk.Frame(canvas, bg=DARK_BG)
    canvas_window = canvas.create_window((0, 0), window=container, anchor="n")

    def resize_canvas(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", resize_canvas)

    def update_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    container.bind("<Configure>", update_scroll)

    root.inventory_image_pool = load_inventory_image_pool()

    row = 0
    col = 0

    for v in vehicles:
        card_canvas = tk.Canvas(
            container,
            width=330,
            height=352,
            bg=DARK_BG,
            highlightthickness=0,
            bd=0
        )
        card_canvas.grid(row=row, column=col, padx=28, pady=28, sticky="n")

        create_rounded_rect(
            card_canvas,
            1,
            1,
            329,
            351,
            CARD_RADIUS,
            fill=CARD_BG,
            outline=CARD_BG
        )

        card = tk.Frame(card_canvas, bg=CARD_BG, padx=CARD_PADDING, pady=CARD_PADDING)
        card_canvas.create_window(165, 176, window=card, width=292, height=314)

        random_photo = random.choice(root.inventory_image_pool)
        tk.Label(card,
                 image=random_photo,
                 bg=CARD_BG).pack(pady=(0, 10))

        tk.Label(card,
                 text=v["Model_Name"],
                 fg=TEXT_COLOR,
                 bg=CARD_BG,
                 font=(BASE_FONT, 14, "bold")).pack()

        tk.Label(card,
                 text=f"Model ID: {v['Model_ID']}",
                 fg=TEXT_COLOR,
                 bg=CARD_BG,
                 font=SYSTEM_FONT).pack()

        rounded_button(
            card,
            "View More",
            lambda name=v["Model_Name"]: vehicle_details_page(name),
            width=145
        ).pack(pady=(10, 0))

        col += 1
        if col == 3:
            col = 0
            row += 1

    for i in range(3):
        container.grid_columnconfigure(i, weight=1)

    rounded_button(
        root,
        "Profile",
        user_profile_page,
        width=120,
        height=40
    ).place(relx=0.98, rely=0.12, anchor="ne")

    rounded_button(
        root,
        "Log Out",
        logout_to_login,
        width=120,
        height=40
    ).place(relx=0.98, rely=0.19, anchor="ne")

#Tim: Function for the inventory / vehicles page. It clears the current window and displays available toyota models.
#Cha: It creates a clean inventory page where each vehicle is displayed as a card with its image and detail
#Juliel: This function creates the inventory page and clears previous widgets. It displays vehicle cards with images, names, and model IDs in a grid layout. Each card has a “View More” button that opens details for the selected vehicle.
#Barrion: Defines the inventory_page function, which clears the window and displays a grid of up to 9 vehicle cards with images, model details, and a "View More" button for each. 

# ---------------- VEHICLE DETAILS PAGE ----------------
def vehicle_details_page(model_name):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=DARK_BG)

    tk.Label(root,
             text="Vehicle Details",
             font=TITLE_FONT,
             bg=DARK_BG,
             fg=TEXT_COLOR).pack(pady=10)

    tk.Label(root,
             text=model_name,
             font=(BASE_FONT, 20, "bold"),
             bg=DARK_BG,
             fg=TEXT_COLOR).pack()

    root.detail_images = load_random_detail_images(3)

    img_frame = tk.Frame(root, bg=DARK_BG)
    img_frame.pack(pady=20)

    for img in root.detail_images:
        tk.Label(img_frame,
                 image=img,
                 bg=DARK_BG).pack(side="left", padx=10)

    tk.Label(root,
             text="₱1,000 - 12 hours",
             font=SYSTEM_FONT,
             bg=DARK_BG,
             fg=TEXT_COLOR).pack()

    tk.Label(root,
             text="₱2,000 - 24 hours",
             font=SYSTEM_FONT,
             bg=DARK_BG,
             fg=TEXT_COLOR).pack()

    button_frame = tk.Frame(root, bg=DARK_BG)
    button_frame.pack(pady=14)

    rounded_button(
        button_frame,
        "Book now",
        lambda: book_now_page(model_name),
        width=185
    ).pack(pady=5)

    rounded_button(
        button_frame,
        "Reviews",
        lambda: reviews_page(model_name),
        width=185
    ).pack(pady=5)

    rounded_button(
        button_frame,
        "Back to Inventory",
        inventory_page,
        width=185
    ).pack(pady=5)

    tk.Label(root,
             text="★★★★★",
             fg="gold",
             bg=DARK_BG,
             font=(BASE_FONT, 20)).pack(pady=(8, 0))


def book_now_page(model_name):
    if current_user is None:
        messagebox.showerror("Error", "Please log in first.")
        login_page()
        return

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=DARK_BG)

    tk.Label(root,
             text=f"Book {model_name}",
             font=TITLE_FONT,
             bg=DARK_BG,
             fg=TEXT_COLOR).pack(pady=18)

    split_frame = tk.Frame(root, bg=DARK_BG)
    split_frame.pack(fill="both", expand=True, padx=36, pady=(0, 24))

    left_panel = tk.Frame(split_frame, bg=CARD_BG, padx=20, pady=20)
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 12))

    right_panel = tk.Frame(split_frame, bg=CARD_BG, padx=20, pady=20)
    right_panel.pack(side="left", fill="both", expand=True, padx=(12, 0))

    tk.Label(left_panel,
             text="Select Date and Duration",
             fg=TEXT_COLOR,
             bg=CARD_BG,
             font=(BASE_FONT, 16, "bold")).pack(pady=(0, 8))

    selected_date_var = tk.StringVar(value="")
    hours_var = tk.StringVar(value="")
    selected_month_var = tk.StringVar()

    def update_price_display():
        selected_date = selected_date_var.get().strip()
        hours_text = hours_var.get().strip()

        date_value_var.set(selected_date if selected_date else "Not selected")

        try:
            hours = int(hours_text)
            if hours <= 0:
                raise ValueError
        except ValueError:
            hours_value_var.set("Not set")
            price_value_var.set("Fill date and hours first")
            return

        hours_value_var.set(f"{hours} hour(s)")

        if not selected_date:
            price_value_var.set("Fill date and hours first")
            return

        computed_price = math.ceil(hours / 12) * 1000
        price_value_var.set(f"₱{computed_price:,}")

    calendar_frame = tk.Frame(left_panel, bg=CARD_BG)
    calendar_frame.pack(pady=6)

    header_frame = tk.Frame(calendar_frame, bg=CARD_BG)
    header_frame.grid(row=0, column=0, columnspan=7, pady=(0, 6))

    today = date.today()
    calendar_state = {"year": today.year, "month": today.month}

    def select_day(day_number):
        selected = date(calendar_state["year"], calendar_state["month"], day_number)
        selected_date_var.set(selected.isoformat())
        update_price_display()
        render_calendar()

    def previous_month():
        month = calendar_state["month"] - 1
        year = calendar_state["year"]
        if month == 0:
            month = 12
            year -= 1
        calendar_state["month"] = month
        calendar_state["year"] = year
        render_calendar()

    def next_month():
        month = calendar_state["month"] + 1
        year = calendar_state["year"]
        if month == 13:
            month = 1
            year += 1
        calendar_state["month"] = month
        calendar_state["year"] = year
        render_calendar()

    tk.Button(header_frame,
              text="◀",
              command=previous_month,
              bg=BUTTON_RED,
              fg="white",
              relief="flat").pack(side="left", padx=8)

    tk.Label(header_frame,
             textvariable=selected_month_var,
             fg=TEXT_COLOR,
             bg=CARD_BG,
             font=(BASE_FONT, 13, "bold")).pack(side="left", padx=8)

    tk.Button(header_frame,
              text="▶",
              command=next_month,
              bg=BUTTON_RED,
              fg="white",
              relief="flat").pack(side="left", padx=8)

    days_grid = tk.Frame(calendar_frame, bg=CARD_BG)
    days_grid.grid(row=1, column=0, columnspan=7)

    def render_calendar():
        for widget in days_grid.winfo_children():
            widget.destroy()

        selected_month_var.set(
            f"{calendar.month_name[calendar_state['month']]} {calendar_state['year']}"
        )

        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for col, name in enumerate(weekdays):
            tk.Label(days_grid,
                     text=name,
                     fg=TEXT_COLOR,
                     bg=CARD_BG,
                     font=(BASE_FONT, 10, "bold"),
                     width=3).grid(row=0, column=col, padx=2, pady=2)

        month_matrix = calendar.monthcalendar(calendar_state["year"], calendar_state["month"])
        for week_index, week in enumerate(month_matrix, start=1):
            for col_index, day_number in enumerate(week):
                if day_number == 0:
                    tk.Label(days_grid, text="", bg=CARD_BG, width=3).grid(
                        row=week_index, column=col_index, padx=2, pady=2
                    )
                    continue

                day_date = date(calendar_state["year"], calendar_state["month"], day_number).isoformat()
                is_selected = day_date == selected_date_var.get()
                tk.Button(
                    days_grid,
                    text=str(day_number),
                    width=3,
                    bg=BUTTON_RED if is_selected else DARK_BG,
                    fg="white",
                    relief="flat",
                    command=lambda d=day_number: select_day(d)
                ).grid(row=week_index, column=col_index, padx=2, pady=2)

    render_calendar()

    tk.Label(left_panel,
             text="Booking hours",
             fg=TEXT_COLOR,
             bg=CARD_BG,
             font=SYSTEM_FONT).pack(anchor="w", pady=(14, 2))

    hour_input = tk.Spinbox(
        left_panel,
        from_=1,
        to=240,
        textvariable=hours_var,
        width=8
    )
    hour_input.pack(anchor="w")

    hour_input.bind("<KeyRelease>", lambda _event: update_price_display())
    hours_var.trace_add("write", lambda *_args: update_price_display())

    tk.Label(left_panel,
             textvariable=selected_date_var,
             fg=TEXT_COLOR,
             bg=CARD_BG,
             font=(BASE_FONT, 11, "italic")).pack(anchor="w", pady=(8, 0))

    tk.Label(right_panel,
             text="Reservation Summary",
             fg=TEXT_COLOR,
             bg=CARD_BG,
             font=(BASE_FONT, 16, "bold")).pack(pady=(0, 12))

    tk.Label(right_panel,
             text=f"Car: {model_name}",
             fg=TEXT_COLOR,
             bg=CARD_BG,
             font=SYSTEM_FONT).pack(anchor="w", pady=4)

    date_value_var = tk.StringVar(value="Not selected")
    hours_value_var = tk.StringVar(value="Not set")
    price_value_var = tk.StringVar(value="Fill date and hours first")

    tk.Label(right_panel, text="Date:", fg=TEXT_COLOR, bg=CARD_BG, font=SYSTEM_FONT).pack(anchor="w", pady=(8, 0))
    tk.Label(right_panel, textvariable=date_value_var, fg=TEXT_COLOR, bg=CARD_BG, font=SYSTEM_FONT).pack(anchor="w")

    tk.Label(right_panel, text="Hours:", fg=TEXT_COLOR, bg=CARD_BG, font=SYSTEM_FONT).pack(anchor="w", pady=(8, 0))
    tk.Label(right_panel, textvariable=hours_value_var, fg=TEXT_COLOR, bg=CARD_BG, font=SYSTEM_FONT).pack(anchor="w")

    tk.Label(right_panel, text="Price:", fg=TEXT_COLOR, bg=CARD_BG, font=SYSTEM_FONT).pack(anchor="w", pady=(8, 0))
    tk.Label(right_panel, textvariable=price_value_var, fg="gold", bg=CARD_BG, font=(BASE_FONT, 14, "bold")).pack(anchor="w")

    def submit_booking():
        selected_date = selected_date_var.get().strip()
        hours_text = hours_var.get().strip()

        if not selected_date:
            messagebox.showerror("Missing Info", "Please select a booking date.")
            return

        try:
            hours = int(hours_text)
            if hours <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Missing Info", "Please enter valid booking hours.")
            return

        computed_price = math.ceil(hours / 12) * 1000

        db_cursor.execute(
            "INSERT INTO bookings(user_id, car_name, booking_date, hours, price) VALUES (?, ?, ?, ?, ?)",
            (current_user["id"], model_name, selected_date, hours, computed_price)
        )
        db_conn.commit()
        messagebox.showinfo("Booked", f"{model_name} booked on {selected_date} for ₱{computed_price:,}.")
        vehicle_details_page(model_name)

    rounded_button(
        right_panel,
        "Back to Vehicle",
        lambda: vehicle_details_page(model_name),
        width=190
    ).pack(pady=(18, 8))

    rounded_button(
        right_panel,
        "Book now",
        submit_booking,
        width=190
    ).pack(pady=4)


def user_profile_page():
    if current_user is None:
        messagebox.showerror("Error", "Please log in first.")
        login_page()
        return

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=DARK_BG)

    tk.Label(root,
             text="User Profile",
             font=TITLE_FONT,
             bg=DARK_BG,
             fg=TEXT_COLOR).pack(pady=(28, 8))

    card = tk.Frame(root, bg=CARD_BG, padx=32, pady=28)
    card.place(relx=0.5, rely=0.48, anchor="center")

    tk.Label(card,
             text=current_user["name"],
             font=(BASE_FONT, 18, "bold"),
             bg=CARD_BG,
             fg=TEXT_COLOR).pack(pady=(0, 6))

    tk.Label(card,
             text=current_user["email"],
             font=SYSTEM_FONT,
             bg=CARD_BG,
             fg=TEXT_COLOR).pack(pady=(0, 14))

    tk.Label(card,
             text="Car Reservations",
             font=(BASE_FONT, 14, "bold"),
             bg=CARD_BG,
             fg=TEXT_COLOR).pack()

    db_cursor.execute(
        "SELECT car_name, booking_date, hours, price FROM bookings WHERE user_id = ? ORDER BY id DESC",
        (current_user["id"],)
    )
    reservations = db_cursor.fetchall()

    if not reservations:
        reservation_text = "No booked car yet."
    else:
        reservation_lines = []
        for car_name, booking_date, hours, price in reservations:
            reservation_lines.append(
                f"{car_name}\nDate: {booking_date}\nHours: {hours}\nPrice: ₱{price:,}"
            )
        reservation_text = "\n\n".join(reservation_lines)

    tk.Label(card,
             text=reservation_text,
             font=SYSTEM_FONT,
             bg=CARD_BG,
             fg=TEXT_COLOR,
             justify="center",
             wraplength=520).pack(pady=(12, 4))

    rounded_button(
        root,
        "Back to Inventory",
        inventory_page,
        width=220
    ).place(relx=0.5, rely=0.88, anchor="center")


def logout_to_login():
    global current_user
    current_user = None
    login_page()

#Tim: Function for the vehicle details page. Displays rental rates, a 5-star rating, and the button to the reviews page.
#Cha: This function creates a vehicle details page showing the model name, multiple images, rental prices, ratings, and buttons for reviews or going back to the inventory
#Juliel: This function displays the vehicle details page and clears previous widgets. It shows the selected vehicle’s name, placeholder images, rental prices, and a star rating. It also adds buttons to view reviews or go back to the inventory page.
#Barrion: Defines the vehicle_details_page function, which clears the window and displays details for a selected vehicle including its name, images, rental prices, rating, and navigation buttons for reviews or returning to inventory.

# ---------------- REVIEWS PAGE ----------------
def reviews_page(model_name):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=DARK_BG)

    tk.Label(root,
             text="Reviews",
             font=TITLE_FONT,
             bg=DARK_BG,
             fg=TEXT_COLOR).pack(pady=20)

    container = tk.Frame(root, bg=DARK_BG)
    container.pack(fill="both", expand=True)

    root.profile_photo = ImageTk.PhotoImage(
        Image.open("./assets/anonymous_placeholder.jpg").resize((80, 80))
    )

    row = 0
    col = 0

    for i in range(4):
        card = tk.Frame(container,
                        bg=CARD_BG,
                        highlightbackground="#444",
                        highlightthickness=2)

        card.grid(row=row, column=col, padx=50, pady=50)

        tk.Label(card,
                 image=root.profile_photo,
                 bg=CARD_BG).pack(pady=5)

        tk.Label(card,
                 text="Anonymous",
                 fg=TEXT_COLOR,
                 bg=CARD_BG,
                 font=(BASE_FONT, 14, "bold")).pack()

        tk.Label(card,
                 text="★★★★★",
                 fg="gold",
                 bg=CARD_BG,
                 font=(BASE_FONT, 16)).pack()

        tk.Label(card,
                 text="Excellent vehicle and smooth experience!",
                 fg=TEXT_COLOR,
                 bg=CARD_BG,
                 font=SYSTEM_FONT).pack()

        col += 1
        if col == 2:
            col = 0
            row += 1

    for i in range(2):
        container.grid_columnconfigure(i, weight=1)

    tk.Button(root,
              text="Back to Vehicle",
              bg=BUTTON_RED,
              fg="white",
              relief="flat",
              font=SYSTEM_FONT,
              command=lambda: vehicle_details_page(model_name)
              ).pack(pady=10)

#Tim: Function for the reviews page. It displays 4 identical review comments.
#Cha: This function is for reviews page. It shows user boxes with profile pictures, names, star ratings, and comments. Overall, this function organizes user reviews in a clean layout that is interactive and visually consistent.
#Juliel: creates the reviews page and clears previous widgets. It displays four review cards with placeholder profile images, anonymous names, star ratings, and sample review text in a grid layout. It also adds a Back button that returns to the inventory page.
#Barrion: Defines the reviews_page function, which clears the window and displays a grid of review cards with profile images, names, ratings, and comments, plus a button to return to the inventory.

def on_close():
    db_conn.close()
    root.destroy()

# ---------------- START APP ----------------
root.protocol("WM_DELETE_WINDOW", on_close)
login_page()
root.mainloop()