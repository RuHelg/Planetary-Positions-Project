import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def generate_file():
    date = date_entry.get()
    text = text_entry.get()
    
    if not date or not text:
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return
    
    with open("config.txt", "w") as file:
        file.write(f"Date: '{date}'\n")
        file.write(f"Text: '{text}'\n")
    
    messagebox.showinfo("Success", "The config.txt file has been generated.\n\nPlease click on the [Create STL & plot-files] button after closing this window")
    #root.quit()  # Close the main window after execution

def run_main(): 
    try: 
        # Activate the virtual environment and run main.py 
        venv_path = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python') 
        subprocess.run([venv_path, "main.py"], check=True) 
        messagebox.showinfo("Success", "You have now these files on your computer: \n plot_3D.png, plot_2D.png & solar_system.stl") 
        root.quit()  # Close the main window after execution
    except subprocess.CalledProcessError as e: 
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("Input info")

# Add instruction text
instruction_label = tk.Label(root, text="Please add your desired date and text in the boxes below.\n Please use date format as (dd.mm.yyyy)")
instruction_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# Create and place the date label and entry
tk.Label(root, text="Date:").grid(row=1, column=0, padx=10, pady=10)
date_entry = tk.Entry(root)
date_entry.grid(row=1, column=1, padx=10, pady=10)

# Create and place the text label and entry
tk.Label(root, text="Text:").grid(row=2, column=0, padx=10, pady=10)
text_entry = tk.Entry(root)
text_entry.grid(row=2, column=1, padx=10, pady=10)

# Create and place the generate button
generate_button = tk.Button(root, text="Save Information", command=generate_file)
generate_button.grid(row=3, column=0, columnspan=2, pady=10)

# Create and place the run button
run_button = tk.Button(root, text="Create STL & plot-files", command=run_main)
run_button.grid(row=4, column=0, columnspan=2, pady=10)

# Run the application
root.mainloop()

