
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from PIL import Image, ImageTk # For image handling

# Cable data (resistance per meter in Ohms/meter at 20°C)
CABLE_DATA = {
    "alarm": {
        "18 AWG": 0.0209,  # Approx. for copper
        "22 AWG": 0.0333,  # Approx. for copper
        "24 AWG": 0.0529,  # Approx. for copper
    },
    "network": {
        "Cat5e": 0.0938,  # Max DC loop resistance per meter for a pair
        "Cat6": 0.0700,   # Approx. DC loop resistance per meter for a pair
    }
}

# Temperature coefficient for copper (alpha at 20°C)
ALPHA_COPPER = 0.00393

def calculate_voltage_drop(length_m, current_a, cable_type, conductor_spec, num_cores=1, temp_c=20):
    """
    Calculates the voltage drop over a specified cable length.

    Args:
        length_m (float): Length of the cable in meters.
        current_a (float): Current flowing through the cable in Amperes.
        cable_type (str): Type of cable (\'alarm\' or \'network\').
        conductor_spec (str): Conductor specification (e.g., \'18 AWG\', \'Cat5e\').
        num_cores (int): Number of parallel cores used for current path (e.g., 2 for a single pair in network cable).
                         For alarm cables, this would typically be 1 per conductor, or 2 if using two conductors for a single path.
        temp_c (float): Operating temperature in Celsius.

    Returns:
        float: Calculated voltage drop in Volts.
    """
    if cable_type not in CABLE_DATA or conductor_spec not in CABLE_DATA[cable_type]:
        raise ValueError("Invalid cable type or conductor specification.")

    resistance_per_meter_at_20c = CABLE_DATA[cable_type][conductor_spec]

    # Adjust resistance for temperature
    resistance_per_meter_at_temp = resistance_per_meter_at_20c * (1 + ALPHA_COPPER * (temp_c - 20))

    # Total resistance of the cable run (round trip for DC circuits)
    # Assuming two conductors for the current path (e.g., positive and negative)
    # If num_cores > 1, it means parallel conductors are used, reducing overall resistance
    total_resistance = (resistance_per_meter_at_temp * length_m * 2) / num_cores

    voltage_drop = current_a * total_resistance
    return voltage_drop

def determine_cores_required(length_m, required_voltage, required_current, cable_type, conductor_spec, min_voltage_percent_drop=10, temp_c=20):
    """
    Determines the minimum number of cores required to maintain a specified voltage.

    Args:
        length_m (float): Length of the cable in meters.
        required_voltage (float): The voltage at the source.
        required_current (float): The current the load requires in Amperes.
        cable_type (str): Type of cable (\'alarm\' or \'network\').
        conductor_spec (str): Conductor specification (e.g., \'18 AWG\', \'Cat5e\').
        min_voltage_percent_drop (float): Maximum allowed voltage drop as a percentage of the required voltage.
        temp_c (float): Operating temperature in Celsius.

    Returns:
        int: Minimum number of cores required.
    """
    if cable_type not in CABLE_DATA or conductor_spec not in CABLE_DATA[cable_type]:
        raise ValueError("Invalid cable type or conductor specification.")

    resistance_per_meter_at_20c = CABLE_DATA[cable_type][conductor_spec]
    resistance_per_meter_at_temp = resistance_per_meter_at_20c * (1 + ALPHA_COPPER * (temp_c - 20))

    max_allowed_voltage_drop = required_voltage * (min_voltage_percent_drop / 100)
    
    if required_current == 0: # Handle division by zero if current is 0
        return 1 if max_allowed_voltage_drop >= 0 else float('inf')

    max_allowed_resistance = max_allowed_voltage_drop / required_current

    # Calculate the resistance of a single round-trip path for the given length
    single_path_resistance = resistance_per_meter_at_temp * length_m * 2

    # Determine how many parallel paths are needed to get below the max_allowed_resistance
    if max_allowed_resistance <= 0: # Avoid division by zero or negative resistance
        return float('inf') # Indicates an impossible scenario

    cores_needed = (single_path_resistance / max_allowed_resistance)
    return max(1, int(round(cores_needed)))


def save_presets(data, filename=".cable_calculator_presets.json"):
    """
    Saves the current input parameters as a preset.
    """
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save preset: {e}")

def load_presets(filename=".cable_calculator_presets.json"):
    """
    Loads presets from a file.
    """
    try:
        if not os.path.exists(filename):
            return {}
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid preset file. It might be corrupted.")
        return {}
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load preset: {e}")
        return {}

class CableCalculatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Cable Calculator")
        master.geometry("500x700") # Adjusted size for Tkinter

        # Developer details
        self.developer_label = ttk.Label(master, text="Developer: Jamie Johnson (TriggerHappyMe)", font=("Helvetica", 10))
        self.developer_label.pack(pady=(5,0))
        self.email_label = ttk.Label(master, text="Email: support@intercomserviceslondon.co.uk", font=("Helvetica", 10))
        self.email_label.pack(pady=(0,10))

        # Logo
        try:
            # Ensure the path is correct relative to where the script is run
            script_dir = os.path.dirname(__file__)
            logo_path = os.path.join(script_dir, "INTERCOMMainLogo(1).png")
            self.logo_image = Image.open(logo_path)
            self.logo_image = self.logo_image.resize((200, 100), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = tk.Label(master, image=self.logo_photo)
            self.logo_label.pack(pady=10)
        except FileNotFoundError:
            messagebox.showwarning("Warning", "Logo image not found. Please ensure INTERCOMMainLogo(1).png is in the same directory as the script.")
        except Exception as e:
            messagebox.showwarning("Warning", f"Error loading logo: {e}")

        # Input Frame
        input_frame = ttk.LabelFrame(master, text="Input Parameters")
        input_frame.pack(padx=10, pady=10, fill="x")

        self.create_input_widgets(input_frame)

        # Calculation Mode
        mode_frame = ttk.Frame(master)
        mode_frame.pack(pady=5)
        self.forward_mode = tk.BooleanVar(value=True)
        ttk.Radiobutton(mode_frame, text="Forward Calculation", variable=self.forward_mode, value=True).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="Reverse Calculation", variable=self.forward_mode, value=False).pack(side="left", padx=5)

        # Buttons
        button_frame = ttk.Frame(master)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Calculate", command=self.calculate).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset", command=self.reset_inputs).pack(side="left", padx=5)

        # Results Frame
        results_frame = ttk.LabelFrame(master, text="Results")
        results_frame.pack(padx=10, pady=10, fill="x")

        self.create_results_widgets(results_frame)

        # Menu Bar
        self.menubar = tk.Menu(master)
        master.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Preset", command=self.save_current_preset)
        file_menu.add_command(label="Load Preset", command=self.load_selected_preset)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=master.quit)

        # Initial update of conductor spec dropdown
        self.update_conductor_specs()

    def create_input_widgets(self, parent_frame):
        self.entries = {}
        labels = ["Cable Type:", "Conductor Spec:", "Length (m):", "Source Voltage (V):", "Required Current (A):", "Number of Cores:", "Temperature (°C):"]
        keys = ["cable_type", "conductor_spec", "length", "voltage", "current", "num_cores", "temp"]
        default_values = {"num_cores": "1", "temp": "20"}

        for i, label_text in enumerate(labels):
            row = ttk.Frame(parent_frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label_text, width=18).pack(side="left")

            if label_text == "Cable Type:":
                self.cable_type_var = tk.StringVar(value=list(CABLE_DATA.keys())[0])
                combo = ttk.Combobox(row, textvariable=self.cable_type_var, values=list(CABLE_DATA.keys()), state="readonly")
                combo.pack(side="right", expand=True, fill="x")
                combo.bind("<<ComboboxSelected>>", self.update_conductor_specs)
                self.entries[keys[i]] = combo
            elif label_text == "Conductor Spec:":
                self.conductor_spec_var = tk.StringVar()
                combo = ttk.Combobox(row, textvariable=self.conductor_spec_var, values=[], state="readonly")
                combo.pack(side="right", expand=True, fill="x")
                self.entries[keys[i]] = combo
            else:
                entry_var = tk.StringVar(value=default_values.get(keys[i], ""))
                entry = ttk.Entry(row, textvariable=entry_var)
                entry.pack(side="right", expand=True, fill="x")
                self.entries[keys[i]] = entry_var

    def create_results_widgets(self, parent_frame):
        self.results_labels = {}
        results_info = [
            ("Voltage Drop (V):", "vd_result"),
            ("Voltage Drop (%):", "vd_percent"),
            ("Current Drop (A):", "cd_result"),
            ("Cores Required:", "cores_required"),
            ("Wiring Recommendation:", "wiring_rec")
        ]

        for label_text, key in results_info:
            row = ttk.Frame(parent_frame)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label_text, width=20).pack(side="left")
            result_var = tk.StringVar()
            ttk.Label(row, textvariable=result_var).pack(side="right", expand=True, fill="x")
            self.results_labels[key] = result_var
        
        self.results_labels["cd_result"].set("N/A (Current is assumed constant for voltage drop)")

    def update_conductor_specs(self, event=None):
        selected_cable_type = self.cable_type_var.get()
        specs = list(CABLE_DATA.get(selected_cable_type, {}).keys())
        self.entries["conductor_spec"]["values"] = specs
        if specs:
            self.entries["conductor_spec"].set(specs[0])
        else:
            self.entries["conductor_spec"].set("")

    def get_input_values(self):
        values = {}
        for key, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                values[key] = widget.get()
            else:
                values[key] = widget.get()
        return values

    def calculate(self):
        try:
            input_values = self.get_input_values()
            length = float(input_values["length"])
            voltage = float(input_values["voltage"])
            current = float(input_values["current"])
            num_cores = int(input_values["num_cores"])
            temp = float(input_values["temp"])
            cable_type = input_values["cable_type"]
            conductor_spec = input_values["conductor_spec"]

            if self.forward_mode.get():
                # Forward Calculation
                voltage_drop = calculate_voltage_drop(length, current, cable_type, conductor_spec, num_cores, temp)
                voltage_drop_percent = (voltage_drop / voltage) * 100 if voltage != 0 else 0

                self.results_labels["vd_result"].set(f"{voltage_drop:.4f} V")
                self.results_labels["vd_percent"].set(f"{voltage_drop_percent:.2f} %")
                self.results_labels["cores_required"].set("N/A")
                self.results_labels["wiring_rec"].set("N/A")

            else:
                # Reverse Calculation
                min_voltage_percent_drop = 10  # Default for now, could be an input field

                cores_needed = determine_cores_required(length, voltage, current, cable_type, conductor_spec, min_voltage_percent_drop, temp)

                self.results_labels["vd_result"].set("N/A")
                self.results_labels["vd_percent"].set("N/A")
                self.results_labels["cores_required"].set(f"{cores_needed}")
                if cores_needed == 1:
                    self.results_labels["wiring_rec"].set(f"Use 1 core of {conductor_spec}")
                elif cores_needed > 1 and cores_needed != float("inf"):
                    self.results_labels["wiring_rec"].set(f"Use {cores_needed} parallel cores of {conductor_spec}")
                elif cores_needed == float("inf"):
                    self.results_labels["wiring_rec"].set("Impossible to meet requirements with this cable.")

            self.results_labels["cd_result"].set("N/A (Current is assumed constant for voltage drop)")

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}. Please enter numeric values for Length, Voltage, Current, Number of Cores, and Temperature.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def reset_inputs(self):
        for key, widget in self.entries.items():
            if key == "cable_type":
                widget.set(list(CABLE_DATA.keys())[0])
                self.update_conductor_specs()
            elif key == "num_cores":
                widget.set("1")
            elif key == "temp":
                widget.set("20")
            elif isinstance(widget, tk.StringVar):
                widget.set("")
        self.forward_mode.set(True)
        for key in self.results_labels:
            if key == "cd_result":
                self.results_labels[key].set("N/A (Current is assumed constant for voltage drop)")
            else:
                self.results_labels[key].set("")

    def save_current_preset(self):
        input_values = self.get_input_values()
        preset_name = filedialog.askstring("Save Preset", "Enter preset name:")
        if preset_name:
            presets = load_presets()
            presets[preset_name] = input_values
            presets[preset_name]["forward_mode"] = self.forward_mode.get()
            save_presets(presets)
            messagebox.showinfo("Preset Saved", f"Preset \'{preset_name}\' saved successfully.")

    def load_selected_preset(self):
        presets = load_presets()
        if not presets:
            messagebox.showinfo("Load Preset", "No presets found.")
            return

        preset_names = list(presets.keys())
        selected_preset_name = filedialog.askstring("Load Preset", "Select preset to load:", initialvalue=preset_names[0])

        if selected_preset_name in presets:
            loaded_preset = presets[selected_preset_name]
            for key, value in loaded_preset.items():
                if key == "cable_type":
                    self.entries[key].set(value)
                    self.update_conductor_specs() # Update conductor specs after setting cable type
                elif key == "conductor_spec":
                    self.entries[key].set(value)
                elif key == "forward_mode":
                    self.forward_mode.set(value)
                elif key in self.entries and isinstance(self.entries[key], tk.StringVar):
                    self.entries[key].set(value)
            messagebox.showinfo("Preset Loaded", f"Preset \'{selected_preset_name}\' loaded successfully.")
        elif selected_preset_name is not None: # User didn't cancel
            messagebox.showwarning("Preset Not Found", f"Preset \'{selected_preset_name}\' not found.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CableCalculatorGUI(root)
    root.mainloop()


