
import customtkinter
import tkintermapview
import numpy as np
import requests
import random

import pop_up

import time

from time import sleep


_USER_IFTTT_INTEGRATION = "https://maker.ifttt.com/trigger/agrisense_trigger/with/key/bduNa0WHavvVqxJ9weg7_W"
_MY_HOME_LAT = -35.425744225920766
_MY_HOME_LONG = 149.2362831623155
_FULLSCREEN = False


class App(customtkinter.CTk):

    def __init__(self, database_accessor):
        super().__init__()

        self.pop_up = None
        self.clicked_sensor = None

        self.database_update = False

        self.database_accessor = database_accessor

        self.title("AgriSense")
        self.minsize(1024, 600)


        self.attributes('-fullscreen', _FULLSCREEN)

        self.home_lat = _MY_HOME_LAT
        self.home_long = _MY_HOME_LONG

        self.configure(fg_color="black")
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0, weight=1)

        # Two frames (RH frame is created on sensor click)
        self.map = tkintermapview.TkinterMapView(self)
        self.map.grid(row=0, column=0, sticky='nsew')

        self.configure_map()

        self.list_of_sensors = [None] * 100
        self.list_of_markers = [None] * 100
        self.alert = False

        self.tick()


    def OnClose(self, *unused):

        self.quit()
        self.destroy()

    def configure_map(self):
        self.map.my_home = [self.home_lat, self.home_long]
        self.map.set_position(self.map.my_home[0], self.map.my_home[1])
        self.map.set_zoom(15)
        self.map.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=18)
    #

    def sensor_click(self, sensor=None):

        # Fetch all information about this sensor that you clicked on
        self.clicked_sensor = sensor

        # grab the event and sensor type info
        event_data = self.database_accessor.get_one_sensor(sensor.data)
        sensor_type = self.database_accessor.get_sensor_type(sensor.data)[0][0]

        #Create a new popup first, then destroy the old one after delay
        new_pop_up = pop_up.pop_up(self, name =sensor.data, type=sensor_type, events= event_data, database_accessor= self.database_accessor)
        new_pop_up.grid(row=0, column=1, sticky='sn')
        self.rowconfigure((0), weight=1)
        sleep(0.2)
        if self.pop_up != None:
            self.pop_up.hide()
        self.pop_up = new_pop_up

    def sensor_refresh(self, sensor):

        # Fetch all information about this sensor
        self.clicked_sensor = sensor
        event_data = self.database_accessor.get_one_sensor(sensor.data)
        self.pop_up.populate_event_list(event_data)


    def tick(self):

        # Iterate through list of sensors, and plot them on the map
        new_list_of_sensors = self.database_accessor.get_sensors()

        # Get a list of Events (all non-archived Events)
        list_of_events = self.database_accessor.get_events()

        no_alert = True
        send_message = False
        active = True
        gps_wrong = False
        for i, sensor in enumerate(new_list_of_sensors):

            # remove the sensor if plotted

            if self.list_of_markers[i] != None:
                self.list_of_markers[i].delete()

            #We can safely ignore this sensor is any values are None

            if sensor[5] != None:
                # Determine appearance of sensor (alert state, age)
                this_alert = False

                # determine location of the sensor

                if sensor[1] == None or sensor[1] == 0:
                    lat = self.home_lat + random.random()/1000
                    centre = "white"
                else:
                    lat = sensor[1]
                    centre = "#90EE90"

                if sensor[2] == None or sensor[2] == 0:
                    long = self.home_long + random.random()/1000
                    centre = "white"
                else:
                    long = sensor[2]
                    centre = "#90EE90"

                # if more than 0 events
                if len(list_of_events) > 0:

                    if sensor[0] in np.array(list_of_events)[:,1].astype(int):

                        # Alert, set master alert state and this_alert state
                        if not self.alert:
                            send_message = True
                        self.alert = True
                        this_alert = True
                        no_alert = False

                # is it grey? (long time since last message)

                if sensor[5] + 60 < time.time():
                    active = False
                    print(f"{sensor[0]} is stale")
                # is it blue? (gps or timestamp was 0)

                if sensor[6] == 1:
                    gps_wrong = True
                    print(f"{sensor[0]} has lost GPS")


                # replot
                if this_alert:
                    self.list_of_markers[i] = self.map.set_marker(lat,long, text=f"{sensor[0]}",
                                                                  marker_color_outside="red",
                                                                  marker_color_circle=centre,
                                                                  command=self.sensor_click,
                                                                  data=sensor[0])
                elif not active:

                    self.list_of_markers[i] = self.map.set_marker(lat, long, text=f"{sensor[0]}"
                                                                    , marker_color_outside = "grey"
                                                                    , marker_color_circle = centre,
                                                                  command=self.sensor_click,
                                                                  data=sensor[0])
                elif gps_wrong:
                    # set at home location

                    self.list_of_markers[i] = self.map.set_marker(lat, long, text=f"{sensor[0]}"
                                                                    , marker_color_outside = "aqua"
                                                                    , marker_color_circle = centre,
                                                                  command=self.sensor_click,
                                                                  data=sensor[0])

                else:
                    self.list_of_markers[i] = self.map.set_marker(lat,long, text=f"{sensor[0]}"
                                                                    , marker_color_outside = "green"
                                                                    , marker_color_circle = centre,
                                                                  command=self.sensor_click,
                                                                  data=sensor[0])

        #if we looked at all sensors and no alerts, we can reset the alert class property

        if no_alert:
            self.alert = False

        # If we've checked everything and we're in alert state, trigger the webhook
        if send_message:
            requests.post(_USER_IFTTT_INTEGRATION)

        #Refresh the pop up
        if self.pop_up != None and not self.pop_up.hidden:

            self.sensor_refresh(self.clicked_sensor)

        self.list_of_sensors = new_list_of_sensors

        self.after(5000,self.tick)




def gui_on_configure(e):

    if str(type(e.widget)) == "<class 'gui_class.App'>":
        sleep(0.015)