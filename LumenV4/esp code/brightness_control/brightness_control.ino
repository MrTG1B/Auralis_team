#define LED_PIN 33    // GPIO 12 for LED control
#define LDR_PIN 35   // GPIO 32 for LDR input

#define ADC_BITS 10             
#define ADC_VREF 1100           

#define LED_MIN_BRIGHTNESS 0    
#define LED_MAX_BRIGHTNESS 255  

void setup() {
    Serial.begin(115200);
    
    pinMode(LDR_PIN, INPUT);
    pinMode(LED_PIN, OUTPUT);
}

void loop() {
    int ldrValue = analogRead(LDR_PIN);
    
    // Convert LDR value to brightness level
    int brightness = map(ldrValue, 0, (1 << ADC_BITS) - 1, LED_MIN_BRIGHTNESS, LED_MAX_BRIGHTNESS);
    
    // Set LED brightness
    analogWrite(LED_PIN, brightness);

    Serial.print("LDR Value: ");
    Serial.print(ldrValue);
    Serial.print(" -> LED Brightness: ");
    Serial.println(brightness);

    delay(1000);
}
