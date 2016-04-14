# Global Imports
import sys
from os.path import dirname
import os.path
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk
from gi.repository import Gdk, GObject
from time import sleep
import threading


# Add top level directory to import path
sys.path.append(
    os.path.abspath(os.path.join(dirname(dirname(__file__)), 'googlevoice')))

# Local Imports
from cli import send_message
from cli import get_sms

# This would typically be its own file
MENU_XML="""
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
      <attribute name="label" translatable="yes">Change label</attribute>
      <item>
        <attribute name="action">win.change_label</attribute>
        <attribute name="target">String 1</attribute>
        <attribute name="label" translatable="yes">String 1</attribute>
      </item>
      <item>
        <attribute name="action">win.change_label</attribute>
        <attribute name="target">String 2</attribute>
        <attribute name="label" translatable="yes">String 2</attribute>
      </item>
      <item>
        <attribute name="action">win.change_label</attribute>
        <attribute name="target">String 3</attribute>
        <attribute name="label" translatable="yes">String 3</attribute>
      </item>
    </section>
    <section>
      <item>
        <attribute name="action">win.maximize</attribute>
        <attribute name="label" translatable="yes">Maximize</attribute>
      </item>
    </section>
    <section>
      <item>
        <attribute name="action">app.about</attribute>
        <attribute name="label" translatable="yes">_About</attribute>
      </item>
      <item>
        <attribute name="action">app.quit</attribute>
        <attribute name="label" translatable="yes">_Quit</attribute>
        <attribute name="accel">&lt;Primary&gt;q</attribute>
    </item>
    </section>
  </menu>
</interface>
"""


class ConversationPage(Gtk.ScrolledWindow):
    """
    Create a single scrolled window containing a Gtk.TextView widget in
    which to display a conversation
    """

    def __init__(self, conversation):
        super().__init__()
        self.conversation = conversation
        self.number = self.conversation['number']
        self.conversation_id = self.conversation['id']
        print(self.number)

        # Add a textview to the window
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_hexpand(True)
        self.textview.set_vexpand(True)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textbuffer = self.textview.get_buffer()
        self.load_conversation()
        #self.textview.
        self.add(self.textview)
        self.show_all()

        # Start a thread which updates the conversation on the page
        thread = threading.Thread(target=self.update_conversation)
        thread.daemon = True
        thread.start()

    def load_conversation(self):
        """ Get a conversation list and load the conversation from the list into
        the text buffer """

        conversations_list = get_sms()
        for conversation in conversations_list:
            if conversation['id'] == self.conversation_id:
                self.conversation = conversation
                text = ''
                for message in self.conversation['messages']:
                    text = text + message['from'].strip(':') + ' (' + message['time'] + '): ' + message['text'] + '\n'
                self.textbuffer.set_text(text)

    def update_conversation(self):
        while True:
            GLib.idle_add(self.load_conversation)
            sleep(5)


class MessageNotebook(Gtk.Notebook):

    def __init__(self, parent):
        """ Create the notebook and popluate with conversations """

        super().__init__()
        self.parent = parent
        self.conversations_list = get_sms()

        # Make the notebook scrollable
        self.set_scrollable(True)
        self.connect('switch-page', self.on_switch_page)
        self.conversations_list = get_sms()

        # Populate the notebook with pages containing conversations
        for conversation in self.conversations_list:
            page = ConversationPage(conversation)
            self.append_page(page, Gtk.Label(conversation['number']))

        self.get_current_page
            
    def on_switch_page(self, page, page_num, user_data):
        """ When the the page in the notebook changes, change the active phone
        number so all texts sent go the the number listed in the window """
        
        #number = self.get_conversation_phone_number(self.get_current_page())
        self.parent.active_phone_number = page_num.number
        print(self.parent.active_phone_number)
        return self.get_current_page()

    def get_conversation_phone_number(self, page_num):
        conversation_phone_number = None
        conversation = self.conversations_list[page_num]
        conversation_phone_number = conversation['number']
        return conversation_phone_number


class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.active_phone_number = None

        # This will be in the windows group and have the "win" prefix
        max_action = Gio.SimpleAction.new_stateful("maximize", None,
                                           GLib.Variant.new_boolean(False))
        max_action.connect("change-state", self.on_maximize_toggle)
        self.add_action(max_action)

        # Keep it in sync with the actual state
        self.connect(
            "notify::is-maximized",
            lambda obj, pspec: max_action.set_state(
                GLib.Variant.new_boolean(obj.props.is_maximized)))

        # Create a grid in the main window to house widgets
        self.grid = Gtk.Grid()
        self.add(self.grid)

        # Create a notebook with a different page for each conversation
        self.notebook = MessageNotebook(self)
        self.grid.attach(self.notebook, 0, 0, 2, 1)

        # Add an entry bar that allows for the sending of texts
        self.entry = Gtk.Entry()
        self.entry.set_hexpand(True)
        self.grid.attach(self.entry, 0, 1, 1, 1)

        # Add a button to send the message to the current
        self.button = Gtk.Button.new_with_label("Send")
        self.button.connect("clicked", self.on_send_clicked)
        self.grid.attach(self.button, 1, 1, 1, 1)

        self.show_all()

    def on_send_clicked(self, button):
        send_message(
            text=self.entry.get_text(),
            phone_number=self.active_phone_number)
        self.entry.set_text('')

    def on_maximize_toggle(self, action, value):
        action.set_state(value)
        if value.get_boolean():
            self.maximize()
        else:
            self.unmaximize()

    def set_active_phone_number(self, number):
        self.active_phone_number = number


class gVoice(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.example.myapp",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        self.window = None

        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "Command line test", None)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        builder = Gtk.Builder.new_from_string(MENU_XML, -1)
        self.set_app_menu(builder.get_object("app-menu"))

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainWindow(application=self, title="gVoice")

        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()

        if options.contains("test"):
            # This is printed on the main instance
            print("Test argument recieved")

        self.activate()
        return 0

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.present()

    def on_quit(self, action, param):
        self.quit()

if __name__ == "__main__":
    GObject.threads_init()
    Gdk.threads_init()
    application = gVoice()
    application.run(sys.argv)

