import tkinter as tk
import tkinter.messagebox
import tkinter
import pyfirmata
from pyfirmata import Arduino
import serial
import serial.tools.list_ports

import time
import os

       
    
class ConnectTest(tk.Frame):
    dummy = "dummy"

class TopMenu(tk.Frame):
    def __init__(self, parent):
        super(TopMenu, self).__init__()
        self.menu = tk.Menu(parent)
        parent.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save As", command=self.callback)

        self.options_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Options", menu=self.options_menu)
        self.options_menu.add_command(label="Connect", command=lambda: self.connect())
        self.options_menu.add_command(label="Test Connection", command=lambda: self.callback())
        self.options_menu.add_command(label="Help!", command=lambda: self.help_info())
        self.menu.add_command(label="exit", command=self.destroy_app)

    def callback(self):
        print("dummy")

    def destroy_app(self):
        self.exit_dialog = tk.messagebox.askyesno("Exit", "Do you really want to quit?")
        if self.exit_dialog == 1:
            root.destroy()

    def connect(self):
        open_check = False
        ard_port = ""
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if "Arduino" in p.description
            ]

        if not arduino_ports:
            raise IOError("No Arduino Found...")

        if len(arduino_ports) > 1:
            warnings.warn("Multiple Arduinos found - Using first one")
            
        try:
            ard_port = str(arduino_ports[0])
            arduino = Arduino(ard_port)
            if len(arduino_ports) > 0:
                tk.messagebox.showinfo("","Connected to " + ard_port) #messagebox.function(title, message[, options])
        except:
            tk.messagebox.showerror("","Already connected to " + ard_port)
    def help_info(self):
        tk.messagebox.showinfo("","Have you tried turning it off and on again?")
        
class ChannelFrame(tk.Frame):
    def __init__(self, parent, ch):
        self.ch = ch
        self.ch_pos_mm = [0]*6
        self.new_ch_pos_adc = [0]*6
        self.old_ch_pos_adc = [0]*6
        self.adc_res = 1024
        self.vcc = 5
        
        self.display_ch_pos_mm = tk.StringVar()#Tkinter variable must be of type: IntVar, StringVar, DoubleVar, BoolVar()
        self.display_ch_pos_mm.set(self.ch_pos_mm[self.ch])#to manipulate Tkinter variable use .set() / .get()
        self.display_new_ch_pos_adc = tk.StringVar()
        self.display_new_ch_pos_adc.set(self.new_ch_pos_adc[self.ch])
        

        super(ChannelFrame, self).__init__()
        self.frame = tk.Frame(parent)

        self.channel_border = tk.LabelFrame(self, text=None,
                                            padx=0, pady=0)
        self.channel_border.grid(sticky=tk.N + tk.W,
                                 padx=5, pady=5)

        self.channel_pos_mm = tk.Label(self.channel_border, textvariable=self.display_ch_pos_mm,
                                          bg="white", fg="black", relief=tk.SUNKEN, width=10)
        self.channel_pos_mm.grid(row=0, column=1,
                                    padx=2, pady=5)
        
        self.channel_mm_label = tk.Label(self.channel_border, text="Position in mm:",
                                      width=16, anchor=tk.E)
        self.channel_mm_label.grid(row=0, column=0,
                                padx=0, pady=5)

        self.channel_pos_adc = tk.Label(self.channel_border, textvariable=self.display_new_ch_pos_adc,
                                          bg="white", fg="black", relief=tk.SUNKEN, width=10)
        self.channel_pos_adc.grid(row=1, column=1,
                                    padx=2, pady=5)
        
        self.channel_adc_label = tk.Label(self.channel_border, text="Position raw adc:",
                                      width=16, anchor=tk.E)
        self.channel_adc_label.grid(row=1, column=0,
                                padx=2, pady=5)
        
        self.tbutton = tk.Button(self.channel_border, text="test", command=lambda: self.arduino_logic())
        self.tbutton.grid(row=2)

    def arduino_logic(self):
        self.new_ch_pos_adc[self.ch] = self.new_ch_pos_adc[self.ch] + 1
        self.ch_pos_mm[self.ch] = self.ch_pos_mm[self.ch] + 1
        self.display_ch_pos_mm.set(self.ch_pos_mm[self.ch])
        self.display_new_ch_pos_adc.set(self.new_ch_pos_adc[self.ch])
        root.after(100, self.arduino_logic)
        
class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.cur_ch = 0
        parent.geometry("500x400")
        parent.resizable(0,0)
        parent.title("Actuator Logger")
        
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.top_menu = TopMenu(parent)
        self.top_menu.grid(sticky=tk.N, padx=0, pady=0)

        self.channel_frame = ChannelFrame(parent, self.cur_ch)
        self.channel_frame.grid(sticky=tk.W+tk.N)
  
    

if __name__ == "__main__":
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', lambda: TopMenu.destroy_app(tk.Frame))
    gui = MainApplication(root)
    root.mainloop()

