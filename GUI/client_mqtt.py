
import time
import paho.mqtt.client as mqtt

_MQTT_BROKER_ADDRESS = "192.168.1.221"

"""
BUilds a python dictionary from the components of the encoded payload.  This needs to be exactly right as per spec
on the Sensor node end.
"""

def build_dict(message):


    # "sensor_id": "1",
    # "sensor_type": "mmRadar",
    # "sensor_lat": "-35.4260349",
    # "sensor_long": "149.2366052",
    # "properties": {
    #   "timestamp": "1682768743",
    # First char is type
    # type 1 : sensorid 2 : sensor_type (accel or person ) 6
    # lat -35.4260349 12 : long 12
    # timestamp 10
    # score 2

    if message[0] == '9':
        my_type = "heartbeat"

        properties = {"timestamp": message[33:43]}
        payload = {"sensor_id": message[1:3],
                   "sensor_type": message[3:9],
                   "sensor_lat": message[9:21],
                   "sensor_long": message[21:33],
                   "properties" : properties


                   }
    else:
        my_type = "event"

        properties = {"timestamp": message[33:43],
                      "confidence": message[43:45]}
        payload = {"sensor_id": message[1:3],
                   "sensor_type": message[3:9],
                   "sensor_lat": message[9:21],
                   "sensor_long": message[21:33],
                   "properties": properties

                   }



    return my_type, payload


class ClientMqtt:
    def __init__(self, database_accessor = None):

        self.database_accessor = database_accessor
        self.mqtt_client = None


    def connectMQTT(self):

        client_id = f"agrisense_gui_{time.time()}"

        self.mqtt_client = mqtt.Client(client_id=client_id, clean_session=True, userdata=None, protocol=mqtt.MQTTv311,
                                           transport="tcp")


        self.mqtt_client.connect(_MQTT_BROKER_ADDRESS)
        print("Connecting..")
        self.mqtt_client.subscribe("SIT730/agrisense")


        self.mqtt_client.on_message = self.on_message

        self.mqtt_client.loop_start()




    def on_message(self, client, userdata, message):


        #Construct the dictionary
        try:
            #Decode from Bytestring, and then build a python dictionary with the message payload
            my_type, payload = build_dict(message.payload.decode("utf-8"))

            print(f"type = {my_type}")
            print(f"message = {payload}")

            # Insert into database
            if my_type == "event":
                self.database_accessor.modify_sensor(payload)
                self.database_accessor.insert_event(payload)
            elif my_type == "heartbeat":
                self.database_accessor.modify_sensor(payload)

        except:
            print("decode error - skipping this payload")

    def log_worker(self):

        self.connectMQTT()

        while True:
            time.sleep(10)