// Define the pin for the LED
const int ledPin = 2; // Change according to your setup

// Threshold value for EEG signal
const int threshold = 300; // Adjust this threshold based on your EEG data

// Variables to store EEG data
int eegSignal = 0;

void setup() {
  // Initialize Serial communication for debugging
  Serial.begin(115200);

  // Initialize Serial communication with Neuphony EXG Synapse
  Serial2.begin(9600, SERIAL_8N1, 16, 17); // Change RX/TX pins as needed

  // Initialize the LED pin as an output
  pinMode(ledPin, OUTPUT);

  // Turn off LED initially
  digitalWrite(ledPin, LOW);
}

void loop() {
  // Check if data is available from Neuphony EXG Synapse
  if (Serial2.available() > 0) {
    // Read EEG data from Neuphony
    eegSignal = Serial2.parseInt(); // Assuming EEG data is sent as integers

    // Debugging: print the EEG signal value to the serial monitor
    Serial.print("EEG Signal: ");
    Serial.println(eegSignal);

    // Check if the EEG signal crosses the threshold
    if (eegSignal > threshold) {
      // Turn on the LED
      digitalWrite(ledPin, HIGH);
    } else {
      // Turn off the LED
      digitalWrite(ledPin, LOW);
    }
  }

  // Small delay to avoid flooding the serial output
  delay(100);
}
