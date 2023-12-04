import sys
import screen_brightness_control as sbc

def set_external_brightness(value):
    monitors = sbc.list_monitors_info()

    for monitor in monitors:
        try:
            current_brightness = sbc.get_brightness(display=monitor['serial'])
            print(f"Current brightness for monitor {monitor['name']}: {current_brightness}%")
            sbc.set_brightness(value, display=monitor['serial'])
            print(f"Brightness set to {value}% for monitor {monitor['name']}")
        except Exception as e:
            print(f"Error setting brightness for monitor {monitor['name']}: {e}")

if __name__ == "__main__":
    try:
        monitors = sbc.list_monitors_info()
        for monitor in monitors:
            current_brightness = sbc.get_brightness(display=monitor['serial'])
            print(f"Current brightness for monitor {monitor['name']}: {current_brightness}%")
        
        brightness_value = int(input("Enter new brightness value (0-100): "))
        
        if 0 <= brightness_value <= 100:
            set_external_brightness(brightness_value)
        else:
            print("Error: Brightness value must be between 0 and 100.")
    except ValueError:
        print("Error: Brightness value must be an integer.")
