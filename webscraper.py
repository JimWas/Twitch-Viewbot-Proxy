import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from seleniumwire.undetected_chromedriver import Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
import os
from datetime import datetime
import re
import threading
import random
import time

class BrowserSession:
    """Class to represent a browser session with metadata"""
    def __init__(self, session_id, driver, url, proxy_string, start_time):
        self.session_id = session_id
        self.driver = driver
        self.url = url
        self.proxy_string = proxy_string
        self.start_time = start_time
        self.status = "Running"

class WebScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ILLPHATED TWITCH UNLIMITED PROXY VIEWERBOT DOWNLOAD AT ILLPHATED.COM")
        self.root.geometry("1000x900")  # Increased height for new controls

        # Initialize WebDriver list and proxy list
        self.browser_sessions = {}  # Store active BrowserSession instances
        self.proxy_list = []  # Store parsed proxies
        self.selected_proxy = tk.StringVar(value="None")
        
        # List of popular user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/139.0.0.0",
            "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
        ]
        self.default_user_agent = self.user_agents[0]
        self.selected_user_agent = tk.StringVar(value="Random")

        # Create main frames
        self.create_main_layout()

    def create_main_layout(self):
        """Create the main layout with left panel for controls and right panel for resource monitor"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_frame = tk.Frame(main_frame, relief=tk.RAISED, borderwidth=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))

        right_frame = tk.Frame(main_frame, relief=tk.RAISED, borderwidth=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_controls(left_frame)
        self.create_resource_monitor(right_frame)

        # Create output directory
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_controls(self, parent):
        """Create the control panel"""
        tk.Label(parent, text="CONTROLS", font=("Arial", 14, "bold")).pack(pady=5)

        tk.Label(parent, text="ENTER TWITCH URL:", font=("Arial", 12)).pack(pady=5)
        self.url_entry = tk.Entry(parent, width=40)
        self.url_entry.pack(pady=5)

        tk.Label(parent, text="Number of Concurrent Sessions:", font=("Arial", 10)).pack()
        self.sessions_entry = tk.Entry(parent, width=10)
        self.sessions_entry.insert(0, "1")
        self.sessions_entry.pack(pady=5)

        tk.Label(parent, text="Browser Mode:", font=("Arial", 10)).pack()
        self.browser_mode = tk.StringVar(value="Headed")  # Default to Headed
        browser_modes = ["Headless", "Headed"]
        self.browser_mode_menu = ttk.Combobox(parent, textvariable=self.browser_mode, values=browser_modes, state="readonly", width=15)
        self.browser_mode_menu.pack(pady=5)

        # Page Interaction Settings
        interaction_frame = tk.LabelFrame(parent, text="Page Interaction Settings", font=("Arial", 11, "bold"))
        interaction_frame.pack(pady=10, padx=5, fill="x")

        tk.Label(interaction_frame, text="Number of Page Scrolls:", font=("Arial", 10)).pack()
        self.scroll_count_entry = tk.Entry(interaction_frame, width=10)
        self.scroll_count_entry.insert(0, "2")  # Default value
        self.scroll_count_entry.pack(pady=2)

        tk.Label(interaction_frame, text="Enable Mouse Movement:", font=("Arial", 10)).pack()
        self.enable_mouse_movement = tk.BooleanVar(value=True)
        tk.Checkbutton(interaction_frame, variable=self.enable_mouse_movement, text="Simulate Human Mouse Movement").pack()

        tk.Label(interaction_frame, text="Number of Mouse Movements:", font=("Arial", 10)).pack()
        self.mouse_movement_count_entry = tk.Entry(interaction_frame, width=10)
        self.mouse_movement_count_entry.insert(0, "5")  # Default value
        self.mouse_movement_count_entry.pack(pady=2)

        tk.Label(parent, text="Select User Agent:", font=("Arial", 10)).pack()
        user_agent_options = ["Random"] + self.user_agents
        self.user_agent_menu = ttk.Combobox(parent, textvariable=self.selected_user_agent, values=user_agent_options, state="readonly", width=50)
        self.user_agent_menu.pack(pady=5)
        tk.Button(parent, text="Reset to Default User Agent", command=self.reset_user_agent, font=("Arial", 9)).pack(pady=2)

        tk.Label(parent, text="Proxy Settings:", font=("Arial", 12)).pack(pady=10)
        
        tk.Label(parent, text="Proxy Type:", font=("Arial", 10)).pack()
        self.proxy_type = tk.StringVar(value="SOCKS5")
        proxy_types = ["None", "SOCKS5", "HTTP"]
        self.proxy_type_menu = ttk.Combobox(parent, textvariable=self.proxy_type, values=proxy_types, state="readonly", width=15)
        self.proxy_type_menu.pack(pady=5)

        tk.Label(parent, text="Select Proxy:", font=("Arial", 10)).pack()
        self.proxy_selector = ttk.Combobox(parent, textvariable=self.selected_proxy, state="readonly", width=40)
        self.proxy_selector.pack(pady=5)
        self.proxy_selector['values'] = ["None"]

        tk.Button(parent, text="Load Proxy File", command=self.load_proxy_file, font=("Arial", 10)).pack(pady=5)

        tk.Label(parent, text="Activity Log:", font=("Arial", 10)).pack(pady=5)
        log_frame = tk.Frame(parent)
        log_frame.pack(pady=5)
        
        self.log_text = tk.Text(log_frame, height=8, width=50, state='disabled')
        log_scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

        tk.Button(parent, text="Start VIEWERS", command=self.scrape_url, font=("Arial", 12), bg="green", fg="white").pack(pady=5)
        tk.Button(parent, text="Stop All VIEWERS", command=self.stop_all_browsers, font=("Arial", 12), bg="red", fg="white").pack(pady=2)
        tk.Button(parent, text="Clear Inputs", command=self.clear_inputs, font=("Arial", 12)).pack(pady=2)
        tk.Button(parent, text="Exit", command=self.exit_app, font=("Arial", 12)).pack(pady=2)

        self.status_label = tk.Label(parent, text="Status: Ready", font=("Arial", 10))
        self.status_label.pack(pady=5)

    def create_resource_monitor(self, parent):
        """Create the resource monitor panel"""
        tk.Label(parent, text="RESOURCE MONITOR", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.session_count_label = tk.Label(parent, text="Active Sessions: 0", font=("Arial", 12))
        self.session_count_label.pack(pady=5)

        tk.Button(parent, text="Refresh", command=self.update_resource_monitor, font=("Arial", 10)).pack(pady=2)

        columns = ("ID", "Status", "URL", "Proxy", "Start Time", "Duration")
        self.session_tree = ttk.Treeview(parent, columns=columns, show='headings', height=20)
        
        self.session_tree.heading("ID", text="Session ID")
        self.session_tree.heading("Status", text="Status")
        self.session_tree.heading("URL", text="URL")
        self.session_tree.heading("Proxy", text="Proxy")
        self.session_tree.heading("Start Time", text="Start Time")
        self.session_tree.heading("Duration", text="Duration")
        
        self.session_tree.column("ID", width=80, anchor="center")
        self.session_tree.column("Status", width=80, anchor="center")
        self.session_tree.column("URL", width=200, anchor="w")
        self.session_tree.column("Proxy", width=150, anchor="w")
        self.session_tree.column("Start Time", width=130, anchor="center")
        self.session_tree.column("Duration", width=100, anchor="center")

        tree_frame = tk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.session_tree.yview)
        self.session_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.session_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")

        self.session_tree.bind("<Button-1>", self.on_session_left_click)
        self.session_tree.bind("<Button-3>", self.on_session_right_click)
        self.session_tree.bind("<Double-1>", self.on_session_double_click)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Restart Session", command=self.restart_selected_session)
        self.context_menu.add_command(label="Close Session", command=self.close_selected_session)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Details", command=self.view_session_details)

        self.auto_refresh_monitor()

    def simulate_human_mouse_movement(self, driver, num_movements):
        """Simulate human-like mouse movements on the page"""
        try:
            actions = ActionChains(driver)
            
            # Get viewport dimensions
            viewport_width = driver.execute_script("return window.innerWidth")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            self.log_message(f"Simulating {num_movements} mouse movements in viewport {viewport_width}x{viewport_height}")
            
            for i in range(num_movements):
                # Generate random coordinates within viewport
                x = random.randint(50, viewport_width - 50)
                y = random.randint(50, viewport_height - 50)
                
                # Move to random position with human-like timing
                actions.move_by_offset(x - (viewport_width // 2), y - (viewport_height // 2))
                actions.pause(random.uniform(0.5, 2.0))  # Random pause between movements
                
                # Occasionally perform a click (10% chance)
                if random.random() < 0.1:
                    actions.click()
                    actions.pause(random.uniform(0.2, 0.8))
                
                # Reset to center occasionally to avoid moving off-screen
                if i % 3 == 0:
                    actions.move_to_element_with_offset(driver.find_element("tag name", "body"), 
                                                      viewport_width // 2, viewport_height // 2)
            
            # Execute all actions
            actions.perform()
            self.log_message(f"Completed {num_movements} mouse movements")
            
        except Exception as e:
            self.log_message(f"Mouse movement simulation error: {str(e)}")

    def auto_refresh_monitor(self):
        """Auto-refresh the resource monitor every 5 seconds"""
        self.update_resource_monitor()
        self.root.after(5000, self.auto_refresh_monitor)

    def update_resource_monitor(self):
        """Update the resource monitor display"""
        for item in self.session_tree.get_children():
            self.session_tree.delete(item)

        active_count = len(self.browser_sessions)
        self.session_count_label.config(text=f"Active Sessions: {active_count}")

        for session_id, session in self.browser_sessions.items():
            try:
                session.driver.current_url
                session.status = "Running"
            except:
                session.status = "Dead"

            duration = datetime.now() - session.start_time
            duration_str = str(duration).split('.')[0]

            display_url = session.url if len(session.url) <= 30 else session.url[:27] + "..."
            display_proxy = (
                session.proxy_string if session.proxy_string and len(session.proxy_string) <= 20
                else (session.proxy_string[:17] + "..." if session.proxy_string else "None")
            )

            self.session_tree.insert("", "end", values=(
                session.session_id,
                session.status,
                display_url,
                display_proxy,
                session.start_time.strftime("%H:%M:%S"),
                duration_str
            ))

    def on_session_left_click(self, event):
        """Handle left click on session (select)"""
        item = self.session_tree.selection()[0] if self.session_tree.selection() else None
        if item:
            self.selected_session_item = item

    def on_session_right_click(self, event):
        """Handle right click on session (show context menu)"""
        item = self.session_tree.identify_row(event.y)
        if item:
            self.session_tree.selection_set(item)
            self.selected_session_item = item
            self.context_menu.post(event.x_root, event.y_root)

    def on_session_double_click(self, event):
        """Handle double click on session (restart)"""
        self.restart_selected_session()

    def restart_selected_session(self):
        """Restart the selected session"""
        if not hasattr(self, 'selected_session_item') or not self.selected_session_item:
            messagebox.showwarning("Warning", "Please select a session first.")
            return

        values = self.session_tree.item(self.selected_session_item)['values']
        session_id = values[0]
        
        if session_id in self.browser_sessions:
            session = self.browser_sessions[session_id]
            
            try:
                session.driver.quit()
            except:
                pass
            
            self.log_message(f"Restarting session {session_id}")
            
            threading.Thread(
                target=self.start_browser_session,
                args=(session.url, session.proxy_string, session_id, True)
            ).start()

    def close_selected_session(self):
        """Close the selected session"""
        if not hasattr(self, 'selected_session_item') or not self.selected_session_item:
            messagebox.showwarning("Warning", "Please select a session first.")
            return

        values = self.session_tree.item(self.selected_session_item)['values']
        session_id = values[0]
        
        if session_id in self.browser_sessions:
            session = self.browser_sessions[session_id]
            
            try:
                session.driver.quit()
                self.log_message(f"Closed session {session_id}")
            except Exception as e:
                self.log_message(f"Error closing session {session_id}: {str(e)}")
            
            del self.browser_sessions[session_id]
            self.update_resource_monitor()

    def view_session_details(self):
        """Show details of selected session"""
        if not hasattr(self, 'selected_session_item') or not self.selected_session_item:
            messagebox.showwarning("Warning", "Please select a session first.")
            return

        values = self.session_tree.item(self.selected_session_item)['values']
        session_id = values[0]
        
        if session_id in self.browser_sessions:
            session = self.browser_sessions[session_id]
            
            details = f"""Session Details:
