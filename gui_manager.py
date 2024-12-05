import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import sys
from threading import Thread

class URLManagerGUI:
    def __init__(self, root):
        print("\n=== Starting Application ===")
        self.root = root
        self.root.title("URL Manager")
        self.root.geometry("600x600")  # Made taller for run button
        
        # Use absolute path for config file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(script_dir, "config.json")
        print(f"Config file path: {self.config_file}")
        
        # Add window closing handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load configuration first
        print("Loading initial configuration...")
        self.load_config()
        
        # Create and setup UI components
        print("Setting up UI components...")
        self.setup_ui()
        
        # Update URL list after UI is ready
        print("Performing initial URL list update...")
        self.update_url_list()
        print("=== Initialization Complete ===\n")

    def setup_ui(self):
        """Setup all UI components"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Credentials Frame
        cred_frame = ttk.LabelFrame(main_frame, text="Login Credentials", padding="5")
        cred_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Username
        ttk.Label(cred_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.username_var = tk.StringVar(value=self.config.get('credentials', {}).get('username', ''))
        self.username_entry = ttk.Entry(cred_frame, textvariable=self.username_var)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Password
        ttk.Label(cred_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.password_var = tk.StringVar(value=self.config.get('credentials', {}).get('password', ''))
        self.password_entry = ttk.Entry(cred_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Show/Hide Password Button
        self.show_password = tk.BooleanVar(value=False)
        self.toggle_pwd_btn = ttk.Checkbutton(cred_frame, text="Show Password", 
                                            variable=self.show_password, 
                                            command=self.toggle_password_visibility)
        self.toggle_pwd_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # URL List
        ttk.Label(main_frame, text="URLs to Check:").grid(row=1, column=0, sticky=tk.W)
        
        # URL Listbox and Scrollbar
        self.url_listbox = tk.Listbox(main_frame, width=50, height=10)
        self.url_listbox.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.url_listbox.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.url_listbox.configure(yscrollcommand=scrollbar.set)
        
        # URL Entry
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        ttk.Button(button_frame, text="Add URL", command=self.add_url).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_url).pack(side=tk.LEFT, padx=5)
        
        # Speed Control Frame
        speed_frame = ttk.LabelFrame(main_frame, text="Navigation Speed", padding="5")
        speed_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Speed Slider
        self.delay_var = tk.DoubleVar(value=self.config.get('delay_seconds', 3))
        self.speed_slider = ttk.Scale(speed_frame, from_=0.5, to=10.0, 
                                    variable=self.delay_var, 
                                    orient=tk.HORIZONTAL,
                                    command=self.update_speed_label)
        self.speed_slider.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        speed_frame.columnconfigure(0, weight=1)
        
        # Speed Label
        self.speed_label = ttk.Label(speed_frame, text="")
        self.speed_label.grid(row=0, column=1, padx=5)
        self.update_speed_label()

        # Run Button Frame
        run_frame = ttk.Frame(main_frame)
        run_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        # Button Frame for Run and Exit
        button_frame = ttk.Frame(run_frame)
        button_frame.pack(pady=10)
        
        # Run Button
        run_button = ttk.Button(button_frame, text="Run Login Checker", 
                              command=self.run_login_checker,
                              style='Run.TButton')
        run_button.pack(side=tk.LEFT, padx=10)
        
        # Exit Button
        exit_button = ttk.Button(button_frame, text="Save & Exit", 
                               command=self.safe_exit,
                               style='Exit.TButton')
        exit_button.pack(side=tk.LEFT, padx=10)
        
        # Create custom styles
        style = ttk.Style()
        style.configure('Run.TButton', font=('Arial', 12, 'bold'))
        style.configure('Exit.TButton', font=('Arial', 12))
        
        # Status Label
        self.status_label = ttk.Label(run_frame, text="")
        self.status_label.pack(pady=5)
    
    def load_config(self):
        """Load configuration from config file"""
        print(f"\nLoading config from: {self.config_file}")
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Ensure all required fields exist
                    self.config = {
                        'use_gui': True,
                        'urls': loaded_config.get('urls', []),
                        'delay_seconds': loaded_config.get('delay_seconds', 3),
                        'credentials': loaded_config.get('credentials', {'username': '', 'password': ''})
                    }
                    print(f"Loaded config successfully. URLs in config: {self.config.get('urls', [])}")
            else:
                print("Config file does not exist, creating new config")
                self.config = {
                    'use_gui': True,
                    'urls': [],
                    'delay_seconds': 3,
                    'credentials': {
                        'username': '',
                        'password': ''
                    }
                }
                # Create the config file
                with open(self.config_file, 'w') as f:
                    json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            self.config = {
                'use_gui': True,
                'urls': [],
                'delay_seconds': 3,
                'credentials': {
                    'username': '',
                    'password': ''
                }
            }

    def save_config(self):
        """Save all settings to config file"""
        print("\nSaving configuration...")
        try:
            # Get current URLs from listbox
            urls = list(self.url_listbox.get(0, tk.END))
            print(f"Current URLs in listbox: {urls}")
            
            # Create new config with current values
            new_config = {
                'use_gui': True,
                'urls': urls,
                'delay_seconds': self.delay_var.get(),
                'credentials': {
                    'username': self.username_var.get(),
                    'password': self.password_var.get()
                }
            }
            
            print(f"Config to save - URLs: {new_config['urls']}")
            
            # Write to file
            with open(self.config_file, 'w') as f:
                json.dump(new_config, f, indent=4)
            print(f"Saved config to: {self.config_file}")
            
            # Update our current config
            self.config = new_config.copy()
            
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def update_url_list(self):
        """Update the URL listbox with URLs from config"""
        print("\nUpdating URL listbox")
        print(f"Current config URLs before update: {self.config.get('urls', [])}")
        
        # Clear the listbox
        self.url_listbox.delete(0, tk.END)
        
        # Get URLs from config
        urls = self.config.get('urls', [])
        print(f"URLs from config to add to listbox: {urls}")
        
        # Add URLs to listbox
        for url in urls:
            self.url_listbox.insert(tk.END, url)
        
        print(f"URL listbox now contains: {list(self.url_listbox.get(0, tk.END))}")

    def add_url(self):
        """Add a URL to the list and save"""
        url = self.url_var.get().strip()
        if url:
            print(f"\nAdding URL: {url}")
            self.url_listbox.insert(tk.END, url)
            self.url_var.set("")
            self.save_config()  # Save after adding
            # Show confirmation
            self.root.bell()
            messagebox.showinfo("Success", f"Added URL: {url}")
            
    def remove_url(self):
        """Remove selected URL from the list and save"""
        selection = self.url_listbox.curselection()
        if selection:
            url = self.url_listbox.get(selection)
            self.url_listbox.delete(selection)
            print(f"\nRemoving URL: {url}")
            self.save_config()
            # Show confirmation
            self.root.bell()
            messagebox.showinfo("Success", f"Removed URL: {url}")
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        self.password_entry.config(show="" if self.show_password.get() else "*")

    def update_speed_label(self, *args):
        """Update the label showing current delay value"""
        delay = self.delay_var.get()
        self.speed_label.config(text=f"{delay:.1f} seconds")
        # Don't automatically save here
        self.config['delay_seconds'] = delay

    def run_login_checker(self):
        """Run the login checker script"""
        if not self.config['urls']:
            messagebox.showerror("Error", "Please add at least one URL before running")
            self.status_label.config(text="Error: No URLs configured")
            return
        
        if not self.config['credentials']['username'] or not self.config['credentials']['password']:
            messagebox.showerror("Error", "Please set username and password before running")
            self.status_label.config(text="Error: Missing credentials")
            return
            
        # Save current settings before running
        self.save_config()
        
        # Update status
        self.status_label.config(text="Running login checker...")
        self.root.update()
        
        # Get the path to login_checker.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        login_checker_path = os.path.join(script_dir, 'login_checker.py')
        
        # Run in a separate thread to keep GUI responsive
        def run_script():
            try:
                # Run the login checker script
                process = subprocess.Popen([sys.executable, login_checker_path],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True)
                
                # Get output
                stdout, stderr = process.communicate()
                
                # Process the output to extract status messages
                status_messages = []
                current_url = None
                errors_found = []
                
                for line in stdout.split('\n'):
                    if "Testing login for:" in line:
                        current_url = line.split("Testing login for:", 1)[1].strip()
                        status_messages.append(f"\nTesting: {current_url}")
                    elif "Found error message:" in line:
                        error_msg = line.split("Found error message:", 1)[1].strip()
                        status_messages.append(f"Error: {error_msg}")
                        # Store error details for popup
                        if current_url:
                            errors_found.append({
                                'url': current_url,
                                'error': error_msg,
                                'type': 'Login Error'
                            })
                    elif "Login Failed -" in line:
                        fail_msg = line.strip()
                        status_messages.append(f"Failed: {fail_msg}")
                        # Store failure details for popup
                        if current_url:
                            errors_found.append({
                                'url': current_url,
                                'error': fail_msg,
                                'type': 'Login Failure'
                            })
                    elif "Success" in line:
                        status_messages.append("Success!")
                    elif "Timeout -" in line:
                        timeout_msg = line.strip()
                        status_messages.append(f"Timeout: {timeout_msg}")
                        if current_url:
                            errors_found.append({
                                'url': current_url,
                                'error': timeout_msg,
                                'type': 'Timeout Error'
                            })
                
                # Update status based on result
                if process.returncode == 0:
                    if status_messages:
                        final_status = "\n".join(status_messages)
                        self.root.after(0, lambda: self.status_label.config(
                            text=final_status))
                        
                        # Show error popup if errors were found
                        if errors_found:
                            self.root.after(0, lambda: self.show_error_details(errors_found))
                    else:
                        self.root.after(0, lambda: self.status_label.config(
                            text="Login checker completed successfully"))
                else:
                    error_msg = stderr if stderr else "Unknown error occurred"
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Error: {error_msg}"))
                    # Show system error popup
                    self.root.after(0, lambda: messagebox.showerror(
                        "System Error",
                        f"An error occurred while running the login checker:\n{error_msg}"
                    ))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Error: {error_msg}"))
                # Show exception popup
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"An unexpected error occurred:\n{error_msg}"
                ))
    
        # Start the thread
        Thread(target=run_script, daemon=True).start()

    def show_error_details(self, errors):
        """Show a detailed error report in a popup window"""
        # Create a new top-level window
        error_window = tk.Toplevel(self.root)
        error_window.title("Login Check Results")
        error_window.geometry("600x400")
        
        # Add a frame with scrollbar
        frame = ttk.Frame(error_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrolled text widget
        text_widget = tk.Text(frame, wrap=tk.WORD, width=70, height=20)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack the widgets
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add a title
        text_widget.tag_configure("title", font=("Arial", 12, "bold"))
        text_widget.tag_configure("error_type", font=("Arial", 10, "bold"), foreground="red")
        text_widget.tag_configure("url", font=("Arial", 10, "italic"))
        
        text_widget.insert(tk.END, "Login Check Error Report\n\n", "title")
        
        # Add error details
        for i, error in enumerate(errors, 1):
            text_widget.insert(tk.END, f"{i}. Error Type: ", "")
            text_widget.insert(tk.END, f"{error['type']}\n", "error_type")
            text_widget.insert(tk.END, f"   URL: ", "")
            text_widget.insert(tk.END, f"{error['url']}\n", "url")
            text_widget.insert(tk.END, f"   Details: {error['error']}\n\n")
        
        # Make text widget read-only
        text_widget.configure(state='disabled')
        
        # Add close button
        ttk.Button(error_window, text="Close", command=error_window.destroy).pack(pady=10)
        
        # Center the window on screen
        error_window.update_idletasks()
        width = error_window.winfo_width()
        height = error_window.winfo_height()
        x = (error_window.winfo_screenwidth() // 2) - (width // 2)
        y = (error_window.winfo_screenheight() // 2) - (height // 2)
        error_window.geometry(f'{width}x{height}+{x}+{y}')

    def safe_exit(self):
        """Safely exit the application after saving"""
        try:
            print("Saving configuration before exit...")
            self.save_config()
            print("Save completed, closing application...")
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Error during save: {str(e)}")
            if messagebox.askokcancel("Error", 
                "There was an error saving your settings. Do you still want to exit?"):
                self.root.destroy()

    def on_closing(self):
        """Handle window closing event"""
        print("\nWindow closing event triggered")
        try:
            self.save_config()
            print("Configuration saved successfully before exit")
        except Exception as e:
            print(f"Error saving configuration during exit: {str(e)}")
        self.root.destroy()

def launch_gui():
    root = tk.Tk()
    app = URLManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
