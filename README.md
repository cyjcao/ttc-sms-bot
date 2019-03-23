# TTC-SMS-BOT

This chatbot was created using **Python**, **Flask**, and the [Twilio API](https://www.twilio.com/).    
This application takes in user inputted strings via SMS and then chooses the appropriate endpoint from the NextBus public XML feed to get information which is then sent to the user as a SMS message.    
    
## Executing Application
1.    Set-up a Twilio Account
2.    Clone this repository into local machine
3.    Create a credentials.py where you'll store sensitive information such as Flask secret key and Twilio authentication tokens.
4.    Download ngrok
5.    Execute the application using flask run
6.    Run ngrok on whichever port is specified in flask