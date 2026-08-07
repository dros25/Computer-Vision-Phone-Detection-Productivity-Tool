/**
 * @file alarm_controller.ino
 * @brief Non-blocking Arduino firmware for audio alarm triggering via USB Serial
 */

// Hardware Configuration
const uint8_t BUZZER_PIN = 8;          // Digital pin connected to buzzer signal
const bool IS_PASSIVE_BUZZER = true;  // Set 'true' for Piezo PWM tone, 'false' for Active Buzzer

// Timing & Audio Parameters
const uint16_t ALARM_FREQUENCY = 2000; // Tone frequency in Hz (for passive buzzers)
const uint32_t ALARM_DURATION_MS = 500; // Alarm duration per trigger

// State Variables
bool alarmActive = false;
uint32_t alarmStartTime = 0;

void setup() {
    Serial.begin(9600);
    pinMode(BUZZER_PIN, OUTPUT);
    stopAlarm();
}

void loop() {
    processSerialInput();
    updateAlarmState();
}

/**
 * @brief Reads incoming serial commands at different times
 */
void processSerialInput() {
    while (Serial.available() > 0) {
        char command = Serial.read();
        if (command == 'H') {
            startAlarm();
        }
    }
}

/**
 * @brief Turns off alarm after set period of time
 */
void updateAlarmState() {
    if (alarmActive && (millis() - alarmStartTime >= ALARM_DURATION_MS)) {
        stopAlarm();
    }
}

/**
 * @brief Activates alarm
 */
void startAlarm() {
    alarmActive = true;
    alarmStartTime = millis();

    if (IS_PASSIVE_BUZZER) {
        tone(BUZZER_PIN, ALARM_FREQUENCY);
    } else {
        digitalWrite(BUZZER_PIN, HIGH);
    }
}

/**
 * @brief Deactivates alarm
 */
void stopAlarm() {
    alarmActive = false;
    if (IS_PASSIVE_BUZZER) {
        noTone(BUZZER_PIN);
    } else {
        digitalWrite(BUZZER_PIN, LOW);
    }
}
