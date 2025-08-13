import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from seleniumwire import webdriver  # Use selenium-wire for proxy support
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from datetime import datetime
import re
import threading
import random
import time

class WebScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Concurrent Chrome Web Scraper with Proxy File Support")
        self.root.geometry("600x700")

        # Initialize WebDriver list and proxy list
        self.drivers = []  # Store active WebDriver instances
        self.proxy_list = []  # Store parsed proxies
        self.selected_proxy = tk.StringVar(value="None")

        # GUI Elements
        tk.Label(root, text="Enter URL to Scrape:", font=("Arial", 12)).pack(pady=10)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # Number of Concurrent Sessions
        tk.Label(root, text="Number of Concurrent Sessions (1-10):", font=("Arial", 10)).pack()
        self.sessions_entry = tk.Entry(root, width=10)
        self.sessions_entry.insert(0, "1")  # Default to 1 session
        self.sessions_entry.pack(pady=5)

        # Browser Mode Selection
        tk.Label(root, text="Browser Mode:", font=("Arial", 10)).pack()
        self.browser_mode = tk.StringVar(value="Headless")
        browser_modes = ["Headless", "Headed"]
        self.browser_mode_menu = ttk.Combobox(root, textvariable=self.browser_mode, values=browser_modes, state="readonly", width=15)
        self.browser_mode_menu.pack(pady=5)

        # Proxy Settings
        tk.Label(root, text="Proxy Settings:", font=("Arial", 12)).pack(pady=10)
        
        tk.Label(root, text="Proxy Type:", font=("Arial", 10)).pack()
        self.proxy_type = tk.StringVar(value="SOCKS5")  # Default to SOCKS5
        proxy_types = ["None", "SOCKS5"]
        self.proxy_type_menu = ttk.Combobox(root, textvariable=self.proxy_type, values=proxy_types, state="readonly", width=15)
        self.proxy_type_menu.pack(pady=5)

        tk.Label(root, text="Select Proxy (or Random if SOCKS5):", font=("Arial", 10)).pack()
        self.proxy_selector = ttk.Combobox(root, textvariable=self.selected_proxy, state="readonly", width=50)
        self.proxy_selector.pack(pady=5)
        self.proxy_selector['values'] = ["None"]

        tk.Button(root, text="Load Proxy File", command=self.load_proxy_file, font=("Arial", 10)).pack(pady=5)

        # Log Display
        tk.Label(root, text="Activity Log:", font=("Arial", 10)).pack(pady=5)
        self.log_text = tk.Text(root, height=8, width=60, state='disabled')
        self.log_text.pack(pady=5)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text['yscrollcommand'] = scrollbar.set

        # Buttons
        tk.Button(root, text="Start Scraping", command=self.scrape_url, font=("Arial", 12)).pack(pady=10)
        tk.Button(root, text="Stop All Browsers", command=self.stop_all_browsers, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="Clear Inputs", command=self.clear_inputs, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="Exit", command=self.exit_app, font=("Arial", 12)).pack(pady=5)

        self.status_label = tk.Label(root, text="Status: Ready", font=("Arial", 10))
        self.status_label.pack(pady=10)

        # Create output directory
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def log_message(self, message):
        """Append a timestamped message to the log display."""
        self.log_text.configure(state='normal')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def validate_url(self, url):
        """Validate the URL format."""
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    def validate_proxy(self, proxy):
        """Validate proxy string format (username:password@host:port or host:port)."""
        regex = re.compile(r'^(?:[\w]+:[\w]+@)?[\w\.-]+:\d+$')
        return re.match(regex, proxy) is not None

    def load_proxy_file(self):
        """Load and parse a proxy list from a .txt file."""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        self.proxy_list = []
        try:
            with open(file_path, 'r') as file:
                proxies = [line.strip() for line in file if line.strip()]
                for proxy in proxies:
                    if self.validate_proxy(proxy):
                        self.proxy_list.append(proxy)
                    else:
                        self.log_message(f"Invalid proxy format: {proxy}")
                        messagebox.showwarning("Warning", f"Invalid proxy format: {proxy}")
            
            if not self.proxy_list:
                self.log_message("No valid proxies found in file.")
                messagebox.showerror("Error", "No valid proxies found in file.")
                self.proxy_selector['values'] = ["None"]
                self.selected_proxy.set("None")
            else:
                self.proxy_selector['values'] = ["None"] + self.proxy_list
                self.selected_proxy.set("None")
                self.log_message(f"Loaded {len(self.proxy_list)} proxies from {file_path}")
                self.status_label.config(text=f"Status: Loaded {len(self.proxy_list)} proxies")
        except Exception as e:
            self.log_message(f"Failed to load proxy file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load proxy file: {str(e)}")
            self.proxy_selector['values'] = ["None"]
            self.selected_proxy.set("None")

    def start_browser_session(self, url, proxy_string, session_id):
        """Start a single browser session with a given proxy."""
        try:
            self.log_message(f"Session {session_id}: Starting browser session")
            
            # Set up Chrome options
            options = webdriver.ChromeOptions()
            if self.browser_mode.get() == "Headless":
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--ignore-certificate-errors")

            # Configure selenium-wire proxy options
            seleniumwire_options = {}
            if proxy_string and self.proxy_type.get() != "None":
                proxy_scheme = self.proxy_type.get().lower()
                seleniumwire_options = {
                    'proxy': {
                        'http': f"{proxy_scheme}://{proxy_string}",
                        'https': f"{proxy_scheme}://{proxy_string}",
                        'no_proxy': 'localhost,127.0.0.1'
                    }
                }
                self.log_message(f"Session {session_id}: Using proxy: {proxy_scheme}://{proxy_string}")

            # Initialize WebDriver
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options,
                seleniumwire_options=seleniumwire_options
            )

            # Store driver in list
            self.drivers.append(driver)

            # Navigate to URL
            self.log_message(f"Session {session_id}: Navigating to {url}")
            driver.get(url)

            # Wait 60 seconds for page to render
            self.log_message(f"Session {session_id}: Waiting 60 seconds before screenshot")
            time.sleep(60)

            # Capture screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_url = re.sub(r'[^\w\-_\. ]', '_', url)
            output_file = os.path.join(self.output_dir, f"screenshot_{safe_url}_session{session_id}_{timestamp}.png")
            if driver.save_screenshot(output_file):
                self.log_message(f"Session {session_id}: Screenshot saved to {output_file}")
            else:
                self.log_message(f"Session {session_id}: Failed to save screenshot")

        except Exception as e:
            self.log_message(f"Session {session_id}: Error: {str(e)}")
            if 'driver' in locals():
                driver.quit()

    def scrape_url(self):
        """Start multiple concurrent browser sessions with random proxies and staggered delays."""
        url = self.url_entry.get().strip()
        proxy_type = self.proxy_type.get()
        selected_proxy = self.selected_proxy.get()
        browser_mode = self.browser_mode.get()

        # Validate URL
        if not url:
            self.log_message("Error: No URL entered")
            messagebox.showerror("Error", "Please enter a URL.")
            return
        if not self.validate_url(url):
            self.log_message("Error: Invalid URL format")
            messagebox.showerror("Error", "Invalid URL format. Please include http:// or https://")
            return

        # Validate number of sessions
        try:
            num_sessions = int(self.sessions_entry.get())
            if not 1 <= num_sessions <= 10:
                self.log_message("Error: Number of sessions must be between 1 and 10")
                messagebox.showerror("Error", "Number of sessions must be between 1 and 10.")
                return
        except ValueError:
            self.log_message("Error: Invalid number of sessions")
            messagebox.showerror("Error", "Please enter a valid number of sessions.")
            return

        # Validate proxy if SOCKS5
        if proxy_type != "None" and not self.proxy_list and selected_proxy == "None":
            self.log_message("Error: No proxies loaded or selected")
            messagebox.showerror("Error", "Please load a proxy file or select a proxy.")
            return

        # Stop any existing browsers
        self.stop_all_browsers()

        self.log_message(f"Starting {num_sessions} browser sessions")
        self.status_label.config(text=f"Status: Starting {num_sessions} sessions...")

        # Schedule sessions with staggered delays
        def schedule_session(session_id, delay):
            proxy_string = None
            if proxy_type != "None":
                if self.proxy_list and selected_proxy == "None":
                    proxy_string = random.choice(self.proxy_list)
                elif selected_proxy != "None":
                    proxy_string = selected_proxy
            threading.Timer(delay, self.start_browser_session, args=(url, proxy_string, session_id)).start()

        for i in range(num_sessions):
            delay = random.uniform(30, 60) * i  # Cumulative delay: 0s, 30-60s, 60-120s, etc.
            self.log_message(f"Scheduling session {i+1} with delay {delay:.1f} seconds")
            schedule_session(i+1, delay)

        # Update status
        self.status_label.config(text=f"Status: Scheduled {num_sessions} browser sessions")
        messagebox.showinfo("Success", f"Scheduled {num_sessions} browser sessions at {url}")

    def stop_all_browsers(self):
        """Stop all active browser sessions."""
        if self.drivers:
            for driver in self.drivers:
                try:
                    driver.quit()
                except Exception as e:
                    self.log_message(f"Error closing browser: {str(e)}")
            self.drivers = []
            self.log_message("All browser sessions closed")
            self.status_label.config(text="Status: All browsers closed")
            messagebox.showinfo("Success", "All browser sessions closed")
        else:
            self.log_message("No browser sessions active")
            self.status_label.config(text="Status: No browser sessions active")

    def clear_inputs(self):
        """Clear all input fields."""
        self.url_entry.delete(0, tk.END)
        self.sessions_entry.delete(0, tk.END)
        self.sessions_entry.insert(0, "1")
        self.browser_mode.set("Headless")
        self.proxy_type.set("SOCKS5")
        self.selected_proxy.set("None")
        self.proxy_selector['values'] = ["None"]
        self.proxy_list = []
        self.log_message("Inputs cleared")
        self.status_label.config(text="Status: Ready")

    def exit_app(self):
        """Exit the application and close all browsers."""
        self.stop_all_browsers()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()