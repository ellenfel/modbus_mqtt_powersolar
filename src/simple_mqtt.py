import paho.mqtt.client as mqtt

# MQTT broker details
broker = "35.169.3.101"
port = 1884
topic = "test/topic"
message = "Hi, MQTT!"

# Create a new MQTT client instance
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(broker, port, keepalive=60)

# Publish the message with QoS 1
client.publish(topic, message, qos=1)

# Disconnect from the broker
client.disconnect()

print("Message published to topic:", topic)
