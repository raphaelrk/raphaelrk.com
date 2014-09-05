#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# imports
import logging  # for webapp2 exception handling
import webapp2  # necessary for app engine
import cgi  # used for escape_html
from string import maketrans  # used in rot13
import re

# set up logging.. didn't work
# logging.basicConfig(filename='example.log', level=logging.DEBUG)
# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')

# html pages
index = open('html/index.html', 'r').read()  # home page
rot13form = open('html/rot13.html', 'r').read()  # rot13 page
signupForm = open('html/signup.html', 'r').read()  # signup page
unlikerPage = open('html/unliker.html', 'r').read()  # facebook mass unliker
keybaseTxt = open('html/keybase.txt', 'r').read()  # keybase verification
html404 = open('html/404.html', 'r').read()  # 404 page not found
html500 = open('html/500.html', 'r').read()  # 500 internal server error page

# pjs sketches
cloverSketch = open('html/clover.html', 'r').read()  # clover page
mandelbrotSketch = open('html/mandelbrot.html', 'r').read()  # mandelbrot page


# escapes >, <, ", and &
def escape_html(s):
    return cgi.escape(s, True)


# unused but it took a while to write so its staying
def extreme_escape_html(s):
    for (k, v) in (('%', '%25'),
                   ('/', '%2F'),
                   ('\\', '%5C'),
                   ('&', '%26'),
                   ('<', '%3C'),
                   ('>', '%3E'),
                   ('"', '%22'),
                   ("'", '%27'),
                   ('`', '%80'),
                   (' ', '%20'),
                   ('!', '%21'),
                   ('@', '%40'),
                   ('$', '%24'),
                   ('(', '%28'),
                   (')', '%29'),
                   ('=', '%3D'),
                   ('+', '%2B'),
                   ('{', '%7B'),
                   ('}', '%7D'),
                   ('[', '%5B'),
                   (']', '%5D')):
        s = s.replace(k, v)
    return s


## regular expressions for user, email, pass validation
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


# user validation
def valid_username(username):
    return USER_RE.match(username)


# password validation
def valid_password(password):
    return PASS_RE.match(password)


# email validation (note: emails can also be blank)
def valid_email(email):
    return EMAIL_RE.match(email)


# Base Handler that others extend, includes logging
class BaseHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug):
        # Log the error.
        logging.exception(exception)

        # Set a custom message.
        response.write('An error occurred.')

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            response.set_status(exception.code)
        else:
            response.set_status(500)


# handles home page
class MainHandler(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(index)

    def post(self):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write("index")


class SignupHandler(BaseHandler):
    # Writes the signup form to the response
    # If there was an error, allows caller to repopulate forms
    # and specify the error
    def writeForm(self, user="", email="",
                  userErr="", passErr="", verifyErr="", emailErr=""):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(signupForm % {"user": user,
                                              "email": email,
                                              "userErr": userErr,
                                              "passErr": passErr,
                                              "verifyErr": verifyErr,
                                              "emailErr": emailErr})

    def get(self):
        self.writeForm()

    def post(self):
        # user input
        user_username = escape_html(self.request.get('username'))
        user_pass = escape_html(self.request.get('password'))
        user_verify = escape_html(self.request.get('verify'))
        user_email = escape_html(self.request.get('email'))

        # check if valid inputs
        user_valid = valid_username(user_username)
        pass_valid = valid_password(user_pass)
        email_valid = len(user_email) == 0 or valid_email(user_email)
        verify_valid = user_pass == user_verify  # check if passwords match

        # go to welcome page upon good input
        if user_valid and pass_valid and email_valid and verify_valid:
            self.redirect('/welcome?username=' + user_username)

        # repopulate form and display error messages
        else:
            # declare variables and their default values
            user_err = ""
            pass_err = ""
            verify_err = ""
            email_err = ""

            # add error messages
            if not user_valid:
                user_err = "That's not a valid username."
            if not pass_valid:
                pass_err = "That wasn't a valid password"
            elif not verify_valid:
                verify_err = "Your passwords didn't match."
            if not email_valid:
                email_err = "That's not a valid email."

            # write form to response
            self.writeForm(user_username, user_email,
                           user_err, pass_err, verify_err, email_err)


class WelcomeHandler(BaseHandler):
    def writeWelcome(self):
        username = self.request.get('username')
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write("Welcome, " + username + "!")

    def get(self):
        self.writeWelcome()

    def post(self):
        self.writeWelcome()


class Rot13Handler(BaseHandler):
    def writeForm(self, text=""):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(rot13form % {"text": text})

    def get(self):
        self.writeForm()

    def post(self):
        user_text = str(escape_html(self.request.get('text')))

        # translation table
        fromABC = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        toABC = "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM"
        trans = maketrans(fromABC, toABC)

        new_text = user_text.translate(trans)
        self.writeForm(new_text)


class PjsHandler(BaseHandler):
    sketches = {'clover': cloverSketch, 'mandelbrot': mandelbrotSketch}

    def get(self):
        sketch = self.request.get('sketch')

        if sketch in self.sketches:
            self.response.out.write(self.sketches[sketch])
        else:
            self.redirect('/')


class UnlikerHandler(BaseHandler):
    div_template = """<div class="fb-like-box" data-href="https://www.facebook.com/%(id)s" data-colorscheme="light" data-show-faces="false" data-header="false" data-stream="false" data-show-border="false"></div>"""

    def writeForm(self, divs=""):
        self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.response.out.write(unlikerPage % {"divs": divs})

    def get(self):
        self.writeForm(self.div_template % {"id": "pageunliker"})

    def post(self):
        # ids of liked pages
        user_liked_pages = escape_html(self.request.get('urls'))
        user_liked_pages = user_liked_pages.split(',')

        # write form to response
        divs = ""

        for page in user_liked_pages:
            divs += self.div_template % {"id": "pageunliker"}

        self.writeForm(divs)


class KeybaseHandler(BaseHandler):
    def get(self):
        self.response.out.write(keybaseTxt)


def handle_404(request, response, exception):
    logging.exception(exception)
    response.write(html404)
    response.set_status(404)


def handle_500(request, response, exception):
    logging.exception(exception)
    response.write(html500)
    response.set_status(500)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/index.html', MainHandler),
    ('/home', MainHandler),
    ('/index', MainHandler),

    ('/rot13', Rot13Handler),
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/pjs', PjsHandler),
    ('/unliker', UnlikerHandler),
    ('/keybase.txt', KeybaseHandler)
], debug=True)

app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
