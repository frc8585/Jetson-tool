from ntcore import NetworkTableInstance as NT
import time

class NetworkTables:
    def __init__(self):
        self.inst = NT.getDefault()

        self.table = self.inst.getTable("Jetson")
        self.test = self.inst.getBooleanTopic("/Jetson/test").publish()
        # start a NT4 client
        self.inst.startClient4("example client")
        # connect to a roboRIO with team number TEAM
        self.inst.setServerTeam(8585)
        # starting a DS client will try to get the roboRIO address from the DS application
        self.inst.startDSClient()
        # connect to a specific host/port
        self.inst.setServer("host", NT.kDefaultPort4)

        self.test.set(True)

        print("NetworkTables Initialized")




    def update_all(self):
        print("update_all")

    def update(self, title, value):
        self.table.putValue(title, value)