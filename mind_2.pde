import processing.serial.*;

Serial myPort;
String eegValue = "0";
int[] eegValues = new int[60];  // Store the last 60 values for the graph

void setup() {
  size(800, 600);
  String portName = Serial.list()[0]; // Adjust this index based on your port
  myPort = new Serial(this, portName, 115200);
  myPort.bufferUntil('\n');
}

void draw() {
  background(255);
  fill(0);
  textSize(32);
  text("EEG Value: " + eegValue, 50, 50);

  // Draw the graph
  stroke(0);
  noFill();
  beginShape();
  for (int i = 0; i < eegValues.length; i++) {
    float x = map(i, 0, eegValues.length - 1, 50, width - 50);
    float y = map(eegValues[i], 0, 1023, height - 50, 100);
    vertex(x, y);
  }
  endShape();
}

void serialEvent(Serial myPort) {
  String inString = myPort.readStringUntil('\n');
  if (inString != null) {
    inString = trim(inString);
    eegValue = inString;
    int val = int(eegValue);
    // Shift all values to the left
    for (int i = 0; i < eegValues.length - 1; i++) {
      eegValues[i] = eegValues[i + 1];
    }
    // Add the new value to the end
    eegValues[eegValues.length - 1] = val;
  }
}
