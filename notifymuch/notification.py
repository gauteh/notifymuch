import shlex
import subprocess
from gi.repository import Notify, Gio
from notifymuch import config
from notifymuch.messages import Messages


__all__ = ["show_notification"]


class NotifymuchNotification(Gio.Application):
    ICON = 'mail-unread-symbolic'

    def __init__(self):
        Gio.Application.__init__(
                self,
                application_id="net.wemakethings.Notifymuch")
        self.connect('startup', self.on_startup)
        self.connect('activate', self.on_activate)

    def on_startup(self, data):
        config.load()
        Notify.init('notifymuch')
        self.notification = Notify.Notification.new('', '', self.ICON)
        self.notification.set_category('email.arrived')
        if config.get("mail_client"):
            self.notification.add_action(
                    'mail-client',
                    'Run mail client',
                    self.action_mail_client)
        self.notification.connect('closed', lambda e: self.quit())
        self.hold()

    def on_activate(self, data):
        config.load()  # Reload config on each update.
        messages = Messages()
        summary = messages.unseen_summary()
        if summary == "":
            self.release()
        else:
            self.notification.update(
                    summary="{count} unread messages".format(
                        count=messages.count()),
                    body=summary,
                    icon=self.ICON)
            self.notification.show()

    def action_mail_client(self, action, data):
        self.release()
        subprocess.Popen(shlex.split(config.get("mail_client")))


def show_notification():
    """If a notification is open already, asks it to update itself and returns
    immediately. Otherwise opens a notification and blocks until it is
    closed."""
    NotifymuchNotification().run()
