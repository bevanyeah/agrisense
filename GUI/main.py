

import multiprocessing

import customtkinter

import Gui
from database_accessor import DatabaseAccessor
from client_mqtt import ClientMqtt
import os, sys




if __name__ == '__main__':

    if os.environ.get('DISPLAY', '') == '':
        # print('no display found. Using :0.0')
        os.environ.__setitem__('DISPLAY', ':0.0')



    database_accessor = DatabaseAccessor()

    client = ClientMqtt(database_accessor)

    client_logger = multiprocessing.Process(target=client.log_worker, args=(), daemon=True, name="MQTTLogProcess")
    client_logger.start()

    database_accessor.connect()

    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("blue")

    gui = Gui.App(database_accessor)
    gui.bind("<Configure>", Gui.gui_on_configure)

    gui.protocol("WM_DELETE_WINDOW", gui.OnClose)
    gui.mainloop()

    client_logger.terminate()

