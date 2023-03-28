import sys
import screen_brightness_control as sbc

def set_external_brightness(value):
    monitors = sbc.list_monitors_info()

    for monitor in monitors:
        if monitor['name'] != 'Laptop screen':
            try:
                sbc.set_brightness(value, display=monitor['serial'])
                print(f"Brightness set to {value} for monitor {monitor['name']}")
            except Exception as e:
                print(f"Error setting brightness for monitor {monitor['name']}: {e}")

if __name__ == "__main__":
    try:
        brightness_value = int(input("Enter brightness value (0-100): "))
        if 0 <= brightness_value <= 100:
            set_external_brightness(brightness_value)
        else:
            print("Error: Brightness value must be between 0 and 100.")
    except ValueError:
        print("Error: Brightness value must be an integer.")
