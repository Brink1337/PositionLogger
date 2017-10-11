import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import tkinter
import pyfirmata
from pyfirmata import Arduino
import serial
import serial.tools.list_ports

import time
import os

class TopMenu(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super(TopMenu, self).__init__()
        self.parent = parent
        self.controller = controller
        self.menu = tk.Menu(self.parent)
        parent.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Select file", command=lambda: self.load_file(self.controller))

        self.options_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Options", menu=self.options_menu)
        self.options_menu.add_command(label="Connect", command=lambda: self.connect(self.controller))
        #self.options_menu.add_command(label="Reconnect", command=lambda: self.callback())
        self.options_menu.add_command(label="Help!", command=lambda: self.help_info())
        self.menu.add_command(label="exit", command=lambda: self.destroy_app(self.controller))

    def callback(self):
        print("dummy")

    def load_file(self, controller):
        self.file_path = tk.filedialog.askopenfilename(filetypes=(("Text files", "*.txt"),
                                                                  ("CSV files", "*.csv"),
                                                                  ("All files", "*.*")))
        if self.file_path:
            try:
                self.controller.variables["loaded_file_path"].set(self.file_path)  
                self.controller.variables["file_flag"].set(True)
                self.controller.variables["file_first_line"].set(True)
                
            except:
                tk.messagebox.showerror("Error", "Failed to open file")
            return

    def destroy_app(self, controller):
        self.controller = controller
        self.exit_dialog = tk.messagebox.askyesno("Exit", "Do you really want to quit?")
        if self.exit_dialog == 1:
            root.destroy()
            if self.controller.variables["connected"].get() == True:
                self.controller.arduino.exit()

    def connect(self, controller):
        self.controller = controller
        self.ard_port = ""
        self.arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if "Arduino" in p.description
            ]

        if not self.arduino_ports:
            self.no_arduino = tk.messagebox.showerror("Error","No Arduino Found...")
            self.controller.variables["connected"].set(False)

        if len(self.arduino_ports) > 1:
            warnings.warn("Multiple Arduinos found - Using first one")
            
        try:
            self.ard_port = str(self.arduino_ports[0])
            self.controller.arduino = Arduino(self.ard_port) #Connect to ard_port
            
            #start iterator that updates measurements from Arduino
            self.it = pyfirmata.util.Iterator(self.controller.arduino)
            self.it.start()
            
            #initialize Arduino Pins
            self.controller.analog_0 = self.controller.arduino.get_pin("a:0:i")
            self.controller.analog_1 = self.controller.arduino.get_pin("a:1:i")
            self.controller.analog_2 = self.controller.arduino.get_pin("a:2:i")
            self.controller.analog_3 = self.controller.arduino.get_pin("a:3:i")
            self.controller.analog_4 = self.controller.arduino.get_pin("a:4:i")
            self.controller.analog_5 = self.controller.arduino.get_pin("a:5:i")
            
            if len(self.arduino_ports) > 0:
                self.connected_to = tk.messagebox.showinfo("Info","Connected to " + self.ard_port) #messagebox.function(title, message[, options])
                self.controller.variables["connected"].set(True)

        except:
            if len(self.ard_port) > 1:
                self.already_connected = tk.messagebox.showerror("Error","Already connected to " + self.ard_port)
            
    def help_info(self):
        tk.messagebox.showinfo("Help", "Have you tried turning it off and on again?")
        
