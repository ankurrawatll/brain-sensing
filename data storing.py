import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, lfilter
import serial
import time
import serial.tools.list_ports
import os

print(os.getcwd())


# Check available ports
ports = list(serial.tools.list_ports.comports())
print("Available ports:")
for p in ports:
    print(p)

# Set up serial connection (adjust the COM port and baud rate as needed)
ser = serial.Serial('COM6', 115200)  
time.sleep(2)  # Allow time for the serial connection to initialize

# Define bandpass filters for different brainwave bands
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Initialize variables
eeg_data = []
data_storage = []  # To store the processed data
sampling_rate = 100  # Adjust based on your Arduino delay (10ms delay -> 100Hz sampling rate)
alpha_threshold = 50  # Adjust this threshold based on your data

try:
    print("Reading EEG data...")
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    eeg_value = float(line)
                    eeg_data.append(eeg_value)
                    if len(eeg_data) > sampling_rate * 10:  # Limit to last 10 seconds of data
                        eeg_data.pop(0)
                    
                    # Convert data to numpy array for processing
                    eeg_signal = np.array(eeg_data)

                    # Apply bandpass filters to extract different brainwave bands
                    delta = bandpass_filter(eeg_signal, 0.5, 4, sampling_rate)
                    theta = bandpass_filter(eeg_signal, 4, 8, sampling_rate)
                    alpha = bandpass_filter(eeg_signal, 8, 13, sampling_rate)
                    beta = bandpass_filter(eeg_signal, 13, 30, sampling_rate)
                    gamma = bandpass_filter(eeg_signal, 30, 45, sampling_rate)

                    # Check alpha band average amplitude against threshold
                    if np.mean(alpha) > alpha_threshold:
                        ser.write(b'H')  # Send command to turn the light on
                    else:
                        ser.write(b'L')  # Send command to turn the light off

                    # Store data
                    data_storage.append({
                        'eeg_value': eeg_value,
                        'delta': np.mean(delta),
                        'theta': np.mean(theta),
                        'alpha': np.mean(alpha),
                        'beta': np.mean(beta),
                        'gamma': np.mean(gamma),
                        'timestamp': time.time()
                    })

                    # Plot the data in real-time
                    plt.clf()
                    plt.subplot(5, 1, 1)
                    plt.plot(delta, label='Delta (0.5-4 Hz)', color='b')
                    plt.title('Delta (0.5-4 Hz)')
                    plt.xlabel('Time (s)')
                    plt.ylabel('Amplitude')
                    plt.grid(True)
                    plt.legend()

                    plt.subplot(5, 1, 2)
                    plt.plot(theta, label='Theta (4-8 Hz)', color='g')
                    plt.title('Theta (4-8 Hz)')
                    plt.xlabel('Time (s)')
                    plt.ylabel('Amplitude')
                    plt.grid(True)
                    plt.legend()

                    plt.subplot(5, 1, 3)
                    plt.plot(alpha, label='Alpha (8-13 Hz)', color='r')
                    plt.title('Alpha (8-13 Hz)')
                    plt.xlabel('Time (s)')
                    plt.ylabel('Amplitude')
                    plt.grid(True)
                    plt.legend()

                    plt.subplot(5, 1, 4)
                    plt.plot(beta, label='Beta (13-30 Hz)', color='c')
                    plt.title('Beta (13-30 Hz)')
                    plt.xlabel('Time (s)')
                    plt.ylabel('Amplitude')
                    plt.grid(True)
                    plt.legend()

                    plt.subplot(5, 1, 5)
                    plt.plot(gamma, label='Gamma (30-45 Hz)', color='m')
                    plt.title('Gamma (30-45 Hz)')
                    plt.xlabel('Time (s)')
                    plt.ylabel('Amplitude')
                    plt.grid(True)
                    plt.legend()

                    plt.tight_layout()
                    plt.pause(0.05)  # Adjust the pause time for smoother updates
                except ValueError:
                    print(f"Invalid value received: {line}")

except KeyboardInterrupt:
    print("Exiting...")
    ser.close()

    # Save data to CSV
    df = pd.DataFrame(data_storage)
    df.to_csv('eeg_data_processed.csv', index=False)
    print("Data saved to eeg_data_processed.csv")

    plt.close()

plt.show()