ID: {session.session_id}
Status: {session.status}
URL: {session.url}
Proxy: {session.proxy_string or 'None'}
Start Time: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {str(datetime.now() - session.start_time).split('.')[0]}"""
            
            messagebox.showinfo(f"Session {session_id} Details", details)

    def reset_user_agent(self):
        """Reset user agent to default value"""
        self.selected_user_agent.set(self.default_user_agent)
        self.log_message("User agent reset to default")

    def log_message(self, message):
        """Append a timestamped message to the log display"""
        self.log_text.configure(state='normal')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')

    def validate_url(self, url):
        """Validate the URL format"""
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    def validate_proxy(self, proxy):
        """Validate proxy string format (username:password@host:port or host:port:username:password or host:port)"""
        regex = re.compile(
            r'^(?:[\w]+:[\w]+@[a-zA-Z0-9.-]+:\d+$|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+:[\w]+:[\w]+$|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$)'
        )
        return re.match(regex, proxy) is not None

    def parse_proxy(self, proxy_string):
        """Parse proxy string into components (host, port, username, password)"""
        try:
            if '@' in proxy_string:
                auth, host_port = proxy_string.split('@')
                username, password = auth.split(':')
                host, port = host_port.split(':')
            elif proxy_string.count(':') == 3:
                host, port, username, password = proxy_string.split(':')
            else:
                host, port = proxy_string.split(':')
                username, password = None, None
            return host, port, username, password
        except Exception:
            return None, None, None, None

    def load_proxy_file(self):
        """Load and parse a proxy list from a .txt file"""
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

    def start_browser_session(self, url, proxy_string, session_id, is_restart=False):
        """Start a single browser session with a given proxy"""
        try:
            if not is_restart:
                self.log_message(f"Session {session_id}: Starting browser session")
            else:
                self.log_message(f"Session {session_id}: Restarting browser session")
            
            # Set up Chrome options
            options = ChromeOptions()
            if self.browser_mode.get() == "Headless":
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-extensions")

            # Select user agent
            selected_user_agent = self.selected_user_agent.get()
            user_agent = random.choice(self.user_agents) if selected_user_agent == "Random" else selected_user_agent
            options.add_argument(f"--user-agent={user_agent}")
            self.log_message(f"Session {session_id}: Using user agent: {user_agent}")

            # Configure selenium-wire proxy options
            seleniumwire_options = {'disable_encoding': True}
            if proxy_string and self.proxy_type.get() != "None":
                proxy_scheme = self.proxy_type.get().lower()
                host, port, username, password = self.parse_proxy(proxy_string)
                if not host or not port:
                    self.log_message(f"Session {session_id}: Invalid proxy format: {proxy_string}")
                    return

                proxy_string_formatted = f"{host}:{port}"
                if username and password:
                    seleniumwire_options['proxy'] = {
                        'http': f"{proxy_scheme}://{username}:{password}@{host}:{port}",
                        'https': f"{proxy_scheme}://{username}:{password}@{host}:{port}",
                        'no_proxy': 'localhost,127.0.0.1'
                    }
                else:
                    seleniumwire_options['proxy'] = {
                        'http': f"{proxy_scheme}://{host}:{port}",
                        'https': f"{proxy_scheme}://{host}:{port}",
                        'no_proxy': 'localhost,127.0.0.1'
                    }
                self.log_message(f"Session {session_id}: Using proxy: {proxy_scheme}://{proxy_string_formatted}")

            # Initialize WebDriver with retry logic
            max_attempts = 2
            for attempt in range(1, max_attempts + 1):
                try:
                    driver = Chrome(options=options, seleniumwire_options=seleniumwire_options, version_main=139)
                    self.log_message(f"Session {session_id}: ChromeDriver initialized successfully")
                    break
                except Exception as e:
                    self.log_message(f"Session {session_id}: ChromeDriver init attempt {attempt} failed: {str(e)}")
                    if attempt == max_attempts:
                        self.log_message(f"Session {session_id}: Failed to initialize ChromeDriver after {max_attempts} attempts")
                        return
                    time.sleep(2)

            # Set browser resolution
            try:
                driver.set_window_size(1280, 720)
                self.log_message(f"Session {session_id}: Set resolution to 1280x720")
            except NoSuchWindowException:
                self.log_message(f"Session {session_id}: Window closed during resolution setup")
                driver.quit()
                return

            # Create browser session object
            session = BrowserSession(
                session_id=session_id,
                driver=driver,
                url=url,
                proxy_string=proxy_string,
                start_time=datetime.now()
            )
            
            # Store session
            self.browser_sessions[session_id] = session

            # Navigate to URL with retry logic
            max_nav_attempts = 2
            for attempt in range(1, max_nav_attempts + 1):
                try:
                    self.log_message(f"Session {session_id}: Navigating to {url} (attempt {attempt})")
                    driver.get(url)
                    break
                except (NoSuchWindowException, WebDriverException) as e:
                    self.log_message(f"Session {session_id}: Navigation failed: {str(e)}")
                    if attempt == max_nav_attempts:
                        self.log_message(f"Session {session_id}: Navigation failed after {max_nav_attempts} attempts")
                        driver.quit()
                        del self.browser_sessions[session_id]
                        return
                    time.sleep(2)

            # Wait for page to render
            self.log_message(f"Session {session_id}: Waiting 30 seconds before page interaction")
            time.sleep(30)
            
            # Get scroll count from user input
            try:
                scroll_count = int(self.scroll_count_entry.get())
                scroll_count = max(0, min(scroll_count, 20))  # Limit between 0 and 20
            except ValueError:
                scroll_count = 2
                self.log_message(f"Session {session_id}: Invalid scroll count, using default: 2")

            # Perform scrolling if requested
            if scroll_count > 0:
                try:
                    for i in range(scroll_count):
                        driver.execute_script("window.scrollBy({ top: window.innerHeight, behavior: 'smooth' });")
                        self.log_message(f"Session {session_id}: Scrolled down by screen {i+1} (smooth)")
                        time.sleep(random.uniform(1.5, 3.0))  # Random pause between scrolls
                    
                    time.sleep(2)  # Final pause to allow page to settle
                    self.log_message(f"Session {session_id}: Completed {scroll_count} smooth scrolls")
                except Exception as e:
                    self.log_message(f"Session {session_id}: Scroll error: {str(e)}")

            # Perform mouse movements if enabled
            if self.enable_mouse_movement.get():
                try:
                    mouse_movement_count = int(self.mouse_movement_count_entry.get())
                    mouse_movement_count = max(0, min(mouse_movement_count, 50))  # Limit between 0 and 50
                    
                    if mouse_movement_count > 0:
                        self.simulate_human_mouse_movement(driver, mouse_movement_count)
                        time.sleep(random.uniform(2, 5))  # Random pause after mouse movements
                except ValueError:
                    self.log_message(f"Session {session_id}: Invalid mouse movement count, skipping mouse simulation")
                except Exception as e:
                    self.log_message(f"Session {session_id}: Mouse movement error: {str(e)}")
                
            # Capture screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_url = re.sub(r'[^\w\-_\. ]', '_', url)
            output_file = os.path.join(self.output_dir, f"screenshot_{safe_url}_session{session_id}_{timestamp}.png")
            try:
                if driver.save_screenshot(output_file):
                    self.log_message(f"Session {session_id}: Screenshot saved to {output_file}")
                else:
                    self.log_message(f"Session {session_id}: Failed to save screenshot")
            except (NoSuchWindowException, WebDriverException) as e:
                self.log_message(f"Session {session_id}: Screenshot error: {str(e)}")
                driver.quit()
                del self.browser_sessions[session_id]
                return

        except Exception as e:
            self.log_message(f"Session {session_id}: Error: {str(e)}")
            if session_id in self.browser_sessions:
                del self.browser_sessions[session_id]
            if 'driver' in locals():
                try:
                    driver.quit()
                except:
                    pass

    def scrape_url(self):
        """Start multiple concurrent browser sessions with random proxies and staggered delays"""
        url = self.url_entry.get().strip()
        proxy_type = self.proxy_type.get()
        selected_proxy = self.selected_proxy.get()
        selected_user_agent = self.selected_user_agent.get()

        if not url:
            self.log_message("Error: No URL entered")
            messagebox.showerror("Error", "Please enter a URL.")
            return
        if not self.validate_url(url):
            self.log_message("Error: Invalid URL format")
            messagebox.showerror("Error", "Invalid URL format. Please include http:// or https://")
            return

        try:
            num_sessions = int(self.sessions_entry.get())
            if not 1 <= num_sessions <= 999:
                self.log_message("Error: Number of sessions must be between 1 and 999")
                messagebox.showerror("Error", "Number of sessions must be between 1 and 999.")
                return
        except ValueError:
            self.log_message("Error: Invalid number of sessions")
            messagebox.showerror("Error", "Please enter a valid number of sessions.")
            return

        # Validate scroll count
        try:
            scroll_count = int(self.scroll_count_entry.get())
            if not 0 <= scroll_count <= 20:
                self.log_message("Error: Number of scrolls must be between 0 and 20")
                messagebox.showerror("Error", "Number of scrolls must be between 0 and 20.")
                return
        except ValueError:
            self.log_message("Error: Invalid scroll count")
            messagebox.showerror("Error", "Please enter a valid number for page scrolls.")
            return

        # Validate mouse movement count
        if self.enable_mouse_movement.get():
            try:
                mouse_count = int(self.mouse_movement_count_entry.get())
                if not 0 <= mouse_count <= 50:
                    self.log_message("Error: Number of mouse movements must be between 0 and 50")
                    messagebox.showerror("Error", "Number of mouse movements must be between 0 and 50.")
                    return
            except ValueError:
                self.log_message("Error: Invalid mouse movement count")
                messagebox.showerror("Error", "Please enter a valid number for mouse movements.")
                return

        if proxy_type != "None" and not self.proxy_list and selected_proxy == "None":
            self.log_message("Error: No proxies loaded or selected")
            messagebox.showerror("Error", "Please load a proxy file or select a proxy.")
            return

        if selected_user_agent != "Random" and selected_user_agent not in self.user_agents:
            self.log_message("Error: Invalid user agent selected, resetting to default")
            self.selected_user_agent.set(self.default_user_agent)

        self.log_message(f"Starting {num_sessions} browser sessions with {scroll_count} scrolls and {'enabled' if self.enable_mouse_movement.get() else 'disabled'} mouse movement")
        self.status_label.config(text=f"Status: Starting {num_sessions} sessions...")

        existing_ids = set(self.browser_sessions.keys())
        session_counter = 1
        while len(str(session_counter)) < 3 or session_counter in existing_ids:
            session_counter += 1

        def schedule_session(session_id, delay):
            proxy_string = None
            if proxy_type != "None":
                if self.proxy_list and selected_proxy == "None":
                    proxy_string = random.choice(self.proxy_list)
                elif selected_proxy != "None":
                    proxy_string = selected_proxy
            threading.Timer(delay, self.start_browser_session, args=(url, proxy_string, session_id)).start()

        for i in range(num_sessions):
            session_id = session_counter + i  # Define session_id here
            delay = random.uniform(5, 15) * i
            self.log_message(f"Scheduling session {session_id} with delay {delay:.1f} seconds")
            schedule_session(session_id, delay)

        self.status_label.config(text=f"Status: Scheduled {num_sessions} browser sessions")
        messagebox.showinfo("Success", f"Scheduled {num_sessions} browser sessions at {url}")

    def stop_all_browsers(self):
        """Stop all active browser sessions"""
        if self.browser_sessions:
            for session_id, session in self.browser_sessions.items():
                try:
                    session.driver.quit()
                    self.log_message(f"Closed session {session_id}")
                except Exception as e:
                    self.log_message(f"Error closing session {session_id}: {str(e)}")
            
            self.browser_sessions.clear()
            self.log_message("All browser sessions closed")
            self.status_label.config(text="Status: All browsers closed")
            self.update_resource_monitor()
            messagebox.showinfo("Success", "All browser sessions closed")
        else:
            self.log_message("No browser sessions active")
            self.status_label.config(text="Status: No browser sessions active")

    def clear_inputs(self):
        """Clear all input fields"""
        self.url_entry.delete(0, tk.END)
        self.sessions_entry.delete(0, tk.END)
        self.sessions_entry.insert(0, "1")
        self.scroll_count_entry.delete(0, tk.END)
        self.scroll_count_entry.insert(0, "2")
        self.mouse_movement_count_entry.delete(0, tk.END)
        self.mouse_movement_count_entry.insert(0, "5")
        self.enable_mouse_movement.set(True)
        self.browser_mode.set("Headed")
        self.proxy_type.set("SOCKS5")
        self.selected_proxy.set("None")
        self.proxy_selector['values'] = ["None"]
        self.proxy_list = []
        self.selected_user_agent.set("Random")
        self.log_message("Inputs cleared")
        self.status_label.config(text="Status: Ready")

    def exit_app(self):
        """Exit the application and close all browsers"""
        self.stop_all_browsers()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()
