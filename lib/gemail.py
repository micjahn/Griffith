# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2007 Vasco Nunes

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import socket
import smtplib
import gutils
import gettext
gettext.install('griffith', unicode=1)

socket.setdefaulttimeout(10)

def mailto(self, tls, port, server, auth, user, password, sender, to, subject, msg):
    """
    sends an email
    """
    try:
        session = smtplib.SMTP(server, port)
        session.set_debuglevel(1)
    except socket.timeout:
        gutils.error(self, _("Connection timed out"), \
            self.widgets['window'])
        return()
    if tls == True:
        session.ehlo()
        session.starttls()
        session.ehlo()
    if auth:
        try:
            session.login(user, password)
        except:
            gutils.error(self, _("Error sending e-mail: %s")%_("login failure"), \
                self.widgets['window'])
            return
    headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" \
        % (sender, to, subject)
    try:
        smtpresult = session.sendmail(sender, to, headers+msg)
        gutils.info(_("E-mail sent sucessfuly"), self.widgets['window'])
        return
    except:
        gutils.error(self, _("Error sending e-mail: %s")%"", self.widgets['window'])
        
    session.quit()

def send_email(self):
    if len(self.person_email):
        if self.config.get('use_auth', False, section='mail') == True:
            use_auth = 1
        else:
            use_auth = 0
        try:
            mailto(self, self.config.get('mail_use_tls', False, section='mail'), \
                self.config.get('mail_smtp_port', '25', section='mail'), \
                self.config.get('smtp_server', 'localhost', section='mail'), \
                use_auth, self.config.get('username', '', section='mail'), \
                self.config.get('password', '', section='mail'), \
                self.config.get('email', 'griffith', section='mail'), self.person_email, \
                _("Movie loan reminder"), _("Hi, %s!\n\nJust to remind you " + \
                "that I'm really needing the following movie I have loaned to you " + \
                "recently:\n\n%s (%s)\n\nLoaned on %s") \
                %(self.person_name, self.widgets['movie']['o_title'].get_text(), \
                self.widgets['movie']['title'].get_text(), self.loan_date[:10]))
        except:
            gutils.error(self, _("Mail could not be sent. Please check e-mail preferences."), self.widgets['window'])
    else:
        gutils.info(_("This person has no e-mail address defined."), \
            self.widgets['window'])