class ChannelFrame(tk.Frame):    
    def __init__(self, parent, ch, controller, *args, **kwargs):
        self. parent = parent
        self.controller = controller
        self.ch = ch
        self.actual_ch = str(ch+1)

        super(ChannelFrame, self).__init__()
        self.frame = tk.Frame(self.parent)
        
        """ Border, Title, Enable"""
        self.channel_border = tk.LabelFrame(self, text=None,
                                            padx=0, pady=0)
        self.channel_border.grid(sticky=tk.N + tk.W,
                                 padx=5, pady=5)

        self.active_ch_label = tk.Label(self.channel_border, text="Channel " + self.actual_ch)
        self.active_ch_label.grid(row=0, column=0, padx=0, pady=0)

        self.channel_enable = tk.Checkbutton(self.channel_border, text=": ON/OFF", variable=self.controller.ch_enable[self.ch])
        self.channel_enable.grid(row=0, column=1, padx=0, pady=0)
        print(self.controller.ch_enable[self.ch].get())
        
        """ Position labels """
        self.channel_pos_mm = tk.Label(self.channel_border, textvariable=self.controller.ch_pos_mm[self.ch],
                                          bg="white", fg="black", relief=tk.SUNKEN, width=10)
        self.channel_pos_mm.grid(row=1, column=1,
                                    padx=2, pady=5)
        
        self.channel_mm_label = tk.Label(self.channel_border, text="Position in mm:",
                                      width=16, anchor=tk.E)
        self.channel_mm_label.grid(row=1, column=0,
                                padx=0, pady=5)

        self.channel_pos_adc = tk.Label(self.channel_border, textvariable=self.controller.filter_ch_pos_adc[self.ch],
                                          bg="white", fg="black", relief=tk.SUNKEN, width=10)
        self.channel_pos_adc.grid(row=2, column=1,
                                    padx=2, pady=5)
        
        self.channel_adc_label = tk.Label(self.channel_border, text="Position raw adc:",
                                      width=16, anchor=tk.E)
        self.channel_adc_label.grid(row=2, column=0,
                                padx=2, pady=5)


        """ Calibration """
        #max cal out
        self.ch_max_out_temp = tk.IntVar()
        self.max_cal_out = tk.Entry(self.channel_border, textvariable=self.ch_max_out_temp,
                                    relief=tk.SUNKEN, width=18)
        self.max_cal_out.grid(row=3, column=0,
                              padx=2, pady=0)
        self.max_cal_button = tk.Button(self.channel_border, text="MAX OUT", command=lambda: self.calibrate_max(self.ch, self.controller, self.ch_max_out_temp),
                                        width=10)
        self.max_cal_button.grid(row=3, column=1,
                                 padx=0, pady=0)
        
        #cal out
        self.cal_out = tk.Label(self.channel_border, textvariable=self.controller.ch_cal_out[self.ch],
                                bg="white", fg="black", relief=tk.SUNKEN, width=16)
        self.cal_out.grid(row=4, column=0,
                            padx=2, pady=0)

        self.cal_out_button = tk.Button(self.channel_border, text="CAL OUT", command=lambda: self.calibrate_out(self.ch, self.controller),
                                        width=10)
        self.cal_out_button.grid(row=4, column=1,
                                padx=0, pady=0)

        #cal in
        self.cal_in = tk.Label(self.channel_border, textvariable=self.controller.ch_cal_in[self.ch],
                                bg="white", fg="black", relief=tk.SUNKEN, width=16)
        self.cal_in.grid(row=5, column=0,
                            padx=2, pady=0)

        self.cal_in_button = tk.Button(self.channel_border, text="CAL IN", command=lambda: self.calibrate_in(self.ch, self.controller),
                                       width=10)
        self.cal_in_button.grid(row=5, column=1,
                                padx=0, pady=0)

        
    """ calibration logic """
    def calibrate_max(self, ch, controller, entry):
        self.controller = controller
        self.ch = ch
        self.entry_val = entry

        try:
            self.controller.ch_max_out[self.ch].set(self.entry_val.get())
            
        except:
            self.non_integer = tk.messagebox.showerror("Error", "Non-integer input")
        
        
        
        
    def calibrate_in(self, ch, controller):
        self.controller = controller
        self.ch = ch
        self.controller.ch_cal_in[self.ch].set(self.controller.ch_pos_adc[self.ch].get())

        if self.controller.ch_cal_in[self.ch].get() == self.controller.ch_cal_out[self.ch].get():
            self.controller.ch_cal_in_flag[self.ch].set(False)
            self.not_same = tk.messagebox.showerror("Error", "Cal in == Cal out")
            if self.controller.variables["calc_in_prog"].get() == False:
                self.controller.ch_cal_in[self.ch].set(0)
                
        else:
            self.controller.ch_cal_in_flag[self.ch].set(True)
            
    def calibrate_out(self, ch, controller):
        self.controller = controller
        self.ch = ch
        self.controller.ch_cal_out[self.ch].set(self.controller.ch_pos_adc[self.ch].get())
        
        if self.controller.ch_cal_out[self.ch].get() == self.controller.ch_cal_in[self.ch].get():
            self.controller.ch_cal_out_flag[self.ch].set(False)
            self.not_same = tk.messagebox.showerror("Error", "Cal out == Cal in")
            if self.controller.variables["calc_in_prog"].get() == False:
                self.controller.ch_cal_out[self.ch].set(0)
                
        else:
            self.controller.ch_cal_out_flag[self.ch].set(True)



