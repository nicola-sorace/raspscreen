from . import core

class Main_Menu(core.Menu):
    title = "Main Menu"
    items = ["Utility", "Security", "Data", "Entertain", "Admin", "Settings"]
    
    def run(self, n):
        super().run(n)
        it = self.items[n]

        if it=="Utility": self.set_view(Utility_Menu)
        elif it=="Admin": self.set_view(Admin_Menu)
        elif it=="Settings": self.set_view(Settings_Menu)

class Utility_Menu(core.Menu):
    title = "Utilities"
    items = [" <-", "Timer", "Counter"]
    
    def run(self, n):
        from . import applets
        super().run(n)
        it = self.items[n]

        if it=="Timer": self.set_view(applets.Timer)

class Admin_Menu(core.Menu):
    title = "Admin tools"
    items = [" <-", "Execute command", "Check network", "Shutdown", "Reboot"]

    cmd = [""]

    def on_open(self):
        super().on_open()
        if self.cmd != [""]:
            cmd = self.cmd[0]
            self.cmd = [""]
            self.set_view(core.CMD_View, s=cmd)

    def run(self, n):
        super().run(n)
        it = self.items[n]

        if it=="Execute command":
            self.cmd = [""]
            self.set_view(core.Input_View, name="Shell command", ref=self.cmd)
        elif it=="Check network": self.set_view(core.CMD_View, s="ping 8.8.4.4")
        elif it=="Shutdown": self.set_view(core.CMD_View, s="shutdown -h 0")
        elif it=="Reboot": self.set_view(core.CMD_View, s="shutdown -r 0")


class Settings_Menu(core.Menu):
    title = "Settings"
    items = [" <-", "WIFI", "Bluetooth", "Display"]

    def run(self, n):
        from . import wifi
        super(Settings_Menu, self).run(n)
        it = self.items[n]

        if it=="WIFI": self.set_view(wifi.WIFI) 

