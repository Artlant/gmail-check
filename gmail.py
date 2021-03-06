#!/usr/bin/env python3

# _Settings____________________________________________________________________
#  CONFIG_PATH = ('~/.local/gmail.cfg')
#  MAX_OPEN_EMAIL = 5
# _____________________________________________________________________________

# https://pypi.org/search/?q=NAME
import logging
import sys
import os
import configparser
import argparse
import feedparser
import webbrowser
import requests
from urllib import parse
from plyer import notification
from plyer.utils import platform


def get_args():
    # import argparse
    parser = argparse.ArgumentParser(
        description='In interactive mode you able to manage your keys.'
    )
    parser.add_argument(
        '-c', '--config', help='Specify a config file.'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true', help='Enables full logging, including debug information.'
    )
    args = parser.parse_args()

    if args.config:
        global CONFIG_PATH
        CONFIG_PATH = args.config

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)


def parse_config(PATH="./gmail.cfg", CONFIG_SECTION='profile'):
    global CONFIG_PATH
    try: CONFIG_PATH
    except NameError: CONFIG_PATH = PATH
    # import configparser
    # HOME = os.environ['HOME']
	# Linux /HOME dit
    if CONFIG_PATH and CONFIG_PATH.startswith('~'):
        CONFIG_PATH = os.path.expanduser("~") + CONFIG_PATH[1:]
    
    try:
        config_file = configparser.ConfigParser()
        config_file.read(CONFIG_PATH)

        global user
        user = config_file.get(CONFIG_SECTION, 'user')
        global passwd
        passwd = config_file.get(CONFIG_SECTION, 'passwd')
        
        global notify
        notify = config_file.getboolean(CONFIG_SECTION, 'notify')

        logging.info("reading config file: %s" % CONFIG_PATH)

        return get_mail_url(user, passwd)

    except Exception as e:
        raise print(str(e), "could not read config file")


def get_mail_url(USER, PWD):
    return 'https://%s:%s@mail.google.com/mail/feed/atom' % (USER, PWD)


def send_notify(TITLE="mail notify", MESSAGE="test"):
	#from plyer import notification
	#from plyer.utils import platform
    global notify
    if notify:
       notification.notify(
           title=TITLE,
           message=MESSAGE,
		   app_icon=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icon') + '.ico' if platform == "win" else '.png', # On Windows ".ico" is required, on Linux ".png"
           timeout=7  # seconds
       )
	
	
def open_rss_link(URL):
   #  import feedparser
    try:
       if not int(MAX_OPEN_EMAIL) > 1:
         MAX_OPEN_EMAIL = 10
    except NameError: MAX_OPEN_EMAIL = 10
    
    rss = feedparser.parse(URL)
    
    logging.info("Feed Title %s" % rss.feed.title)
    
    if (len(rss.entries) > int(MAX_OPEN_EMAIL)):
       webbrowser.open('https://mail.google.com/')
       logging.error("to many open new mail!")

    else:
       for entry in rss.entries:
          f=parse.parse_qsl(parse.urlsplit(entry.link).query)
          message_id=dict(f)['message_id']
          logging.info("message_id: %s" % message_id)
          logging.info("Title: %s" % entry.title)
          logging.info("link: %s" % entry.link)
          
          webbrowser.open('https://mail.google.com/mail/u/0/h/?&v=c&th=%s' % message_id)
    # return entry.link


def get_gmail(URL):
    #  import requests
    r = requests.get(URL)
       
    if r.status_code == 401:
       print("login [%s] or password [%s] is incorrect\n%s" %
       (user, passwd, 'Also try enable "Allow less secure apps" on https://myaccount.google.com/lesssecureapps'))
       return False
       
    elif r.status_code != 200:
       print("Requests error [%s] - %s" % (r.status_code, URL))
       return False
       
    contents = r.text
    ifrom=contents.index('<fullcount>') + 11
    ito=contents.index('</fullcount>')

    mail_count=int(contents[ifrom:ito])

    if mail_count > 0:
        mail_ed="mail"
        if mail_count > 1:
            mail_ed += "s"

        send_notify("Gmail", "%d new %s" % (mail_count, mail_ed))
        print(" %s" % mail_count)
        return contents

    elif mail_count != 0:
        print("gmail format xml is changed")
    else:
        logging.info("new mail not found")

    return False

def main():
    try:
        get_args()
        logging.info("Working...")
        mail_url=parse_config()
        if mail_url:
            new_gmail=get_gmail(mail_url)
            if new_gmail:
                open_rss_link(new_gmail)
            
        logging.info("completed.")

    except IOError as e:
        #print("I/O error: %s" % format(e))
        print("Failed to establish a new connection")

    #  hide error msg
    #  finally:
        #  sys.exit()


if __name__ == '__main__':
    main()
