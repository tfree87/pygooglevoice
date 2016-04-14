
''' 
A command-line interface to Google Voice 
'''


# Global Imports
import argparse
from bs4 import BeautifulSoup
from pprint import pprint
import re

# Local Imports
from googlevoice import Voice


def send_message (text=None, phone_number=None):
    ''' Send a text (SMS) message to a phone number'''

    # Initialize values
    voice = login()
    phone_number = phone_number
    text = text

    # If no values are passed for phone number and text, ask user for input
    if phone_number == None:
        phone_number = eval(input('Number to send message to: '))
    if text == None:
        text = input('Message text: ')

    try:
        voice.send_sms(phone_number, text)
        print('Message successfully transmitted')
    except:
        print('Error: message not transmitted')
        raise

def get_settings(voice):
    ''' List your Google Voice settings'''
    voice = login()
    pprint(voice.settings)


def print_sms() :
    conversation_list = get_sms()

    # Print out each message in the conversation
    for conversation in conversation_list:
        print('Conversation ' + conversation['number'] + ':')
        print('------------------------------------------------------')
        for message in conversation['messages']:
            string = '\t' + message['from'].strip(':') + ' (' + message['time'] + '): ' + message['text']
            print(string)


def get_sms():
    """
    Returns a list of conversations obtained from Google Voice

    :param voice: A Google Voice object
    :return: Returns a list of conversations.
    """

    voice = login()
    voice.sms()

    # Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup(voice.sms.html, 'html.parser')

    # Loop through all coversations
    divs = tree.findAll('div',attrs={'id' : True},recursive=False)
    conversation_list= []
    for div in divs:
        # Get the conversation id and associate it with the conversation
        conversation = {'id' : div['id']}

        # Get the phone number associated with the conversation
        number_spans = div.findAll('span', attrs={'class': 'gc-message-type'}, recursive=True)
        for item in number_spans:
            number = re.sub('[^0-9]', '', item.string)
            conversation['number'] = number

        # Iterate through messages and get content
        rows = div.findAll(attrs={"class" : "gc-message-sms-row"})
        message_list = []
        for row in rows:
            message = {'id' : div['id']}
            # Loop through each element of the message and add to dictionary
            spans = row.findAll('span',attrs={'class' : True}, recursive=False)
            for span in spans:
                # Get the category of the span and remove formatting
                label = str(span['class']).replace("['gc-message-sms-", '')
                label = label.replace("']", '')
                # Append text to the dictionary
                message[label] = (" ".join(span.findAll(text=True))).strip()
            message_list.append(message)
        conversation['messages'] = message_list
        conversation_list.append(conversation)

    return conversation_list


def parse_arguments():
    '''Read arguments from the command line'''

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(
        title='Sub Commands',
        dest='command',
        help='Commands'
    )

    # SMS command
    parser_command = subparsers.add_parser(
        'sms',
        help='Send a text (SMS) message'
    )
    parser_command.add_argument(
        '-d',
        '--dial',
        help='Phone number to send an SMS message to'
    )
    parser_command.add_argument('-t', '--text',
        help='Text message to submit in a text message (SMS)')

    # Settings command
    parser_command = subparsers.add_parser(
        'settings',
        help='Display Google Voice settings'
    )
    parser_command = subparsers.add_parser(
        'print',
        help='Print a list of text messages (SMS)'
    )
    args = parser.parse_args()
    return args

def login():
    voice = Voice()
    voice.login()
    return voice

def main():
    args = parse_arguments()

    if args.command == 'sms':
        send_message(phone_number=args.dial, text=args.text)
    elif args.command == 'settings':
        get_settings()
    elif args.command == 'print':
        print_sms()


if __name__ == '__main__':
    ''' Run main() if this file is executed in Python '''
    main()