class PollLoop(tk.Frame):
    #PollLoop does as the name suggests, it polls for new data every 10mS
    #PollLoop also takes care of conversions from ADC to mm, and filtering.
    def __init__(self, controller, *args, **kwargs):
        self.controller = controller
        self.connected_var = self.controller.variables["connected"].get()
        
        if self.connected_var == True:
            self.arduino_data(self.controller)
        root.after(1, lambda: PollLoop(self.controller))

    def arduino_data(self, controller):
        self.controller = controller
        #For a short period of time after connecting to Arduino, None values will be returned.
        #to avoid None values affecting measurements, wait until None is no longer received.
        while self.controller.analog_0.read() is None:
            pass
        
        for x in range(self.controller.variables["total_actuators"].get()):
            if self.controller.ch_enable[x].get() == True:
                #read current channel
                self.controller.ch_pos_adc[x].set(self.current_ch(self.controller, x))
                #filter reading
                self.controller.filter_ch_pos_adc[x].set(round(self.analog_filter(self.controller, x), 2))
                #print(self.controller.ch_pos_adc[x].get())
                self.controller.ch_pos_mm[x].set(self.pos_conversion(self.controller, x))
        
    #Python doesn't have switch case, this is somewhat equivalent.
    def current_ch(self, controller, ch):
        self.controller = controller
        self.ch = ch
        return_val = 0
        if self.ch == 0:
            self.return_val = self.controller.analog_0.read()
        if self.ch == 1:
            self.return_val = self.controller.analog_1.read()
        if self.ch == 2:
            self.return_val = self.controller.analog_2.read()
        if self.ch == 3:
            self.return_val = self.controller.analog_3.read()
        if self.ch == 4:
            self.return_val = self.controller.analog_4.read()
        if self.ch == 5:
            self.return_val = self.controller.analog_5.read()
            
        return (self.return_val * self.controller.variables["adc_res"].get())


    #Filter equation: ADC_OLD = (ADC_OLD * (N - 1) + ADC_NEW) / N   
    def analog_filter(self, controller, ch):
        self.controller = controller
        self.ch = ch
        self.n = self.controller.variables["filter_factor"].get()
        self.adc_old = self.controller.filter_ch_pos_adc[self.ch].get()
        self.adc_new = self.controller.ch_pos_adc[self.ch].get()
        
        self.adc_old = ((self.adc_old * (self.n - 1)) + self.adc_new) / self.n
        #print(self.adc_old)
        return self.adc_old

    #Conversion from ADC to Position in mm
    #Displays which parameters are needed if they haven't been entered.
    def pos_conversion(self, controller, ch):
        self.controller = controller
        self.v_res = self.controller.variables["vcc"].get() / self.controller.variables["adc_res"].get()
        self.ch = ch
        self.cal_flag = 0
        
        if self.controller.ch_cal_in[self.ch].get() != False:
            if self.controller.ch_cal_out[self.ch].get() != False:
                if self.controller.ch_max_out[self.ch].get() != False:
                    if self.controller.ch_cal_in_flag[self.ch].get() & self.controller.ch_cal_out_flag[self.ch].get() != False:
                        self.controller.variables["calc_in_prog"].set(True)
                        self.cal_diff = (self.controller.ch_cal_in[self.ch].get() - self.controller.ch_cal_out[self.ch].get())*self.v_res
                        self.cal_diff_res = self.cal_diff / self.controller.ch_max_out[self.ch].get()
                        self.pot_length = (self.controller.ch_cal_in[self.ch].get() * self.v_res) / self.cal_diff_res
                        self.pos_in_mm = self.pot_length - ((self.controller.ch_pos_adc[self.ch].get() * self.v_res) / self.cal_diff_res)
                        self.controller.variables["calc_in_prog"].set(False)
                        self.pos_in_mm = round(float(self.pos_in_mm), 2)
                
                
        if self.controller.ch_cal_in_flag[self.ch].get() == False:
           if self.controller.ch_cal_out_flag[self.ch].get() == False:
               self.pos_in_mm = "CAL in & out"
                
        if  self.controller.ch_cal_out_flag[self.ch].get() == True:
            if self.controller.ch_cal_in_flag[self.ch].get() == False:
                self.pos_in_mm = "CAL in"
                
        if self.controller.ch_cal_in_flag[self.ch].get() == True:
            if self.controller.ch_cal_out_flag[self.ch].get() == False:
                self.pos_in_mm = "CAL out"

        if self.controller.ch_max_out[self.ch].get() == False:
            self.pos_in_mm = "Enter Max"

        return self.pos_in_mm

        
