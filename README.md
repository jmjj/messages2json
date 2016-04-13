E-mail message to JSON converter
================================

Version: 0.2.0

Author: Jari Juopperi

Overview
--------

A program that can be used to convert messages stored in various mailbox formats into JSON format. Currently the only supported input format is the `mailbox` format referred in the Python standard library
[documentation](https://docs.python.org/2/library/mailbox.html#mbox).

**Please note that this program is in the early stage of development. It is not ready for the business critical use.**

Installation
------------

To install use pip:

    $ pip install messages2json


Or clone the repo:

    $ git clone https://github.com/jmjj/messages2json.git
    $ python setup.py install

Usage
-----
To get help on the usage of the program:

    $  messages2json --help
    usage: messages2json [-h] [--input IN_F_OR_D] [--output OUT_F_OR_D] [--body]  
    [--format {mbox}] [--force]

    Convert e-mail messages to JSON format

    optional arguments:
    -h, --help           show this help message and exit
    --input IN_F_OR_D    input file or directory
    --output OUT_F_OR_D  output file or directory
    --body               include the body of the message, by default only
                         headers are converted
    --format {mbox}      the format of input messages
    --force              Overwrite the output files even if they exist

How to store messages to a file in `mbox` format ?
------------------------------------------
The following instructions help you to store messages from your favorite e-mail progran/service into a file in `mbox` format:
   + [Mozilla Thunderbird](https://freeshell.de/~kaosmos/mboximport-en.html)
   +  [Gmail](http://email.about.com/od/gmailtips/fl/How-to-Export-Your-Emails-from-Gmail-As-Mbox-Files.htm), not tested.
   + [MS Outlook](http://www.techhit.com/outlook/convert_outlook_mbox.html), not tested.





Contributing
------------

Bug report, pull requests and comments are appreciated. Please use the standard mechanisms of GitHub on [https://github.com/jmjj/messages2json](https://github.com/jmjj/messages2json) to submit your feedback.
