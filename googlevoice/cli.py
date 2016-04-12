''' A command-line interface to Google Voice'''

# Global Imports
import argparse


# Local Imports
from voice import Voice


def send_message (voice, text=None, phone_number=None):
    ''' Send a text (SMS) message to a phone number'''
    
    phone_number = input('Number to send message to: ')
    text = raw_input('Message text: ')
    voice = voice
    voice.send_sms(phone_number, text)

def parse_arguments():
    '''Read arguments from the command line'''

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('command',
        help='Send a message via Google Voice')
    #parser.add_argument('-d', '--dial',
    #                help='Phone number to send an SMS message to')
    #parser.add_argument('-t', '--text'
    #    help='Text message to submit in a text message (SMS)')

    args = parser.parse_args()
    return args
    
if __name__ == '__main__':
    args = parse_arguments()
    voice = Voice()
    voice.login()
    if args.command == 'send':
        send_message(voice)
