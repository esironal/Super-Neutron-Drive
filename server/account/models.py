import urllib
import datetime
from importlib import import_module

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

from ndrive.utils.lib import cached_method
from ndrive.utils.email import send_mail

import jwt

SESSION_ENGINE = import_module(settings.SESSION_ENGINE)

class User (AbstractBaseUser, PermissionsMixin):
  verified_email = models.EmailField('verified email address', null=True, blank=True)
  verified = models.BooleanField(default=False)
  newsletter = models.BooleanField('Subscribe to Newsletter', default=False)
  
  first_name = models.CharField('first name', max_length=30, blank=True)
  last_name = models.CharField('last name', max_length=30, blank=True)
  
  username = models.CharField('Username', max_length=30, unique=True,
        help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[
          validators.RegexValidator(r'^[\w.@+-]+$', 'Enter a valid username.', 'invalid')
        ])
  email = models.EmailField('E-Mail', unique=True)
  
  is_staff = models.BooleanField('staff status', default=False,
    help_text='Designates whether the user can log into this admin site.')
  is_active = models.BooleanField('active', default=True,
    help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
  date_joined = models.DateTimeField('date joined', default=timezone.now)
  
  USERNAME_FIELD = 'username'
  REQUIRED_FIELDS = ['email']
  
  objects = UserManager()
  
  def __unicode__ (self):
    return self.username
    
  def get_short_name (self):
    return self.username
    
  @staticmethod
  def autocomplete_search_fields():
    return ("id__iexact", "username__icontains", "email__icontains", "first_name__icontains", "last_name__icontains")
    
  def chrome_token (self, session):
    return jwt.encode({
      'session': session.session_key,
      'exp': datetime.datetime(2030, 1, 1)
    }, settings.SECRET_KEY)
    
  @staticmethod
  def get_session (token):
    payload = jwt.decode(token, settings.SECRET_KEY, verify_expiration=False)
    return SESSION_ENGINE.SessionStore(payload['session'])
    
  def send_verify (self, request):
    if self.email != self.verified_email:
      EmailVerify.new_verify(self, request)
      
  def send_pwreset (self, request):
    EmailVerify.new_verify(self, request, True)
    
class EmailVerify (models.Model):
  user = models.ForeignKey(User)
  email = models.EmailField()
  used = models.BooleanField(default=False)
  reset = models.BooleanField(default=False)
  
  created = models.DateTimeField(default=timezone.now)
  
  class Meta:
    verbose_name = 'E-Mail Verify'
    verbose_name_plural = 'E-Mail Verifies'
    
  def __unicode__ (self):
    return self.email
    
  def qs (self):
    return '?token={}&email={}'.format(self.token(), urllib.quote(self.email))
    
  @cached_method
  def token (self):
    return jwt.encode({'id': self.id, 'created': unicode(self.created)}, settings.SECRET_KEY)
    
  @staticmethod
  def new_verify (user, request, reset=False):
    verify = EmailVerify(user=user, email=user.email, reset=reset)
    verify.save()
    
    context = {'verify': verify, 'request': request}
    if reset:
      tpl = 'account/email.password-reset'
      send_mail('Password Reset - {site_name}', [verify.email], tpl, context)
      
    else:
      tpl = 'account/email.verify'
      send_mail('Please Verify Your E-Mail - {site_name}', [verify.email], tpl, context)
      
    return verify
    
  @staticmethod
  def verify_token (token, email, age=10, reset=False):
    payload = jwt.decode(token, settings.SECRET_KEY)
    
    old = timezone.now() - datetime.timedelta(days=age)
    verify = EmailVerify.objects.get(
      id=payload['id'],
      email=email,
      created__gte=old,
      used=False,
      reset=reset,
    )
    
    if not reset:
      verify.used = True
      verify.save()
      
    return verify
    