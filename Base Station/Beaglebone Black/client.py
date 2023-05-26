import serial
import paho.mqtt.client as mqtt

import Adafruit_BBIO.UART as UART

# UART configuration
uart_device = '/dev/ttyO1'  # Replace with your UART device
uart_baudrate = 9600  # Replace with the appropriate baudrate

# MQTT configuration
mqtt_broker = 'localhost'  # Replace with your MQTT broker IP or hostname
mqtt_port = 1883
mqtt_topic = 'SIT730/agrisense'

# Connect to the MQTT broker
client = mqtt.Client("beagleboneClient")

client.username_pw_set("username_on_broker", "password_on_broker")

def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    # Subscribe to necessary topics if required
    # client.subscribe('SIT730/agrisense')

def on_publish(client, userdata, mid):
    print('Message published')

client.on_connect = on_connect
client.on_publish = on_publish

client.connect(mqtt_broker)
client.loop_start()



# Open the UART device
#uart = serial.Serial(uart_device, uart_baudrate)

UART.setup("UART1")

uart = serial.Serial(port='/dev/ttyO1',baudrate=9600)
uart.close()

uart.open()



try:
    while True:
        if uart.in_waiting>0:
            uart_data = uart.readline()
            print(uart_data)


            # Publish the data to MQTT
            client.publish(mqtt_topic, uart_data)

except:
    print("Error")

finally:
    # Cleanup
    client.loop_stop()
    client.disconnect()
    uart.close()
