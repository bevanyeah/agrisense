import customtkinter, tkinter
import time

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

        # self.label = customtkinter.CTkLabel(self.top, text= f"Sensor: {name}",anchor='w')
        # self.label.grid(row=0, column=0, sticky="we")
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
        customtkinter.CTkLabel(self.mid, text=f"{len(events)}", anchor='w', width=150).grid(row=0, column=1,padx=5, sticky="we")

        customtkinter.CTkLabel(self.mid, text=f"Most recent:", anchor='w').grid(row=1, column=0, sticky="we")
        if len(events) >0:
            customtkinter.CTkLabel(self.mid, text=f"{time_diff(events[-1][2])}", anchor='w').grid(row=1, column=1,padx=5, sticky="w")
        else:
            customtkinter.CTkLabel(self.mid, text=f"None", anchor='w').grid(row=1, column=1,padx=5, sticky="w")

        customtkinter.CTkLabel(self.mid, text=f"List of events:", anchor='w').grid(row=2, column=0, sticky="w")
        self.event_list = customtkinter.CTkTextbox(self.mid,text_color="black", fg_color="#CACACA",
                                                font=customtkinter.CTkFont(family="Courier New", size=16), height=150)
        self.event_list.grid(row=3, column=0,columnspan=2, padx=5, sticky="we")
        self.populate_event_list()

        customtkinter.CTkLabel(self.mid, text=f"List of Alerts:", anchor='w').grid(row=4, column=0, sticky="w")
        self.alert_list = customtkinter.CTkTextbox(self.mid,text_color="black", fg_color="#CACACA",
                                                font=customtkinter.CTkFont(family="Courier New", size=16), height=150)
        self.alert_list.grid(row=5, column=0,columnspan=2, padx=5, sticky="we")
        self.mid.rowconfigure((3,5),weight=0)
        self.populate_alert_list()

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

        for event in events:
            formatted_time = time.asctime( time.localtime(int(event[2])) )
            f_time = time_diff(int(event[2]))
            self.event_list.insert("0.0", f"{event[0]} | {f_time}\n")

    def populate_alert_list(self, events=None):

        self.alert_list.delete(1.0,tkinter.END)
        if events == None:
            events = self.events

        for event in events:
            formatted_time = time.asctime( time.localtime(int(event[2])) )
            f_time = time_diff(int(event[2]))
            self.alert_list.insert("0.0", f"{event[0]} | {f_time}\n")

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