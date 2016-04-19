# coding=utf-8
import re
from flask import Blueprint, render_template,\
                  session, request, redirect, url_for,\
                  flash, make_response, abort
from database_setup import User
from hmac import new as hmac_new
from os import urandom
import random, string
from functools import wraps
from urlparse import urlparse, parse_qs

from oauth2client import client, crypt
import config

blueprint = Blueprint('user', __name__)

def login_required(*args, **kwargs):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      print 'step: login_required decorator.'
      if check_signin() == False:
        print 'login_required: User is NOT signed in. Checked in login_required decorator.'
        return redirect(url_for('user.do_login', next = request.path))
      else:
        print 'login_required: User is signed in. Checked in login_required decorator.'
      return f(*args, **kwargs)
    return decorated_function
  return decorator

@blueprint.route('/login', methods=['GET', 'POST'])
def do_login():
  print 'step: do_login() with request method - ', request.method
  user = None
  _is_authenticated = False
  
  try:
    if request.method == 'GET':
      if 'user_id' in session:
        user = User.get_by_id(get_user_id_from_session())
        if user is None:
          raise
          print 'user %s is not existing.' % get_user_id_from_session()
        else:
          _is_authenticated = check_signin()
          print 'user exists'
      
    elif request.method == 'POST':
      #Check e-mail
      email = request.form['email']
      if validate_email(email) == None:
        flash('This e-mail address is invalid.', 'error')
        raise
      
      user = User.get_by_id(email)
        
      if user is None:
        flash('This e-mail is not registered.', 'error')
        raise
      
      #Check password
      if user.verify_password(request.form['password']) == False:
        flash('Password is invalid!', 'error')
        raise
      
      session['user_id'] = email
      _is_authenticated = True
  except:
    session.pop('user_id', None)
  finally:
    if _is_authenticated == True:
      print '<authenticated>'
      response = make_response(redirect_common(url_for('user.myaccount')))
      key_random = urandom(24)
      session['random_auth'] = hmac_new(key_random, get_user_id_from_session()).hexdigest()
      response.set_cookie('random_auth', session['random_auth'])
      return response
    else:
      print '<NOT authenticated>'
      return render_template('login.html', email = get_user_id_from_session())
  
@blueprint.route('/logout')
def do_logout():
  session.pop('user_id', None)
  session.pop('token', None)
  session.pop('signin_party', None)
  
  response = make_response(redirect_common(url_for('user.do_login')))
  response.delete_cookie('random_auth')
  return response
  
@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
  return 'signup page'
  
@blueprint.route('/myaccount')
@login_required()
def myaccount():
  return render_template('myaccount.html')

def validate_email(email_address):
  email_format = re.compile('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$')
  return re.match(email_format, email_address)

def get_user_id_from_session():
  if 'user_id' in session:
    return session['user_id']
  else:
    return None
    
def do_before_request():
  csrf_protect()
  session.permanent = True
  
def inject_context():
  print 'inject_context'
  user = User.get_by_id(get_user_id_from_session())
  if user is None:
    print 'failed to inject user.'
    user = User()
  else:
    print 'successful to inject user.'
  
  def check_signin_in_template():
    print 'step: check_signin_in_template().'
    return check_signin()
  
  def redirect_in_template(last_path):
    return redirect_common(last_path, just_path = True)
  
  return dict(current_user = user, \
              redirect_in_template = redirect_in_template, \
              check_signin_in_template = check_signin_in_template)

def redirect_common(last_path, just_path = False):
  path = '/'
  
  #1. Check 'next' argument
  next_argument = request.args.get('next')
  if next_argument == request.path or next_argument == None:
    #result is invalid
    print 'next argument is invalid.'
    print next_argument
    print 'request.path = ' + request.path
  else:
    if just_path == True:
      return next_argument
    return redirect(next_argument)
  
  #2. Check request.referrer
  if request.referrer != None:
    dict_params = {}
    dict_params = parse_qs(urlparse(request.referrer).query)
    path_referrer = '/'
    if 'next' in dict_params:
      path_referrer = dict_params['next'][0]
    if path_referrer == urlparse(request.referrer).path or path_referrer == request.path:
      #result is invalid
      print 'request.referrer is invalid.'
      print request.referrer
      print 'request.path = ' + request.path
    else:
      if just_path == True:
        return request.referrer
      return redirect(request.referrer)
  
  #3. Check last path
  if last_path == request.path or last_path == None:
    #result is invalid
    print 'last path is invalid.'
    print last_path
    print 'request.path = ' + request.path
  else:
    if just_path == True:
      return last_path
    return redirect(last_path)
  
  if just_path == True:
    return path
  return redirect(path)
  
