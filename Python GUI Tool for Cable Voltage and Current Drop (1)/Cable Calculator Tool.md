# Cable Calculator Tool

## Overview
This Python GUI application calculates voltage/current drop and determines required conductors for low-voltage alarm and network data cable installations. It supports both forward and reverse calculations.

## Features
- **Forward Calculations**: Calculate voltage drop for a given cable type, conductor size, number of cores, initial voltage, and current.
- **Reverse Calculations**: Determine the minimum number of cores needed to maintain a specified minimum voltage and deliver required current over a distance.
- **Customizable Parameters**: Includes standard values for resistivity and temperature coefficients, with options for customization.
- **User-Friendly GUI**: Built with Tkinter (included with Python) for easy input and clear display of results.
- **Save/Load Presets**: Save your calculation parameters as presets for future use.
- **Free and Open Source**: Uses only free, open-source libraries that come with Python.

## Installation
1. **Prerequisites**:
   - Python 3.10+ installed on your system.

2. **Download the Application**:
   Download the `cable_calculator.py`, `run.bat`, `run.sh` and `INTERCOMMainLogo(1).png` files to the same directory on your local machine.

## Usage
1. **Run the Application**:
   - **Windows**: Double-click `run.bat`.
   - **Linux/macOS**: Open a terminal, navigate to the directory where you saved the files, and run `chmod +x run.sh` followed by `./run.sh`.

   The script will automatically check for and install necessary Python dependencies (PySimpleGUI, tkinter) if they are not found, and then launch the GUI.

2. **Input Parameters**:
   - Select the **Cable Type** (Alarm or Network).
   - Select the **Conductor Spec** (e.g., 18 AWG, Cat5e).
   - Enter the **Length (m)**, **Source Voltage (V)**, **Required Current (A)**, **Number of Cores**, and **Temperature (°C)**.

3. **Choose Calculation Mode**:
   - Select **Forward Calculation** to calculate voltage drop.
   - Select **Reverse Calculation** to determine the number of cores required.

4. **Calculate**: Click the `Calculate` button to see the results.

5. **Reset**: Click the `Reset` button to clear all input fields.

6. **Save/Load Presets**:
   - Use `File > Save Preset` to save your current input parameters.
   - Use `File > Load Preset` to load previously saved parameters.

7. **Change Theme**:
   - Use `Options > Theme` to select a different visual theme.

## Developer Details
- **Name**: Jamie Johnson (TriggerHappyMe)
- **Email**: support@intercomserviceslondon.co.uk

## Disclaimer
This tool provides estimations based on standard electrical formulas and general cable specifications. Always consult with a qualified electrician or engineer for critical installations and verify calculations with actual cable data sheets.

