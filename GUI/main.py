
import multiprocessing

import customtkinter

import Gui
from database_accessor import DatabaseAccessor
from client_mqtt import ClientMqtt
import os, sys




if __name__ == '__main__':

    # Used for Launching application when executed from command line

    if os.environ.get('DISPLAY', '') == '':
        print('no display found. Using :0.0')
        os.environ.__setitem__('DISPLAY', ':0.0')



    # Create an instance of the database accessor to pass to each of the processes
    database_accessor = DatabaseAccessor()

    # Create our client process, used for MQTT access and database write operations
    client = ClientMqtt(database_accessor)

    # Spawn the process as a deamon (i.e repeat forever)
    client_logger = multiprocessing.Process(target=client.log_worker, args=(), daemon=True, name="MQTTLogProcess")
    client_logger.start()

    # Connect to the database back in this parent process
    database_accessor.connect()

    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("blue")

    gui = Gui.App(database_accessor)
    gui.bind("<Configure>", Gui.gui_on_configure)

    gui.protocol("WM_DELETE_WINDOW", gui.OnClose)
    gui.mainloop()

    # On ending of gui loop, terminate the program
    client_logger.terminate()

