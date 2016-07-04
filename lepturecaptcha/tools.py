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
import base64
import logging

from mediagoblin import messages
from mediagoblin.tools import pluginapi
from mediagoblin.tools.translate import lazy_pass_to_ugettext as _

from hashlib import sha1

_log = logging.getLogger(__name__)


def captcha_challenge(request):
    config = pluginapi.get_config('mediagoblin.plugins.lepturecaptcha')
    captcha_secret = config.get('CAPTCHA_SECRET_PHRASE')

    captcha_challenge_passes = False

    captcha_hash = request.form['captcha_hash']
    captcha_response = request.form['captcha_response']
    remote_addr = request.remote_addr

    captcha_response_hash = sha1(captcha_secret + captcha_response).hexdigest()
    captcha_challenge_passes = (captcha_response_hash == captcha_hash)

    if not captcha_challenge_passes:
        _log.info('Failed registration attempt from %s', remote_addr)
        messages.add_message(
            request,
            messages.WARNING,
            _('Sorry, captcha was incorrect. Please try again.'))

    return captcha_challenge_passes