class WriteFileLoop(tk.Frame):
    #WriteFileLoop initiates with GUI.
    #When file is selected from file menu, WriteFileLoop will write actuator position to selected for every 10ms.
    #
    def __init__(self, controller, *args, **kwargs):
        self.controller = controller
        self.i = 0
        try:
            if self.controller.variables["file_flag"].get() == True:
                with open(self.controller.variables["loaded_file_path"].get(), "a+") as self.file:
                    for self.ch in range(self.controller.variables["total_actuators"].get()):
                        if self.controller.variables["file_first_line"].get() == True:
                            self.file.write("ch1;ch2;ch3;ch4;ch5;ch6; \n")
                            self.controller.variables["file_first_line"].set(False)
                            
                        if self.controller.ch_enable[self.ch].get() == True:
                            self.file.write(str(self.controller.ch_pos_mm[self.ch].get()))
                            #self.file.write(str(self.ch)) #Debugging purposes
                        self.i = self.i + 1
                        self.file.write(";")
                        if self.i == (self.controller.variables["total_actuators"].get()):
                                self.file.write("\n")
                                
        except:
            self.controller.variables["file_flag"].set(False)
            tk.messagebox.showerror("Error", "Error during file handling")
            
        root.after(10, lambda: WriteFileLoop(self.controller))


                  
class MainApplication(tk.Frame):
    #MainApplication is used to initialize each component of the GUI and shared variables.
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        tk.Frame.__init__(self, self.parent, *args, **kwargs)
        self.arduino = None
        self.analog_0 = None
        self.analog_1 = None
        self.analog_2 = None
        self.analog_3 = None
        self.analog_4 = None
        self.analog_5 = None
        
        #self.cur_ch = 0
        self.variables = {
            "vcc": tk.IntVar(),
            "adc_res": tk.IntVar(),
            "connected": tk.BooleanVar(),
            "total_actuators": tk.IntVar(),
            "filter_factor": tk.IntVar(),
            "calc_in_prog": tk.BooleanVar(),
            "file_flag": tk.BooleanVar(),
            "loaded_file_path": tk.StringVar(),
            "file_first_line": tk.BooleanVar(),
            }

        self.variables["filter_factor"].set(12)
        self.variables["total_actuators"].set(6) #max actuator count = 6
        self.variables["vcc"].set(5)
        self.variables["adc_res"].set(1024)
        self.variables["connected"].set(False)
        
        #Index 0 = CH1, 1 = CH2...
        self.ch_enable = [tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()]
        self.ch_max_out = [tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()]
        self.ch_pos_mm = [tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()]
        self.ch_pos_adc = [tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()]
        self.filter_ch_pos_adc = [tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()]
        self.ch_cal_in = [tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()]
        self.ch_cal_out = [tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar(), tk.DoubleVar()]
        self.ch_cal_in_flag = [tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()]
        self.ch_cal_out_flag = [tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()]

        
        self.parent.protocol('WM_DELETE_WINDOW', lambda: TopMenu.destroy_app(tk.Frame, self))
        #parent.geometry("440x200")
        self.parent.resizable(0,0)
        self.parent.title("Actuator Logger")

        self.poll_loop = PollLoop(self)
        self.file_append = WriteFileLoop(self)

        self.top_menu = TopMenu(self.parent, self)
        self.top_menu.grid(sticky=tk.N, padx=0, pady=0)
        
        for f in range(self.variables["total_actuators"].get()):
            self.channel_frame = ChannelFrame(self.parent, f, self)
            self.channel_frame.grid(row=0, column=f, padx=0, pady=0)

        #self.channel_frame1 = ChannelFrame(self.parent, self.cur_ch, self)
        #self.channel_frame1.grid(row=0, column=0, padx=0, pady=0)

        #self.channel_frame2 = ChannelFrame(self.parent, self.cur_ch+1, self)
        #self.channel_frame2.grid(row=0, column=1, padx=0, pady=0)







if __name__ == "__main__":
    
    root = tk.Tk()
    gui = MainApplication(root)
    root.mainloop()

