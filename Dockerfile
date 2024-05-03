FROM python
WORKDIR /app
copy . /app
RUN pip install paho-mqtt
RUN pip install pymongo
