# mediagoblin-lepturecaptcha -- a plugin for GNU MediaGoblin
# This program is based on, and adapted from, GNU MediaGoblin.
# Copyright (C) 2016 Andrew Browning.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import base64
import logging
import wtforms

from mediagoblin.init import ImproperlyConfigured
from mediagoblin.plugins.lepturecaptcha import forms as captcha_forms
from mediagoblin.plugins.lepturecaptcha import tools as captcha_tools
from mediagoblin.tools import pluginapi
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from captcha.image import ImageCaptcha
from hashlib import sha1
from random import choice

_log = logging.getLogger(__name__)
PLUGIN_DIR = os.path.dirname(__file__)


def setup_plugin():
    _log.info('Setting up lepturecaptcha...')

    config = pluginapi.get_config('mediagoblin.plugins.lepturecaptcha')
    if config:
        if config.get('CAPTCHA_SECRET_PHRASE') == 'changeme':
            configuration_error = 'You must configure the captcha secret phrase.'
            raise ImproperlyConfigured(configuration_error)

    pluginapi.register_template_path(os.path.join(PLUGIN_DIR, 'templates'))

    pluginapi.register_template_hooks(
        {'register_captcha': 'mediagoblin/plugins/lepturecaptcha/captcha_challenge.html'})

    # Create dummy request object to find register_form.
    environ = create_environ('/foo', 'http://localhost:8080/')
    request = Request(environ)
    register_form = pluginapi.hook_handle("auth_get_registration_form", request)
    del request

    # Add plugin-specific fields to register_form class.
    register_form_class = register_form.__class__
    register_form_class.captcha_response = captcha_forms.CaptchaStringField('CAPTCHA response', id='captcha_response', name='captcha_response')
    register_form_class.captcha_hash = wtforms.HiddenField('')
    register_form_class.remote_address = wtforms.HiddenField('')

    _log.info('Done setting up lepturecaptcha!')


def add_to_form_context(context):
    config = pluginapi.get_config('mediagoblin.plugins.lepturecaptcha')
    captcha_secret = config.get('CAPTCHA_SECRET_PHRASE')
    captcha_charset = config.get('CAPTCHA_CHARACTER_SET')
    captcha_length = config.get('CAPTCHA_LENGTH')

    captcha_string = u''.join([choice(captcha_charset) for n in xrange(captcha_length)])

    captcha_hash = sha1(captcha_secret + captcha_string).hexdigest()
    context['captcha_hash'] = captcha_hash

    image = ImageCaptcha()
    data = image.generate(captcha_string)
    captcha_image = base64.b64encode(data.getvalue())
    context['captcha_image'] = captcha_image

    return context


hooks = {
    'setup': setup_plugin,
    'auth_extra_validation': captcha_tools.extra_validation,
    ('mediagoblin.auth.register',
     'mediagoblin/auth/register.html'): add_to_form_context,
}
