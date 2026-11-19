#!/usr/bin/python3
"""A passive desktop notice, behind application windows and outside the taskbar."""
import os
import signal

# This image deliberately runs an X11 desktop.
os.environ['GDK_BACKEND'] = 'x11'

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib, Gtk  # noqa: E402


class Desktop(Gtk.Window):
    def __init__(self):
        super().__init__(title='Ahnenblatt Desktop')
        self.set_wmclass('ahnenblatt-desktop', 'AhnenblattDesktop')
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.set_decorated(False)
        self.set_accept_focus(False)
        self.set_focus_on_map(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_below(True)
        self.stick()
        self.connect('delete-event', lambda *_: True)

        locale = (os.environ.get('LC_ALL') or os.environ.get('LC_MESSAGES')
                  or os.environ.get('LANG') or 'en_US.UTF-8')
        german = locale.lower().split('_')[0].split('-')[0].split('.')[0] == 'de'
        lines = (
            ('Ahnenblatt',
             'Ahnenblatt startet automatisch.',
             'Nach dem Beenden wird die Anwendung nach wenigen Sekunden neu gestartet.',
             'Ein minimiertes Fenster können Sie über die Taskleiste wieder öffnen.')
            if german else
            ('Ahnenblatt',
             'Ahnenblatt starts automatically.',
             'After you close the application, it restarts within a few seconds.',
             'Use the taskbar to restore a minimized window.')
        )
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.set_margin_start(32)
        box.set_margin_end(32)
        for i, text in enumerate(lines):
            label = Gtk.Label(label=text)
            label.set_line_wrap(True)
            label.set_max_width_chars(65)
            label.set_justify(Gtk.Justification.CENTER)
            label.get_style_context().add_class('heading' if i == 0 else 'notice')
            if i == 3:
                label.get_style_context().add_class('muted')
            box.pack_start(label, False, False, 0)
        self.add(box)
        css = Gtk.CssProvider()
        css.load_from_data(b'''
            window { background-color: #183c35; }
            label { color: #e1eee0; font-family: sans-serif; }
            .heading { font-size: 36px; font-weight: bold; margin-bottom: 12px; }
            .notice { font-size: 18px; }
            .muted { color: #adc8bf; font-size: 15px; margin-top: 14px; }
        ''')
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), css,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.get_screen().connect('size-changed', self.fit_screen)
        self.fit_screen()

    def fit_screen(self, *_):
        screen = self.get_screen()
        self.move(0, 0)
        self.resize(screen.get_width(), screen.get_height())


def stop():
    Gtk.main_quit()
    return GLib.SOURCE_REMOVE


if __name__ == '__main__':
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, stop)
    desktop = Desktop()
    desktop.show_all()
    Gtk.main()
