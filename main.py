from paho.mqtt import client as mqtt_client
import logging
from pymongo import MongoClient
import time

mqtt_server = '10.59.10.113'
port = 1883
client_id = 'Kubyk'
topic_sub = '#'
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logging.getLogger('pika').setLevel(logging.WARNING)
logger = logging.getLogger()

pictures = 10

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("Successfully connected to MQTT broker")
        else:
            logger.info("Failed to connect, return code %d", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.connect(mqtt_server, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        if msg.topic.startswith("frigate/") and msg.topic.endswith("/snapshot"):
            save_images(msg.payload)

    client.subscribe("frigate/+/+/snapshot")
    client.on_message = on_message

def save_images(payload):
    global pictures
    with open(f"received_image_{pictures}.jpg", "wb") as f:
        f.write(payload)
        logger.info(f"Image received and saved as 'received_image_{pictures}.jpg'")
        client = MongoClient("mongodb://192.168.10.37:27017/")
        db = client["photos"]
        collection = db["images"]
        current_time = time.localtime()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
        image_data = {  
            "filename": f"received_image_{pictures}.jpg",
            "data": payload,
            "timestamp" : formatted_time
        }
        collection.insert_one(image_data)
        logger.info(f"Image 'received_image_{pictures}.jpg' is saved in database.")
        
        pictures -= 1
        if pictures == 0:
            pictures = 10
        f.close()

def main():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    main()
