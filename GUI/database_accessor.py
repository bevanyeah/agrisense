import sqlite3


class DatabaseAccessor:
    def __init__(self):

        self.connection = None
        self.cursor = None
        self.connected = False


    def connect(self):

        if not self.connected:
            self.connection = sqlite3.connect('database.db')
            self.cursor = self.connection.cursor()
            self.cursor.execute('PRAGMA journal_mode=wal')
            self.connected = True

    def commit(self):

        if self.connected:
            self.connection.commit()

    def close_database(self):
        if self.connected:
            self.connection.close()
            self.connected = False



    def insert_event(self, event):

        self.connect()
        try:
            self.cursor.execute("INSERT INTO Events (event_sensor_id, event_timestamp,"
                                " event_status, event_description)"
                                " VALUES (?,?,?,?);",
                                (int(event['sensor_id']),
                                 int(event['properties']['timestamp']),
                                 int(event['properties']['confidence']),
                                 event['sensor_type']))
            self.commit()
        except:
            print("malformed data - not inserting into database")

    def modify_sensor(self, heartbeat):

        self.connect()

        try:

            self.cursor.execute("UPDATE Sensors SET sensor_lat =?,"
                                " sensor_long =?,"
                                " sensor_time=?,"
                                " sensor_type=? WHERE sensor_id = ?;",
                                (float(heartbeat['sensor_lat']),
                                 float(heartbeat['sensor_long']),
                                 int(heartbeat['properties']['timestamp']),
                                 heartbeat['sensor_type'],
                                 int(heartbeat['sensor_id'])))


            self.commit()
        except:
            print("malformed data - not inserting into database")

    def get_sensors(self):

        self.connect()

        list_sensors = list(self.cursor.execute('SELECT * FROM Sensors;'))

        return list_sensors

    def get_events(self):

        self.connect()

        list_events = list(self.cursor.execute('SELECT * FROM Events WHERE event_archive = 0;'))

        return [list(x) for x in list_events]


    def get_one_sensor(self, sensor_id):

        self.connect()

        list_events = list(self.cursor.execute('SELECT * FROM Events WHERE event_archive = 0 and event_sensor_id =?'
                                               ,(sensor_id,)))

        return [list(x) for x in list_events]

    def get_sensor_type(self, sensor_id):

        self.connect()

        sensor_type = list(self.cursor.execute('SELECT sensor_type FROM Sensors WHERE sensor_id = ? LIMIT 1'
                                               ,(sensor_id,)))

        return sensor_type

    def archive_this_sensor(self, sensor_id):

        self.connect()

        self.cursor.execute('UPDATE Events SET event_archive = 1 WHERE event_sensor_id = ?;', (sensor_id,))
        self.commit()

