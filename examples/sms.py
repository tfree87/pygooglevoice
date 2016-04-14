from googlevoice import Voice
from googlevoice.util import input

voice = Voice()
voice.login()

phoneNumber = eval(input('Number to send message to: '))
text = eval(input('Message text: '))

voice.send_sms(phoneNumber, text)