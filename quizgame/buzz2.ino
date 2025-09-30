#include <WiFi.h>
#include <HTTPClient.h>

// WiFi
const char* ssid = "TUO_WIFI";
const char* password = "TUA_PASSWORD";

// Server Django
String serverName = "http://192.168.1.100:8000/quiz/buzz/";  // Cambia IP!

// Pin pulsante
#define BTN 12       // Cambiare per ogni ESP32

// Nome del team
String teamName = "Team 1";  // Cambiare per ciascun ESP32

void setup() {
  Serial.begin(115200);
  pinMode(BTN, INPUT_PULLUP);

  // Connetti WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connessione a WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnesso a WiFi!");
}

void loop() {
  if (digitalRead(BTN) == LOW) {
    sendBuzz();
    delay(500); // debounce
  }
}

void sendBuzz() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    int httpResponseCode = http.POST("player=" + teamName);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(teamName + " → " + response);
    } else {
      Serial.print("Errore richiesta: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi non connesso");
  }
}
