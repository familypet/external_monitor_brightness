import tkinter as tk
from tkinter import ttk
import logging
import screen_brightness_control as sbc
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class BrightnessControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Brightness Control")
        
        # Initialize monitor data
        self.monitors = []
        self.last_update_time = {}
        self.previous_slider_values = {}  # Track previous slider values
        self.running = True  # Flag to control the background thread

        # Create GUI elements
        self.create_widgets()

        # Start a background thread to handle brightness updates
        self.start_brightness_thread()

        # Bind the ESC key to close the program
        self.root.bind("<Escape>", self.close_program)

    def list_monitors(self):
        """
        List all connected monitors and their current brightness levels.
        
        Returns:
            List[Dict]: A list of dictionaries containing monitor information.
        """
        try:
            monitors = sbc.list_monitors_info()
            for i, monitor in enumerate(monitors):
                try:
                    current_brightness = sbc.get_brightness(display=monitor['serial'] or i)
                    
                    # Handle cases where brightness is returned as a list
                    if isinstance(current_brightness, list):
                        current_brightness = current_brightness[0]  # Use the first value
                    
                    # Add an 'index' field to uniquely identify monitors without a serial
                    monitor['index'] = i
                    monitor['brightness'] = current_brightness  # Store current brightness
                    self.previous_slider_values[i] = current_brightness  # Initialize previous slider values
                    logging.info(f"Monitor: {monitor['name']}, Serial: {monitor['serial']}, Index: {i}, Current Brightness: {current_brightness}%")
                except Exception as e:
                    logging.error(f"Error initializing monitor {monitor['name']} (Index: {i}): {e}")
                    continue  # Skip this monitor if an error occurs
            
            return monitors
        except Exception as e:
            logging.error(f"Error listing monitors: {e}")
            return []

    def create_widgets(self):
        """Create the GUI widgets."""
        self.monitors = self.list_monitors()  # Populate the monitors list
        
        if not self.monitors:
            tk.Label(self.root, text="No monitors detected.", fg="red").pack(pady=20)
            return

        # Create a frame for each monitor
        for monitor in self.monitors:
            monitor_frame = ttk.Frame(self.root, padding=10)
            monitor_frame.pack(fill='x', pady=5)

            # Monitor name label
            ttk.Label(monitor_frame, text=f"Monitor: {monitor['name']} (Index: {monitor['index']})").pack(anchor='w')

            # Current brightness label
            current_brightness_label = ttk.Label(monitor_frame, text=f"Current Brightness: {monitor['brightness']}%")
            current_brightness_label.pack(anchor='w')

            # Slider for brightness control
            brightness_slider = ttk.Scale(
                monitor_frame,
                from_=0,
                to=100,
                orient='horizontal',
                value=monitor['brightness']
            )
            brightness_slider.pack(fill='x', pady=5)

            # Store slider reference and current brightness label for later use
            monitor['slider'] = brightness_slider
            monitor['label'] = current_brightness_label

        # Text box for global brightness adjustment
        global_brightness_frame = ttk.Frame(self.root, padding=10)
        global_brightness_frame.pack(fill='x', pady=10)

        ttk.Label(global_brightness_frame, text="Set Global Brightness (0-100):").pack(side=tk.LEFT, padx=5)
        self.global_brightness_entry = ttk.Entry(global_brightness_frame, width=5)
        self.global_brightness_entry.pack(side=tk.LEFT, padx=5)

        # Set focus to the text box automatically
        self.global_brightness_entry.focus_set()

        # Bind the Enter key to apply the global brightness
        self.global_brightness_entry.bind("<Return>", self.apply_global_brightness_via_enter)

    def start_brightness_thread(self):
        """
        Start a background thread to handle brightness updates.
        """
        def brightness_worker():
            while self.running:
                for monitor in self.monitors:
                    slider_value = int(monitor['slider'].get())
                    current_time = time.time()
                    
                    # Update the brightness label immediately
                    monitor['label'].config(text=f"Current Brightness: {slider_value}%")
                    
                    # Check if the slider value has changed
                    if slider_value != self.previous_slider_values.get(monitor['index'], -1):
                        # Minimal throttling to avoid excessive calls
                        last_update = self.last_update_time.get(monitor['index'], 0)
                        if current_time - last_update < 0.01:  # Limit updates to every 50ms
                            continue
                        
                        # Update the last update time
                        self.last_update_time[monitor['index']] = current_time

                        try:
                            # Use the monitor's index as a fallback identifier if serial is None
                            display_identifier = monitor['serial'] or monitor['index']
                            
                            # Apply the brightness to the specific monitor using its identifier
                            sbc.set_brightness(slider_value, display=display_identifier)
                            monitor['brightness'] = slider_value
                            self.previous_slider_values[monitor['index']] = slider_value  # Update previous slider value
                            logging.info(f"Brightness set to {slider_value}% for monitor {monitor['name']} (Index: {monitor['index']})")
                        except Exception as e:
                            logging.error(f"Error setting brightness for monitor {monitor['name']} (Index: {monitor['index']}): {e}")
                
                time.sleep(0.01)  # Poll every 10ms for near-instant updates

        # Start the thread
        self.thread = threading.Thread(target=brightness_worker, daemon=True)
        self.thread.start()

    def apply_global_brightness_via_enter(self, event=None):
        """
        Set the brightness of all monitors to the value entered in the global brightness text box when Enter is pressed.
        """
        try:
            global_brightness = int(self.global_brightness_entry.get())
            if 0 <= global_brightness <= 100:
                for monitor in self.monitors:
                    display_identifier = monitor['serial'] or monitor['index']
                    sbc.set_brightness(global_brightness, display=display_identifier)
                    monitor['brightness'] = global_brightness
                    monitor['label'].config(text=f"Current Brightness: {global_brightness}%")
                    monitor['slider'].set(global_brightness)  # Update the slider position
                    logging.info(f"Brightness set to {global_brightness}% for monitor {monitor['name']} (Index: {monitor['index']})")
            else:
                logging.warning("Global brightness value must be between 0 and 100.")
        except ValueError:
            logging.warning("Invalid input. Please enter an integer between 0 and 100.")

    def close_program(self, event=None):
        """
        Close the program when the ESC key is pressed.
        """
        logging.info("Program closed via ESC key.")
        self.running = False  # Stop the background thread
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BrightnessControlApp(root)
    root.mainloop()
