#include <WiFi.h>
#include <HTTPClient.h>

// Config WiFi
const char* ssid = "TUO_WIFI";
const char* password = "TUA_PASSWORD";

// Indirizzo del server Django
String serverName = "http://192.168.1.100:8000/quiz/buzz/";  // Cambia IP!

// Pin pulsanti
#define BTN1 12
#define BTN2 13
#define BTN3 14
#define BTN4 27

void setup() {
  Serial.begin(115200);

  pinMode(BTN1, INPUT_PULLUP);
  pinMode(BTN2, INPUT_PULLUP);
  pinMode(BTN3, INPUT_PULLUP);
  pinMode(BTN4, INPUT_PULLUP);

  WiFi.begin(ssid, password);
  Serial.print("Connessione a WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnesso a WiFi!");
}

void loop() {
  if (digitalRead(BTN1) == LOW) {
    sendBuzz("Team 1");
    delay(500); // debounce
  }
  if (digitalRead(BTN2) == LOW) {
    sendBuzz("Team 2");
    delay(500);
  }
  if (digitalRead(BTN3) == LOW) {
    sendBuzz("Team 3");
    delay(500);
  }
  if (digitalRead(BTN4) == LOW) {
    sendBuzz("Team 4");
    delay(500);
  }
}

void sendBuzz(String team) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    String postData = "player=" + team;
    int httpResponseCode = http.POST(postData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Risposta server: " + response);
    } else {
      Serial.print("Errore richiesta: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi non connesso");
  }
}