@blueprint.route('/googlesignin', methods=['POST'])
def googlesignin():
  print 'step: googlesignin'
  token = request.form['idtoken']
  
  if token == None:
    print 'token is none.'
    return 'False'
  else:
    print 'token is available.'
  
  session['signin_party'] = 'google'
  result, idinfo = get_info_from_google(token)
  
  if result == False:
    print 'googlesignin: failed to get info from google.'
    session.pop('signin_party', None)
    return 'False'
  
  user = User.get_by_id(idinfo['email'])
  
  if user == None:
    print 'googlesingin: It is new user.'
    user = User()
    user.id = idinfo['email']
    user.first_name = idinfo['given_name']
    user.last_name = idinfo['family_name']
    user.add()
  else:
    print 'googlesingin: It is NOT new user.'
    user.id = idinfo['email']
    user.first_name = idinfo['given_name']
    user.last_name = idinfo['family_name']
    user.merge()
  print user.commit()
  
  session['user_id'] = user.id
  session['token'] = token
  session['signin_party'] = 'google'

  return 'True'

def check_signin():
  """Check user if signed in
  1. Verify with local permission logic
  2. Verify with 3rd party system
  """
  if verify_local_permission():
    return True
  else:
    print 'login_required: failed to verify with local permission.'
  
  #Check 3rd party auth
  result = get_info_from_google()[0]
  if result == False:
    print 'login_required: failed to verify with Google.'
  else:
    return True
  
  return False

def verify_local_permission():
  try:
    flask_sess_random_auth = session['random_auth']
  except KeyError:
    print 'login_required: random_auth is missed in flask session.'
    return False
  
  try:
    random_auth = request.cookies['random_auth']
  except KeyError:
    print 'login_required: random_auth is missed.'
    return False
  
  if flask_sess_random_auth == random_auth:
    return True
  else:
    return False
  #return hmac_compare_digest(flask_sess_random_auth, random_auth)

def get_info_from_google(token = None):
  try:
    if session['signin_party'] != 'google':
      print 'login_required: Do not verified by Google.'
      return False, {}
  except KeyError:
    print 'login_required: signin_party is missed.'
    return False, {}
  
  if token == None:
    try:
      token = session['token']
    except KeyError:
      print 'login_required: token is missed.'
      return False, {}
  
  try:
    idinfo = client.verify_id_token(token, config.CLIENT_ID)
    # If multiple clients access the backend server:
    #if idinfo['aud'] not in [ANDROID_CLIENT_ID, IOS_CLIENT_ID, WEB_CLIENT_ID]:
    #    raise crypt.AppIdentityError("Unrecognized client.")
    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise crypt.AppIdentityError("Wrong issuer.")
    #if idinfo['hd'] != APPS_DOMAIN_NAME:
    #    raise crypt.AppIdentityError("Wrong hosted domain.")
  except crypt.AppIdentityError as e:
      # Invalid token
      print e
      return False, {}
  
  return True, idinfo

def generate_csrf_token():
  print 'generate_csrf_token'
  if '_csrf_token' not in session:
    session['_csrf_token'] = ''.join(\
                                [random.choice(\
                                  string.ascii_letters + string.digits)\
                                  for n in xrange(16)])
  return session['_csrf_token']

def csrf_protect():
  print 'csrf_protect'
  print request.method
  
  if request.method == "POST":
    token = session.pop('_csrf_token', None)
    token_outside = request.form.get('_csrf_token')
    if token_outside == None:
      token_outside = request.args.get('_csrf_token')
    if not token or token != token_outside:
        abort(403)