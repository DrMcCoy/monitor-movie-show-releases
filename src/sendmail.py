"""! Sending email.
"""

# Monitor Movie and Show Releases - Monitor future movie and TV show releases
#
# Monitor Movie and Show Releases is the legal property of its developers,
# whose names can be found in the AUTHORS file distributed with this source
# distribution.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from email.message import EmailMessage
from smtplib import SMTP


class SendMail:  # pylint: disable=too-few-public-methods
    """! Sending email.
    """

    def __init__(self, host: str, port: int, sender: str) -> None:
        self._host = host
        self._port = port
        self._sender = sender

    def send(self, receiver: str, subject: str, body: str) -> None:
        """! Send an email.

        @param receiver  The address to which to send the email to.
        @param subject   The email subject.
        @param body      The email body.
        """

        msg = EmailMessage()
        msg.set_content(body)
        msg['From'] = self._sender
        msg['To'] = receiver
        msg['Subject'] = subject

        with SMTP(host=self._host, port=self._port) as smtp:
            smtp.send_message(msg)
