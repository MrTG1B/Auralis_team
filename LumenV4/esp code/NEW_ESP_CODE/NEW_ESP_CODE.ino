#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <WiFiClientSecure.h>  // Secure client for HTTPS

const char* ssid = "Tirthankar";
const char* password = "Dasgupta2004";
const char* serverHost = "https://6883cjlh-8080.inc1.devtunnels.ms";
WebServer server(80);

const int pin = 15, led_pin = 33, irp = 34, ldr = 35, cu_sen = 32, output_pin = 2;
const int br = 5000; // PWM frequency for LED (in Hz)
const int b_per=60;

#define ADC_BITS 10             
#define ADC_VREF 1100           

#define LED_MIN_BRIGHTNESS 0    
#define LED_MAX_BRIGHTNESS 255 

const float lthold = 50, ccc = 5.015, ct = 0.16;
float energy = 0.0, currentData = 0.0;

String deviceID;
QueueHandle_t httpQueue;

struct HttpRequest {
  String endpoint;
  String payload;
};

void sendDataTask(void* parameter) {
  WiFiClientSecure client;
  HTTPClient http;
  client.setInsecure();  // Disable SSL certificate validation

  while (true) {
    if (WiFi.status() == WL_CONNECTED) {
      String dataEndpoint = "/data";
      String dataPayload = "{\"deviceID\":\"" + deviceID + "\",\"current\":" + String(csread()) + ",\"energy\":" + String(energy) + "}";

      String irEndpoint = "/ir";
      int irState = !digitalRead(irp);
      String irPayload = "{\"deviceID\":\"" + deviceID + "\",\"irState\":" + String(irState) + "}";

      Serial.println("Sending HTTP Request:");
      Serial.println("IR Payload: " + irPayload);
      Serial.println("Data Payload: " + dataPayload);

      http.begin(client, serverHost + dataEndpoint);
      http.addHeader("Content-Type", "application/json");
      int httpResponseCode = http.POST(dataPayload);
      Serial.println("HTTP Response Code: " + String(httpResponseCode));
      if (httpResponseCode > 0) Serial.println("Response: " + http.getString());
      http.end();

      http.begin(client, serverHost + irEndpoint);
      http.addHeader("Content-Type", "application/json");
      httpResponseCode = http.POST(irPayload);
      Serial.println("HTTP Response Code: " + String(httpResponseCode));
      if (httpResponseCode > 0) Serial.println("Response: " + http.getString());
      http.end();
    } else {
      Serial.println("WiFi Disconnected! Cannot send data.");
    }

    vTaskDelay(5000 / portTICK_PERIOD_MS);
  }
}

void sendDataAsync(const char* endpoint, const String& payload) {
  HttpRequest request = {endpoint, payload};
  xQueueSend(httpQueue, &request, portMAX_DELAY);
}

int checkFault() {
  digitalWrite(led_pin, HIGH);
  int p = digitalRead(pin);
  float c = csread();
  int result = (p == HIGH && c > ct) || (p == HIGH && c < ct) ? 1 : 0;
  return result;
}

void setup() {
  Serial.begin(115200);
  pinMode(ldr,INPUT);
  pinMode(irp, INPUT);
  pinMode(pin, INPUT);
  pinMode(cu_sen, INPUT);
  pinMode(output_pin, OUTPUT);
  pinMode(led_pin, OUTPUT); // Set LED pin as output

  Serial.println("\nConnecting to WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);
  WiFi.setSleep(false);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  deviceID = WiFi.localIP().toString();
  Serial.println("Device ID (IP Address): " + deviceID);

  digitalWrite(output_pin, HIGH);

  server.on("/led/on", HTTP_GET, []() {
    Serial.println("Received request: /led/on");
    lon(1);
    server.send(200, "text/plain", "light on");
  });

  server.on("/fault_scan", HTTP_GET, []() {
    String status = String(checkFault());
    server.send(200, "text/plain", status);
  });

  server.begin();
  Serial.println("ESP32 server is ready");

  httpQueue = xQueueCreate(10, sizeof(HttpRequest));

  xTaskCreatePinnedToCore(sendDataTask, "HTTP Task", 8192, NULL, 1, NULL, 0);
}

float brightnessf() {
  int ldrValue = analogRead(ldr);
  int brightness = map(ldrValue, 0, (1 << ADC_BITS) - 1, LED_MIN_BRIGHTNESS, LED_MAX_BRIGHTNESS);
  return constrain(brightness < 10 ? 0 : brightness, 0, 255);
  // return brightness;
}

float csread() {
  float voltage = analogRead(cu_sen) * ccc / 4095.0;
  float current = 0.0;
  for (int i = 0; i < 512; i++) current += (voltage - 2.5) / 0.100;
  current /= 512;
  return current <= 0.06 ? 0.0 : current / 100.0;
}

void lon(int i) {
  if (i == 1) {
    analogWrite(led_pin, brightnessf()); 
    delay(1000);
  }
  analogWrite(led_pin, round((brightnessf() * b_per) / 100.0));
}

void loop() {
  server.handleClient();
  int irState = !digitalRead(irp);
  // Serial.println(analogRead(ldr));
  // Serial.println(brightnessf());
  if (irState == HIGH) {
    analogWrite(led_pin, brightnessf());
  } else {
    analogWrite(led_pin, round((brightnessf() * b_per) / 100.0));
  }

  energy += csread() * 12 / 3600000.0;
  delay(50);
}