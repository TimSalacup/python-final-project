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

# ---------------- SQL SETUP ----------------
def load_sql_queries(sql_path):
    queries = {}
    current_query_name = None
    current_query_lines = []

    with open(sql_path, "r", encoding="utf-8") as sql_file:
        for raw_line in sql_file:
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            if stripped.startswith("-- name:"):
                if current_query_name is not None:
                    query_text = "\n".join(current_query_lines).strip()
                    if query_text:
                        queries[current_query_name] = query_text
                current_query_name = stripped.split(":", 1)[1].strip()
                current_query_lines = []
            elif current_query_name is not None:
                current_query_lines.append(line)

    if current_query_name is not None:
        query_text = "\n".join(current_query_lines).strip()
        if query_text:
            queries[current_query_name] = query_text

    return queries


SQL_QUERIES = load_sql_queries("./index.sql")

db_conn = sqlite3.connect(":memory:")
db_cursor = db_conn.cursor()
db_cursor.execute(SQL_QUERIES["create_users_table"])
db_cursor.execute(SQL_QUERIES["create_bookings_table"])
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


def create_rounded_card(parent, width, height, bg_color=CARD_BG, radius=CARD_RADIUS, content_padding=20):
    card_canvas = tk.Canvas(
        parent,
        width=width,
        height=height,
        bg=parent.cget("bg"),
        highlightthickness=0,
        bd=0
    )
    create_rounded_rect(
        card_canvas,
        1,
        1,
        width - 1,
        height - 1,
        radius,
        fill=bg_color,
        outline=bg_color
    )

    card_frame = tk.Frame(card_canvas, bg=bg_color)
    card_canvas.create_window(
        width // 2,
        height // 2,
        window=card_frame,
        width=width - (content_padding * 2),
        height=height - (content_padding * 2)
    )
    return card_canvas, card_frame


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
            SQL_QUERIES["select_user_by_credentials"],
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
                SQL_QUERIES["insert_user"],
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
            SQL_QUERIES["insert_booking"],
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
             fg=TEXT_COLOR).pack(pady=(22, 8))

    content_frame = tk.Frame(root, bg=DARK_BG)
    content_frame.place(relx=0.5, rely=0.5, anchor="center")

    top_box_canvas, top_box = create_rounded_card(
        content_frame,
        width=520,
        height=250,
        bg_color=CARD_BG,
        radius=CARD_RADIUS,
        content_padding=20
    )
    top_box_canvas.pack(pady=(0, 18))

    try:
        with Image.open("./assets/anonymous_placeholder.jpg") as profile_image:
            root.user_profile_photo = ImageTk.PhotoImage(profile_image.resize((95, 95)))
        tk.Label(top_box, image=root.user_profile_photo, bg=CARD_BG).pack(pady=(0, 10))
    except OSError:
        tk.Label(top_box,
                 text="[No profile image]",
                 fg=TEXT_COLOR,
                 bg=CARD_BG,
                 font=SYSTEM_FONT).pack(pady=(0, 10))

    tk.Label(top_box,
             text=f"User ID: {current_user['id']}",
             font=(BASE_FONT, 16, "bold"),
             bg=CARD_BG,
             fg=TEXT_COLOR).pack(pady=(0, 8))

    tk.Label(top_box,
             text=f"{current_user['name']}  |  {current_user['email']}",
             font=SYSTEM_FONT,
             bg=CARD_BG,
             fg=TEXT_COLOR).pack()

    bottom_box_canvas, bottom_box = create_rounded_card(
        content_frame,
        width=860,
        height=340,
        bg_color=CARD_BG,
        radius=CARD_RADIUS,
        content_padding=20
    )
    bottom_box_canvas.pack()

    left_panel = tk.Frame(bottom_box, bg=CARD_BG)
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 14))

    divider = tk.Frame(bottom_box, bg=DARK_BG, width=2)
    divider.pack(side="left", fill="y", padx=6)

    right_panel = tk.Frame(bottom_box, bg=CARD_BG)
    right_panel.pack(side="left", fill="y", padx=(14, 0))

    tk.Label(left_panel,
             text="Your Car Bookings",
             font=(BASE_FONT, 14, "bold"),
             bg=CARD_BG,
             fg=TEXT_COLOR).pack(anchor="w", pady=(0, 10))

    tk.Label(right_panel,
             text="Delete",
             font=(BASE_FONT, 14, "bold"),
             bg=CARD_BG,
             fg=TEXT_COLOR).pack(anchor="center", pady=(0, 10))

    db_cursor.execute(SQL_QUERIES["select_bookings_for_user"], (current_user["id"],))
    reservations = db_cursor.fetchall()

    def delete_booking(booking_id):
        db_cursor.execute(SQL_QUERIES["delete_booking_for_user"], (booking_id, current_user["id"]))
        db_conn.commit()
        user_profile_page()

    if not reservations:
        tk.Label(left_panel,
                 text="No booked car yet.",
                 font=SYSTEM_FONT,
                 bg=CARD_BG,
                 fg=TEXT_COLOR,
                 justify="left").pack(anchor="w", pady=(8, 0))

        tk.Label(right_panel,
                 text="No actions",
                 font=SYSTEM_FONT,
                 bg=CARD_BG,
                 fg=TEXT_COLOR).pack(anchor="center", pady=(8, 0))
    else:
        for booking_id, car_name, booking_date, hours, price in reservations:
            booking_line = (
                f"{car_name}\n"
                f"Date: {booking_date} | Hours: {hours} | Price: ₱{price:,}"
            )
            tk.Label(left_panel,
                     text=booking_line,
                     font=SYSTEM_FONT,
                     bg=CARD_BG,
                     fg=TEXT_COLOR,
                     justify="left",
                     anchor="w").pack(anchor="w", pady=6)

            rounded_button(
                right_panel,
                "Delete",
                lambda bid=booking_id: delete_booking(bid),
                width=110,
                height=34
            ).pack(pady=12)

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

def on_close():
    db_conn.close()
    root.destroy()

# ---------------- START APP ----------------
root.protocol("WM_DELETE_WINDOW", on_close)
login_page()
root.mainloop()