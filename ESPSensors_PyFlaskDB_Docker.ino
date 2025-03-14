/***************************************************************************************************************
****************************    Author  : Ehab Magdy Abdullah                      *****************************
****************************    Linkedin: https://www.linkedin.com/in/ehabmagdyy/  *****************************
****************************    Youtube : https://www.youtube.com/@EhabMagdyy      *****************************
****************************************************************************************************************/

#ifdef ESP32
#include <WiFi.h>
#include <HTTPClient.h>
#elif ESP8266
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#endif

#define ssid         "ssid"
#define password     "password"
#define serverUrl    "http://<FlaskHostIpAddress>:5000/sensor"  // Update with Flask server IP

#define POT_PIN      32   // potentiometer pin number
uint16_t potVal = 0;

void setup()
{
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected!");
}

void loop()
{
    if (WiFi.status() == WL_CONNECTED)
    {
        potVal = analogRead(POT_PIN);
        Serial.println(potVal);

        HTTPClient http;
    #ifdef ESP32
        http.begin(serverUrl);
    #elif ESP8266
        WiFiClientSecure client;
        client.setInsecure();
        http.begin(client, serverUrl);
    #endif

        http.addHeader("Content-Type", "application/json");
        // prepare potentiometer data for POST request
        String jsonPayload = "{\"sensor_id\": \"potentiometer\", \"value\": " + String(potVal) + "}";
        int httpResponseCode = http.POST(jsonPayload);   // send data to Flask web page

        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);

        http.end();
    }
    else { WiFi.reconnect(); }
    delay(5000);
}
