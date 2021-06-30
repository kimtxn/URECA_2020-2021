/*
  Optical SP02 Detection (SPK Algorithm) using the MAX30105 Breakout
  By: Nathan Seidle @ SparkFun Electronics
  Date: October 19th, 2016
  https://github.com/sparkfun/MAX30105_Breakout

  This demo shows heart rate and SPO2 levels.

  It is best to attach the sensor to your finger using a rubber band or other tightening 
  device. Humans are generally bad at applying constant pressure to a thing. When you 
  press your finger against the sensor it varies enough to cause the blood in your 
  finger to flow differently which causes the sensor readings to go wonky.

  This example is based on MAXREFDES117 and RD117_LILYPAD.ino from Maxim. Their example
  was modified to work with the SparkFun MAX30105 library and to compile under Arduino 1.6.11
  Please see license file for more info.

  Hardware Connections (Breakoutboard to Arduino):
  -5V = 5V (3.3V is allowed)
  -GND = GND
  -SDA = A4 (or SDA)
  -SCL = A5 (or SCL)
  -INT = Not connected
 
  The MAX30105 Breakout can handle 5V or 3.3V I2C logic. We recommend powering the board with 5V
  but it will also run at 3.3V.
*/
#include <Arduino.h>
#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm_new.h"
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <math.h>

MAX30105 particleSensor;

#define MAX_BRIGHTNESS 255

uint32_t elapsedTime,timeStart;

uint32_t irBuffer[100]; //infrared LED sensor data
uint32_t redBuffer[100];  //red LED sensor data

int32_t bufferLength; //data length
int32_t old_n_spo2=0;
int32_t n_spo2=0;
float ratio,correl; 
int8_t validSPO2=0; //indicator to show if the SPO2 calculation is valid
int32_t heartRate=0; //heart rate value
int8_t validHeartRate=0; //indicator to show if the heart rate calculation is valid

byte pulseLED = 11; //Must be on PWM pin
byte readLED = 13; //Blinks with each data read

uint8_t k;

Adafruit_BNO055 myIMU = Adafruit_BNO055(55,0x29);
long ax,ay,az,mx,my,mz,gx,gy,gz=0;

void setup()
{
  Serial.begin(115200); // initialize serial communication at 115200 bits per second:

  pinMode(pulseLED, OUTPUT);
  pinMode(readLED, OUTPUT);

  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println(F("MAX30105 was not found. Please check wiring/power."));
    while (1);
  }

  Serial.read();

  byte ledBrightness = 40; //Options: 0=Off to 255=50mA
  byte sampleAverage = 4; //Options: 1, 2, 4, 8, 16, 32
  byte ledMode = 2; //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
  byte sampleRate = 100; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411; //Options: 69, 118, 215, 411
  int adcRange = 4096; //Options: 2048, 4096, 8192, 16384

  myIMU.begin();
  
  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange); //Configure sensor with these settings
  timeStart=millis();
}

void loop()
{
  bufferLength = 100; //buffer length of 100 stores 4 seconds of samples running at 25sps

  //read the first 100 samples, and determine the signal range
  for (byte i = 0 ; i < bufferLength ; i++)
  {
    while (particleSensor.available() == false) //do we have new data?
      particleSensor.check(); //Check the sensor for new data

    redBuffer[i] = particleSensor.getFIFORed();
    irBuffer[i] = particleSensor.getFIFOIR();
    particleSensor.nextSample(); //We're finished with this sample so move to next sample
        
    Serial.print(F("red "));
    Serial.print(redBuffer[i], DEC);
    Serial.print(F(" ir "));
    Serial.print(irBuffer[i], DEC);
    Serial.println(" HR 0 SPO2 0 0 0 0 0 0 0 0 0 0");
    
  }

  //calculate heart rate and SpO2 after first 100 samples (first 4 seconds of samples)
  maxim_heart_rate_and_oxygen_saturation(irBuffer, bufferLength, redBuffer, &n_spo2, &validSPO2, &heartRate, &validHeartRate, &ratio, &correl);

  //Continuously taking samples from MAX30102.  Heart rate and SpO2 are calculated every 2 second
  while (1)
  {
    //dumping the first 25 sets of samples in the memory and shift the last 75 sets of samples to the top
    for (byte i = 50; i < 100; i++)
    {
      redBuffer[i - 50] = redBuffer[i];
      irBuffer[i - 50] = irBuffer[i];
    }

    //take 25 sets of samples before calculating the heart rate.
    for (byte i = 50; i < 100; i++)
    {
      while (particleSensor.available() == false) //do we have new data?
        particleSensor.check(); //Check the sensor for new data

      //digitalWrite(readLED, !digitalRead(readLED)); //Blink onboard LED with every data read

      redBuffer[i] = particleSensor.getFIFORed();
      irBuffer[i] = particleSensor.getFIFOIR();
      particleSensor.nextSample(); //We're finished with this sample so move to next sample
      
      imu::Quaternion quat=myIMU.getQuat();
      imu::Vector<3> acc = myIMU.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
      imu::Vector<3> gyr = myIMU.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
      imu::Vector<3> mag = myIMU.getVector(Adafruit_BNO055::VECTOR_MAGNETOMETER);
      ax=acc.x();
      ay=acc.y();
      az=acc.z();
      mx=mag.x();
      my=mag.y();
      mz=mag.z();
      gx=gyr.x();
      gy=gyr.y();
      gz=gyr.z();
      
      //send samples and calculation result to terminal program through UART
      Serial.print(F("red "));
      Serial.print(redBuffer[i], DEC);
      Serial.print(F(" ir "));
      Serial.print(irBuffer[i], DEC);

      Serial.print(F(" HR "));
      Serial.print(heartRate, DEC);

//      Serial.print(F(" HRvalid "));
//      Serial.print(validHeartRate, DEC);

      Serial.print(F(" SPO2 "));
      Serial.print(n_spo2, DEC);

//      Serial.print(F(" SPO2Valid "));
//      Serial.print(validSPO2, DEC);

      Serial.print(" ");
      Serial.print(acc.x());
      Serial.print(" ");
      Serial.print(acc.y());
      Serial.print(" ");
      Serial.print(acc.z());
      Serial.print(" ");
      Serial.print(mag.x());
      Serial.print(" ");
      Serial.print(mag.y());
      Serial.print(" ");
      Serial.print(mag.z());
      Serial.print(" ");
      Serial.print(gyr.x());
      Serial.print(" ");
      Serial.print(gyr.y());
      Serial.print(" ");
      Serial.println(gyr.z());
    }

    //After gathering 50 new samples recalculate HR and SP02
    maxim_heart_rate_and_oxygen_saturation(irBuffer, bufferLength, redBuffer, &n_spo2, &validSPO2, &heartRate, &validHeartRate, &ratio, &correl);

  }
}
