# -*- coding: utf-8 -*-

'''
Created on Wed Mar  2 10:56:34 2016

@author: jmjj (Jari Juopperi, jmjj@juopperi.org)
'''

import sys
import os
import argparse
import mailbox
import json
import tempfile


def parse_cmd_line_args(arg_str: str='') -> argparse.Namespace:
    '''
        Parse the command line arguments

        Arguments:
        arg_str:       String of command line argumnets. To support
                       unit testing.

        Output:
        Namespace containing command line optios; see module argparse
    '''

    parser = argparse.ArgumentParser(description=
                                     'Convert e-mail messages to JSON format')
    parser.add_argument('--input', dest='in_f_or_d', action='store',
                        default="stdin", help='input file or directory')
    parser.add_argument('--output', dest='out_f_or_d', action='store',
                        default="stdout", help='output file or directory')
    parser.add_argument('--body', dest='include_body', action='store_true',
                        default=False, help='include the body of the message,\
                        by default only headers are converted')
    parser.add_argument('--format', dest='format', choices=['mbox'], action='store',
                        default="mbox", help='the format of input messages')
    parser.add_argument('--force', dest='force_save', action='store_true',
                        default=False,
                        help='Overwrite the output files even if they exist')

    if arg_str == '':
        args = parser.parse_args()
    else:
        args = parser.parse_args(arg_str.split())

    return args


def expand_paths(source: str, destination: str) -> dict:
    '''
        Expand the given input file/directory to a list of absolute paths
        to files to be processed. Expand the give ouput file/directory to
        a list of absolute paths.

        Verify that the input files exists and are readable. Verify that the
        verify that the output directory exists and is writable.

        Arguments:
        source:      User given paths to sources of the content.
        destination: User given paths to the deststinations of the processed
                     content

        Output:
        Dictionary that contains the input-output mapping of the expanded paths.

    '''

    abs_source_path = ""
    abs_dest_path = ""
    input_output_map = {}

    if source == 'stdin':
        abs_source_path = source
    else:
        abs_source_path = os.path.abspath(os.path.expanduser(source))

    if destination == 'stdout':
        abs_dest_path = destination
    else:
        abs_dest_path = os.path.abspath(os.path.expanduser(destination))

    input_output_map[abs_source_path] = abs_dest_path

    return input_output_map


def process_files(io_map: dict, msg_content_format: str, force: bool, body: bool) -> None:
    '''
        Convert a set of files

        Arguments:
        in_file_list:     Absolute paths of files to be processed.
        content_format:   The input format of the messages.

        Output: none
    '''

    # Process each mbox file
    for mail_file in io_map.keys():
        # mailbox.mbox() nrequires a path to mailbox file, a handle to an open
        # file is not acceptable. Write the input from stdin to temporary file
        # and pass the path to the temporary file later to mailbox.mbox()
        if mail_file == 'stdin':
            real_mail_file = tempfile.NamedTemporaryFile(mode='w').name
            with open(real_mail_file, mode='w', newline=None) as real_fp:
                for line in sys.stdin:
                    real_fp.write(line)
        else:
            # The input comes from a real file, so copy the path to be
            # passed to mailbox.mbox()
            real_mail_file = mail_file

        # Construct a list of dictionaries, a dictionary for each mbox message
        # in the input file.
        list_of_messages = []
        for message in mailbox.mbox(real_mail_file, create=False):
            list_of_messages.append(process_one_message(message, body))

        # Send the messages out
        send_messages_out(io_map[mail_file], list_of_messages,
                          msg_content_format, force)

        # If the content was coming stdin, remove the temporary file.
        if mail_file == 'stdin':
            os.remove(real_mail_file)


def process_one_message(message: mailbox.mboxMessage, inc_body: bool) -> dict:
    '''
       Process one mailbox message.

       Arguments:
       message: Mailbox message to be processed.
       inc_body: Process message body or not.

       Output: Dictionary that contains the content of the message.
    '''

    # mbox syntax allows tabs, newlines and carriage returns in the message.
    # These characters are not valid symbols in JSON. Remove the control
    # Removae the control characters from the mbox message based dictionaries.
    temp_dict = {key:str(message[key]).replace('\r\n', ' ').replace('\r', ' ').\
                replace('\n', ' ').replace('\t', ' ') for key in message.keys()}
    if inc_body:
        temp_dict.update(process_message_body(message))

    return temp_dict


def process_message_body(message: mailbox.mboxMessage) -> dict:
    '''
       Process the body of the message

       Arguments:
       message: Mailbox message to be processed.

       Ouput: Dictionary where the parts of the message are keyes int the
              following way part 0 -> "body_0", part 1 -> "body_1" etc.
    '''

    part_dict = {}
    part_count = 0
    if message.is_multipart():
        part_count = 1
        for part in message.walk():
            part_dict['body_'+str(part_count)] = str(part).\
                 replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ').\
                 replace('\t', ' ')
            part_count = part_count + 1
    else:
        part_dict['body_'+str(part_count)] = message.get_payload().replace('\r\n', ' ').\
                replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')

    return part_dict

def send_messages_out(out_file: str, list_of_messages: list,
                      msg_content_format: str, force: bool) -> None:
    '''
         Store list of message to a file in the selected fomat.

         Arguments:
         out_file:             The absolute path of the ouput file.
         list_of _messages:    List of dicts containitn the messages.
         msg_content_format:   The format desrired output format. Only JSON
                               supported currently
         force:                True: Overwrite the existing output file
                               False: Do not overwrite the existing output file
    '''

    file_mode = 'x'
    if out_file == "stdout":
        json.dump(list_of_messages, sys.stdout)
    else:
        if force:
            # Overwrite the existing file
            file_mode = 'w'
        else:
            # Do not overwrite the existing file
            file_mode = 'x'
        try:
            with open(out_file, mode=file_mode) as out_file_pointer:
                json.dump(list_of_messages, out_file_pointer)
        except (OSError, IOError) as inst:
            print("Can't write to ouput file: {}".format(inst))
            sys.exit(1)

def main():
    '''
        The top level function of the program
    '''

    args = parse_cmd_line_args()
    io_map = expand_paths(args.in_f_or_d, args.out_f_or_d)
    process_files(io_map, args.format, args.force_save, args.include_body)


if __name__ == "__main__":
    main()
