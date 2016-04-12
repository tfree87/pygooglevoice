''' A command-line interface to Google Voice'''


# Global Imports
import argparse
from pprint import pprint


# Local Imports
from voice import Voice


def send_message (voice, text=None, phone_number=None):
    ''' Send a text (SMS) message to a phone number'''
    
    phone_number = input('Number to send message to: ')
    text = raw_input('Message text: ')
    voice = voice
    voice.send_sms(phone_number, text)

    
def get_settings(voice):
    ''' List your Google Voice settings'''
    
    pprint(voice.settings)

    
def parse_arguments():
    '''Read arguments from the command line'''

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(help='Commands')

    # SMS command
    parser_command = subparsers.add_parser('sms', help='Send a text (SMS) message')
    parser_command.add_argument('-d', '--dial',
                    help='Phone number to send an SMS message to')
    parser_command.add_argument('-t', '--text',
        help='Text message to submit in a text message (SMS)')

    # Settings command
    parser_command = subparsers.add_parser('settings', help='Display Google Voice settings')

    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    voice = Voice()
    voice.login()
    if args.command == 'sms':
        send_message(voice)
    elif args.command == 'settings':
        get_settings(voice)


if __name__ == '__main__':
    ''' Run main() if this file is executed in Python '''
    main()
    
