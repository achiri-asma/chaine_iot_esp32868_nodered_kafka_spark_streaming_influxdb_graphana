
// Update these with values suitable for your network.

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#define wifi_ssid "Redmi"
#define wifi_password "abcd1234"
float hum = 0; 
// serveur mqtt
const char* mqtt_server = "192.168.25.244"; // TP1: broker on docker in raspberry pi
#define sensor_topic "sensor_temp" //Topic light

//les topic de souscription coté wemos sur le broker 
#define led_topic "home/led"
int led=D2;

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

void setup() {
pinMode(D2, OUTPUT); // intitialisation du pin pour activer la LED
Serial.begin(9600);

WiFi.begin(wifi_ssid, wifi_password);

while (WiFi.status() != WL_CONNECTED) {
delay(500);
Serial.print(".");
}

Serial.println("");
Serial.println("WiFi connected");
Serial.println("IP address: ");
Serial.println(WiFi.localIP());
client.setServer(mqtt_server, 8883);
}

void reconnect() {
// Loop until we're reconnected
while (!client.connected()) {
Serial.print("Attempting MQTT connection...");
String clientId = "SensorClient";
clientId += String(random(0xffff), HEX);
if (client.connect(clientId.c_str())) {
Serial.println("connected");
} else {
Serial.print("failed, rc=");
Serial.print(client.state());
Serial.println(" try again in 5 seconds");

delay(5000);
}
}
}



void loop() {
   hum +=0.5;
    Serial.println(hum);
delay(2000);
if (!client.connected()) {
reconnect();
}
client.loop();
client.publish(sensor_topic, String(hum).c_str(), true);

}
