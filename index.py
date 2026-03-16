import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import platform

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
DARK_BG = "#222222"
TEXT_COLOR = "white"
BUTTON_RED = "#d53c3c"

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Toyota Dealership")
root.geometry("1200x700")

#Tim: configures the GUI window’s visual settings
#Cha: System_Font is for normal text, and Title_Font is for bigger, bold titles. We set the title of the window to “Toyota Dealership”,
#Juliel: This code sets font styles for the app. It creates the main Tkinter window and sets its title to "Toyota Dealership." It also defines the window size and background color.
#Barrion: Creates the main Tkinter window titled "Toyota Dealership", sets its size to 1200x700 pixels, and applies a light gray background. 

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
        if not name_entry.get():
            messagebox.showerror("Error", "Enter name")
            return
        inventory_page()

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

    root.vehicle_photo = ImageTk.PhotoImage(
        Image.open("./assets/inventory_placeholder.png").resize((250, 150))
    )

    row = 0
    col = 0

    for v in vehicles:
        card = tk.Frame(container,
                        bg=DARK_BG,
                        highlightbackground="#444",
                        highlightthickness=2)

        card.grid(row=row, column=col, padx=40, pady=40, sticky="n")

        tk.Label(card,
                 image=root.vehicle_photo,
                 bg=DARK_BG).pack(pady=10)

        tk.Label(card,
                 text=v["Model_Name"],
                 fg=TEXT_COLOR,
                 bg=DARK_BG,
                 font=(BASE_FONT, 14, "bold")).pack()

        tk.Label(card,
                 text=f"Model ID: {v['Model_ID']}",
                 fg=TEXT_COLOR,
                 bg=DARK_BG,
                 font=SYSTEM_FONT).pack()

        tk.Button(card,
                  text="View More",
                  bg=BUTTON_RED,
                  fg="white",
                  relief="flat",
                  font=SYSTEM_FONT,
                  command=lambda name=v["Model_Name"]:
                  vehicle_details_page(name)).pack(pady=10)

        col += 1
        if col == 3:
            col = 0
            row += 1

    for i in range(3):
        container.grid_columnconfigure(i, weight=1)

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

    root.detail_images = [
        ImageTk.PhotoImage(Image.open("./assets/car-details_placeholder.png").resize((300, 200))),
        ImageTk.PhotoImage(Image.open("./assets/car-details_placeholder.png").resize((300, 200))),
        ImageTk.PhotoImage(Image.open("./assets/car-details_placeholder.png").resize((300, 200)))
    ]

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

    tk.Button(root,
              text="Reviews",
              bg=BUTTON_RED,
              fg="white",
              relief="flat",
              font=SYSTEM_FONT,
              command=lambda: reviews_page(model_name)
              ).pack(pady=10)

    tk.Button(root,
              text="Back to Inventory",
              bg=BUTTON_RED,
              fg="white",
              relief="flat",
              font=SYSTEM_FONT,
              command=inventory_page).pack()

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
                        bg=DARK_BG,
                        highlightbackground="#444",
                        highlightthickness=2)

        card.grid(row=row, column=col, padx=50, pady=50)

        tk.Label(card,
                 image=root.profile_photo,
                 bg=DARK_BG).pack(pady=5)

        tk.Label(card,
                 text="Anonymous",
                 fg=TEXT_COLOR,
                 bg=DARK_BG,
                 font=(BASE_FONT, 14, "bold")).pack()

        tk.Label(card,
                 text="★★★★★",
                 fg="gold",
                 bg=DARK_BG,
                 font=(BASE_FONT, 16)).pack()

        tk.Label(card,
                 text="Excellent vehicle and smooth experience!",
                 fg=TEXT_COLOR,
                 bg=DARK_BG,
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

# ---------------- START APP ----------------
register_page()
root.mainloop()