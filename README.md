# ChatSpot: Meet new people through IoT

**ChatSpot** is an RaspberryPi-based device designed to promote social interaction and community building in public and private spaces. By facilitating face-to-face conversations with a simple, user-friendly interface, ChatSpot helps people overcome barriers to social engagement and reduces feelings of loneliness in communities.

---

## Overview

ChatSpot aims to transform public spaces into hubs of connection by making it easier for people to start conversations with strangers. Unlike digital alternatives like social media, ChatSpot focuses on real-time, human interactions, offering a simple and accessible way for individuals to engage socially.

---

## How It Works

1. **Setup in Public Spaces:**
   - ChatSpot devices are to be installed in parks, cafes, benches, or similar spaces.
2. **Simple Interaction:**
   - A glowing light indicates that ChatSpot is available.
   - A user presses the button to signal they’re open to a conversation (light changes color).
   - A second person presses the button to join the interaction.
3. **Ice-Breaker Prompts:**
   - The device displays and reads out a conversation starter, such as *“If you could travel anywhere tomorrow, where would you go and why?”*
4. **Data Analysys:**
    - The device connects to a server/broker and sends information of the converastions.
    - The server/broker displays almost real time data that can be used to improve the usage and questions.

---

## Key Features

- **Human-Centric Design:** Facilitates natural, face-to-face conversations.
- **Simple, Accessible Interface:** Includes a button, labeled LED lights, a display, and a speaker for ease of use by all age groups and abilities.
- **Ice-Breaker Prompts:** Reduces akwarness about starting conversations by providing engaging, pre-selected topics for everyone.

---

## Use Cases

- **New Residents:** Helping individuals new to a city meet others and integrate socially.
- **Shy Individuals:** Breaking the ice for people hesitant to initiate conversations.
- **Elderly or Isolated Individuals:** Creating opportunities for social interaction for those who may feel lonely.
- **Public Spaces and Social Venues:** Transforming parks, benches, cafes, and more into hubs of social connection.

---

## Advantages

- **Promotes Real-World Interaction:** Encourages human connection in physical spaces, avoiding the isolating effects of purely digital platforms.
- **Accessible Design:** Accommodates users with disabilities through a simple interface and dual output modes (display and speaker).
- **Mental Well-Being:** Helps reduce loneliness and fosters mental health by connecting individuals.
- **Transforms Spaces:** Activates underutilized public and private spaces for social interaction.

---

## Future Enhancements

- **AI-Generated Prompts:** Use LLMs to generate tailored questions based on user interests.
- **App-Enabled Reservations:** Allow users to book ChatSpots at specific times.
- **Enhanced Analytics:** Gather feedback to improve question quality and engagement.

---

## Set-up

### **Hardware**

1. **Raspberry Pi (any model with GPIO and internet connectivity)**
   - Acts as the core controller for the ChatSpot device.

2. **Grove Components:**
   - **Grove Button v1.2 (3 pieces)**  
     Used for initiating and joining a conversation, as well as additional interactions.
   - **Grove LCD RGB Backlight v4.0**  
     Displays conversation prompts and interaction status.
   - **Grove Rotary Angle Sensor v1.2**  
     Allows users to control volume or navigate menu options (if applicable).
   - **Grove Ultrasonic Distance Sensor v2.0**  
     Detects when a person is near the device and lights up the availability indicator.

3. **Speaker**
   - Plays audio prompts for ice-breaker questions, ensuring accessibility for users with visual impairments.

4. **PC/Server**
   - Acts as the MQTT broker for managing communication between multiple ChatSpot devices and (optionally) a backend app or database.

### **Software**

Both the PC/Server and the RaspberryPi require Python to be installed, as well as MQTT through [Mosquitto](https://mosquitto.org/), and they must be able to communicate between them.

- **PC/Server requirements**
  - [SQLite](https://www.sqlite.org/) to store the data in a local database.
  - Configuration of Mosquitto to act as the broker.
  - All the python packages listed in the [pc-requirements.txt](broker/pc-requirements.txt).
   
    ```bash 
     pip install -r pc-requirements.txt
    ```
    
- **RaspberrPi requirements**
  - Mosquitto client.
  - A python virtual environment using [venv](https://docs.python.org/es/3/library/venv.html)
  - All the python packages listed in the [raspi-requirements.txt](raspi/raspi-requirements.txt)

    ```bash 
     pip install -r raspi-requirements.txt
    ```

#### **Execution**

To make all components of ChatSpot work together, follow these steps:

1. **On the Raspberry Pi:**
   - Launch the main program that controls the ChatSpot device by running:

     ```bash 
     source <env_name>/bin/activate
     python3 main.py
     ```

   - In addition, the execution on the RaspberryPi can be automated with a job-scheduler like **cron**.
     This crontab routine activates all the funcionality when turning the RaspberryPi on:

     ```bash
     @reboot /bin/bash -c "source <env_name></env_name>/bin/activate && cd path/to/the/project && python main.py" >> /path/to/log/folder/ChatSpot-raspi.log 2>&1
     ```

2. **On the Server/PC:**
   - Start the MQTT broker by running:

     ```bash
     python broker.py
     ```

   - Launch the visualization dashboard for monitoring and managing ChatSpot interactions:

     ```bash
     python visu-dash.py
     ```
