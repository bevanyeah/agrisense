import customtkinter, tkinter
import time


"""
Popup class for the creation of a sensor node information panel
All data is populated from database for each sensor.  Main GUI tick will refresh individual components as needed.
"""
class pop_up(customtkinter.CTkFrame):
    def __init__(self, *args, name=None, type=None, events=None, database_accessor = None,  **kwargs):
        super().__init__(*args, **kwargs)

        self.database_accessor = database_accessor
        self.sensor_id = name
        self.events = events

        self.hidden = False

        # Top
        self.top = customtkinter.CTkFrame(self)
        self.top.grid(row=0, column=0, padx=5, pady=(5, 5), sticky="new")


        customtkinter.CTkLabel(self.top, text=f"Sensor:", anchor='w').grid(row=0, column=0, sticky="we")
        customtkinter.CTkLabel(self.top, text=f"{name}", anchor='w').grid(row=0, column=1, sticky="we")

        customtkinter.CTkLabel(self.top, text=f"Type:", anchor='w').grid(row=1, column=0, sticky="we")
        customtkinter.CTkLabel(self.top, text=f"{type}", anchor='w').grid(row=1, column=1, sticky="we")

        customtkinter.CTkButton(self.top, text= "➡", width=40, height=40, command=self.hide,font=customtkinter.CTkFont(family='Helvetica',size=26)).grid(row=0, column=2, sticky="e")
        self.top.columnconfigure((0,1,2),weight=1)


        # Middle
        self.mid = customtkinter.CTkFrame(self)
        self.mid.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="nesw")

        customtkinter.CTkLabel(self.mid, text=f"Current Events:", anchor='w').grid(row=0, column=0, sticky="we")
        self.number_events = customtkinter.CTkLabel(self.mid, text=f"{len(events)}", anchor='w', width=150)
        self.number_events.grid(row=0, column=1,padx=5, sticky="we")

        customtkinter.CTkLabel(self.mid, text=f"Most recent:", anchor='w').grid(row=1, column=0, sticky="we")
        if len(events) >0:
            self.most_recent = customtkinter.CTkLabel(self.mid, text=f"{time_diff(events[-1][2])}", anchor='w')
        else:
            self.most_recent = customtkinter.CTkLabel(self.mid, text=f"None", anchor='w')
        self.most_recent.grid(row=1, column=1,padx=5, sticky="w")

        customtkinter.CTkLabel(self.mid, text=f"List of events:", anchor='w').grid(row=2, column=0, sticky="w")
        self.event_list = customtkinter.CTkTextbox(self.mid,text_color="black", fg_color="#CACACA",
                                                font=customtkinter.CTkFont(family="Courier New", size=16), height=300)
        self.event_list.grid(row=3, column=0,columnspan=2, rowspan=2, padx=5, sticky="we")
        self.populate_event_list()

        # Bottom
        self.bottom = customtkinter.CTkFrame(self)
        self.bottom.grid(row=2, column=0, padx=5, pady=(0, 5),sticky='sew')

        customtkinter.CTkButton(self.bottom, text="Acknowledge all events", command=self.archive, anchor=tkinter.CENTER).grid(row=0, column=0)

        self.bottom.columnconfigure((0),weight=1)
        self.bottom.rowconfigure((0), weight=1)

        self.rowconfigure((2),weight=1)


    def hide(self):

        self.hidden = True
        self.destroy()

    def archive(self):

        self.database_accessor.archive_this_sensor(self.sensor_id)

    def populate_event_list(self, events=None):


        self.event_list.delete(1.0,tkinter.END)
        if events == None:
            events = self.events

        if len(events) > 0:
            self.most_recent.configure( text=f"{time_diff(events[-1][2])}")
            self.number_events.configure(text=f"{len(events)}")

        else:
            self.most_recent.configure( text= "None")
            self.number_events.configure( text= "None")

        for event in events:
            formatted_time = time.asctime( time.localtime(int(event[2])) )
            f_time = time_diff(int(event[2]))
            self.event_list.insert("0.0", f"{event[0]} | {f_time}\n")

    def populate_alert_list(self, events=None):

        pass


def time_diff(epoch_time):
    current_time = int(time.time())
    diff = current_time - epoch_time

    if diff < 60:
        return f"{int(diff)} seconds ago"
    elif diff < 3600:
        return f"{int(diff // 60)} minutes ago"
    elif diff < 86400:
        return f"{int(diff // 3600)} hours ago"
    elif diff < 604800:
        return f"{int(diff // 86400)} days ago"
    else:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(epoch_time))