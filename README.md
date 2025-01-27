# RR-Team-21-emostream-concurrent-emoji-broadcast-over-event-driven-architecture

## Project Description

EmoStream is a scalable system designed to capture, process, and broadcast real-time emoji reactions during live events. It leverages event-driven architecture with tools like Kafka and Spark to handle massive user interactions, process emoji data in micro-batches, and aggregate reactions efficiently. The system enhances audience engagement by reflecting collective sentiments dynamically through real-time updates while ensuring seamless scalability and low latency.

## Tech Stack

- Apache Kafka
- Apache Spark
- Apache Zookeeper

## Brief Overview

1.`app.py`

**Purpose:** To act as the entry point for receiving emoji data and producing messages to Kafka for further processing.

**What it does:** It accepts emoji data as JSON through a Flask endpoint and sends the data to a Kafka topic in batches.

**Role in the system:** Acts as the producer for the initial data pipeline, collecting emoji messages from clients and relaying them to Kafka.

**How it works:** Buffers emoji data received via HTTP POST requests, then sends them to the emoji_topic topic in Kafka every 500ms using a timer-based batching mechanism.

2.`client_simulator.py`

**Purpose:** To simulate multiple clients interacting with the system, registering, and sending emoji data.

**What it does:** Registers clients with subscribers and simulates the sending of emoji messages to the Flask app at fixed intervals.

**Role in the system:** Mimics real-world clients generating and sending data, testing the flow of the data pipeline.

**How it works:** Creates multiple threads to simulate clients, assigns each to a subscriber, and sends 20 emoji messages per client using HTTP POST requests with controlled time intervals.

3.`emoji_processor.py`

**Purpose:** To process and aggregate emoji data streamed from Kafka, producing meaningful insights like emoji counts.

**What it does:** Consumes emoji data from Kafka, aggregates counts in 2-second windows, and writes the aggregated data back to another Kafka topic.

**Role in the system:** Processes raw emoji data into structured insights, preparing it for distribution to subscribers.

**How it works:** Utilizes Spark Structured Streaming for real-time processing, with a checkpointing mechanism to ensure fault tolerance. Aggregated data is filtered and formatted as JSON before being published to the `aggregated_emoji_topic`.

4.`pubsub_service.py`

**Purpose:** To distribute processed data to subscribers for real-time consumption.

**What it does:** Consumes aggregated emoji data from Kafka and forwards it to active subscribers based on their client assignments.

**Role in the system:** Acts as the final step in the pipeline, ensuring subscribers receive the processed data they are interested in.

**How it works:** Maintains active subscriber information using SubscriberManager. Listens to the `aggregated_emoji_topic` and broadcasts messages to appropriate WebSocket subscribers.

5.`registration_app.py`

**Purpose:** To manage client registration, unregistration, and assignment to subscribers.

**What it does:** Registers new clients, assigns them to subscribers, and returns WebSocket URLs for data streaming. Also cleans up assignments during unregistration.

**Role in the system:** Provides a client-facing interface for managing connections to the system.

**How it works:** Exposes Flask endpoints for registration/unregistration and communicates with PubSubService to manage client-subscriber mappings efficiently.

6.`subscriber_manager.py`

**Purpose:** To manage the mapping of clients to subscribers for balanced data distribution.

**What it does:** Tracks active subscribers, assigns clients to available subscribers, and dynamically adds new subscribers when needed.

**Role in the system:** Ensures efficient load balancing and scalability for subscriber management.

**How it works:** Uses data structures to maintain subscriber-client mappings and checks thresholds to decide when to add or remove subscribers dynamically.

7.`subscriber_service.py`

**Purpose:** To provide WebSocket-based communication for subscribers to receive aggregated emoji data in real time.

**What it does:** Establishes WebSocket connections with subscribers and relays messages from Kafka to the appropriate clients.

**Role in the system:** Acts as the subscriber-facing endpoint, enabling real-time data delivery.

**How it works:** Maintains WebSocket sessions, listens to `aggregated_emoji_topic` in Kafka, and broadcasts messages to connected subscribers mapped by their session IDs.

## Commands to run the project

Ensure to `pip install` the required packages before running the project.

### 1. Kafka Setup

- On a terminal, navigate to the Kafka installation directory to access its binaries and configuration files.

  ```bash
  cd /usr/local/kafka
  ```

- On a new terminal, start the Zookeeper server, which Kafka depends on for maintaining cluster state.

  ```bash
  bin/zookeeper-server-start.sh config/zookeeper.properties
  ```

- On another terminal, start the Kafka broker, which handles messaging between producers and consumers.

  ```bash
  bin/kafka-server-start.sh config/server.properties
  ```

- On a fresh terminal, create the `emoji_topic`, which will be used for sending raw emoji data from the producer.

  ```bash
  bin/kafka-topics.sh --create --topic emoji_topic --bootstrap-server localhost:9092
  ```

- On a new terminal, create the aggregated_emoji_topic, which will store processed emoji data for subscribers.

  ```bash
  bin/kafka-topics.sh --create --topic aggregated_emoji_topic --bootstrap-server localhost:9092
  ```

---

### 2. Running Services

- Navigate to the project directory containing all the python files.

- Open a new terminal and start the WebSocket-based subscriber service to relay processed emoji data to clients.

  ```bash
  python3 subscriber_service.py
  ```

- In a seperate terminal, launch the registration service for managing client registrations and unregistrations.

  ```bash
  python3 registration_app.py
  ```

- In another terminal, start the Flask app to receive emoji data and produce it to the `emoji_topic` Kafka topic.

  ```bash
  python3 app.py
  ```

---

### 3. Spark Streaming

- On a fresh terminal, execute the Spark streaming job to process emoji data in real-time and produce aggregated results to `aggregated_emoji_topic`.

  ```bash
  spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3 emoji_processor.py
  ```

---

### 4. Simulating Clients

- Open a seperate terminal and simulate multiple clients registering and sending emoji data to the Flask app.

  ```bash
  python3 client_simulator.py
  ```

---

### 5. Monitoring Kafka Topics

- These commands are optional and used to observe data in Kafka topics.

- On a new terminal, view raw emoji data being produced to the `emoji_topic` This could be useful for debugging and monitoring.

  ```bash
  bin/kafka-console-consumer.sh --topic emoji_topic --bootstrap-server localhost:9092
  ```

- Open a seperate terminal to view processed data being written to the `aggregated_emoji_topic`. This could be useful for verifying processing output.

  ```bash
  bin/kafka-console-consumer.sh --topic aggregated_emoji_topic --bootstrap-server localhost:9092
  ```

## Conclusion

In conclusion, this project demonstrates a real-time data processing pipeline using Kafka for message streaming and Spark for data aggregation. It enables efficient processing of emoji data with a Flask application handling data ingestion and WebSocket communication for live updates. The system effectively simulates client interactions and provides aggregated emoji data for real-time insights.
