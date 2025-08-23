#include <WiFi.h>
#include <WebServer.h>
// #include <ledc.h>

const char* ssid = "Tirthankar";
const char* password = "Dasgupta2004";
WebServer server(80);

const int pin = 15, led_pin = 33, irp = 34, ldr = 35, cu_sen = 32, output_pin = 2;
const int br = 5000; // PWM frequency for LED (in Hz)
const int b_per=60;
const int led_channel = 0; // LEDC channel for LED
const int led_resolution = 8; // LEDC resolution (8-bit)

const float lthold = 50, ccc = 5.015, ct = 0.16;
float energy = 0.0;

void setup() {
  Serial.begin(115200);
  pinMode(irp, INPUT);
  pinMode(pin, INPUT);
  pinMode(ldr, INPUT);
  pinMode(cu_sen, INPUT);
  pinMode(led_pin, OUTPUT);
  pinMode(output_pin, OUTPUT);

  ledcSetup(led_channel, br, led_resolution);
  ledcAttachPin(led_pin, led_channel);

  Serial.println("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());

  digitalWrite(output_pin, HIGH); // Set pin 2 to HIGH after connecting to WiFi

  server.on("/led/on", HTTP_GET, []() {
    lon(1);
    server.send(200, "text/plain", "light on");
  });

  server.on("/en", HTTP_GET, []() {
    server.send(200, "text/plain", String(energy));
    energy = 0.0;
  });

  server.on("/ir", HTTP_GET, []() {
    server.send(200, "text/plain", String(digitalRead(irp) == LOW ? "1" : "0"));
  });

  server.on("/cs", HTTP_GET, []() {
    server.send(200, "text/plain", String(csread()));
  });

  server.on("/fss", HTTP_GET, []() {
    digitalWrite(led_pin, HIGH);
    int p = digitalRead(pin);
    float c = csread();
    String r = (p == HIGH && c > ct) || (p == LOW && c < ct) ? "1" : "0";
    ledcWrite(led_channel, round((brightnessf() * br) / 100.0)); // Adjust PWM duty cycle based on brightness
    server.send(200, "text/plain", r);
  });

  server.begin();
  Serial.println("ESP32 server is ready");
}

int brightnessf() {
  int ldrr = analogRead(ldr);
  int brightness = map(ldrr, 0, 4095, 0, 255); // Adjusted for ESP32's 12-bit ADC
  return constrain(brightness < lthold ? 0 : brightness, 0, 255);
}

float csread() {
  float voltage = analogRead(cu_sen) * ccc / 4095.0;
  float current = 0.0;
  for (int i = 0; i < 512; i++)
    current += (voltage - 2.5) / 0.100;
  current /= 512;
  return current <= 0.06 ? 0.0 : current / 100.0;
}

void lon(int i) {
  if (i == 1) {
    ledcWrite(led_channel, brightnessf());
    delay(1000); // Delay is necessary if you want to keep the light on for a specific period
  }
  ledcWrite(led_channel, round((brightnessf() * b_per) / 100.0));
}

void loop() {
  int irState = digitalRead(irp);
  // int ldrr = analogRead(ldr);
  // int brightness = map(ldrr, 0, 1023, 0, 255);
  if ((irState == LOW)) {
    ledcWrite(led_channel, brightnessf());
  } else {
    ledcWrite(led_channel, round((brightnessf() * b_per) / 100.0));
  }
  energy += csread() * 12 / 3600000.0;
  
  server.handleClient(); // Handle incoming client requests asynchronously
}
