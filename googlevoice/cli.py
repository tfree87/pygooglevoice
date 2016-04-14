''' A command-line interface to Google Voice '''


# Global Imports
import argparse
from bs4 import BeautifulSoup
from pprint import pprint


# Local Imports
from googlevoice import Voice


def send_message (voice, text=None, phone_number=None):
    ''' Send a text (SMS) message to a phone number'''

    # Initialize values
    voice = voice
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

    pprint(voice.settings)


def print_sms(voice) :
    '''
    print_sms
    Print out messages in a conversation
    '''

    voice = voice
    voice.sms()

    msgitems = []										# accum message items here
    #	Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup(voice.sms.html, 'html.parser')			# parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        print(('Convsersation' + ' ' + conversation['id'] + ':'))
        #	For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows :								# for all rows
            #	For each row, which is one message, extract all the fields.
            msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans : # for all spans in row
                cl = str(span["class"]).replace('gc-message-sms-', '')
                cl = cl.replace("['", '')
                cl = cl.replace("']", '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
            msgitems.append(msgitem)					# add msg dictionary to list
        for item in msgitems:
            string = '\t' + item['from'].strip(':') + ' (' + item['time'] + '): ' + item['text']
            print(string)
                

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


def main():
    args = parse_arguments()
    voice = Voice()
    voice.login()

    if args.command == 'sms':
        send_message(voice, phone_number=args.dial, text=args.text)
    elif args.command == 'settings':
        get_settings(voice)
    elif args.command == 'print':
        print_sms(voice)


if __name__ == '__main__':
    ''' Run main() if this file is executed in Python '''
    main()
