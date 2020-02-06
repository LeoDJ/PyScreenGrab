import tkinter as tk
from tkinter import Canvas, Tk, Button
import os
import time
import threading
import sys

class CaptureTask(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.capture_running = True
        print("Capture Task started")
        self.start()

    def run(self):
        while self.capture_running:
            time.sleep(2)
            # print("foo", time.time())

    def stop(self):
        self.capture_running = False
    
    def handle_config_update(self, pos, size, output_size):
        # print(pos, size, output_size)
        pass

class SelectionWindow:
    def __init__(self, master, window_changed_callback=None, init_pos=None):
        self.master = master
        self.window_changed_callback = window_changed_callback
        self.master.title('Selection')
        if init_pos:
            self.master.geometry('{}x{}+{}+{}'.format(init_pos[0], init_pos[1], init_pos[2], init_pos[3]))
        self.previous_size = [self.master.winfo_width(), self.master.winfo_height()]
        self.keep_aspect = False
        self.ignore_own_resize = False
        self.last_event = 0
        # makes window content transparent
        if os.name == 'nt':  # Windows
            self.master.configure(background='purple')
            self.master.wm_attributes('-transparentcolor', 'purple')
        else:
            print("You're not running windows, transparency isn't implemented for other OSes yet.")
        self.canvas = Canvas(self.master, bg='purple', bd=2, relief='flat', highlightbackground='red')
        self.canvas.pack(fill='both', expand=1)
        self.master.bind('<Configure>', self.window_changed)
        self.master.bind('<Right>', self.move_window)
        self.master.bind('<Left>', self.move_window)
        self.master.bind('<Up>', self.move_window)
        self.master.bind('<Down>', self.move_window)
        self.master.bind('<Control-Right>', self.size_window)
        self.master.bind('<Control-Left>', self.size_window)
        self.master.bind('<Control-Up>', self.size_window)
        self.master.bind('<Control-Down>', self.size_window)

    def move_window(self, event):
        pos = [self.master.winfo_x(), self.master.winfo_y()]
        delta = 10 if event.state & 0x01 else 1 # move faster on shift
        if(event.keysym == 'Right'):
            pos[0] += delta
        elif(event.keysym == 'Left'):
            pos[0] -= delta
        elif(event.keysym == 'Down'):
            pos[1] += delta
        elif(event.keysym == 'Up'):
            pos[1] -= delta
        self.master.geometry("+{}+{}".format(pos[0], pos[1]))

    def size_window(self, event):
        size = [self.master.winfo_width(), self.master.winfo_height()]
        delta = 10 if event.state & 0x01 else 1 # move faster on shift
        if(event.keysym == 'Right'):
            size[0] += delta
        elif(event.keysym == 'Left'):
            size[0] -= delta
        elif(event.keysym == 'Down'):
            size[1] += delta
        elif(event.keysym == 'Up'):
            size[1] -= delta
        self.master.geometry("{}x{}".format(size[0], size[1]))

    def window_changed(self, event):
        if self.keep_aspect:
            delta_ms = (time.time() - self.last_event) * 1000
            print('[{:10.3f}] '.format(delta_ms), end=' ')
            self.last_event = time.time()
            size = [event.width, event.height]
            print(size, self.previous_size, self.ignore_own_resize, end=' ')
            if self.ignore_own_resize:
                self.ignore_own_resize = False
                print('')
                return
            if size != self.previous_size and delta_ms > 8:
                if size[0] != self.previous_size[0]: # only x, or x and y changed
                    size[1] = int(size[0] / self.aspect)
                elif size[1] != self.previous_size[1]: # only y changed
                    size[0] = int(size[1] * self.aspect)

                print('changed', end=' ')

                self.master.geometry("{}x{}".format(size[0], size[1]))
                self.previous_size = size
                self.ignore_own_resize = True
            print('')

        pos = [self.canvas.winfo_rootx() + 2, self.canvas.winfo_rooty() + 2]
        size = [self.canvas.winfo_width() - 4, self.canvas.winfo_height() - 4]
        window_pos = [self.master.winfo_width(), self.master.winfo_height(), self.master.winfo_x(), self.master.winfo_y()]
        # print(pos, size)
        self.window_changed_callback(pos, size, window_pos)

    def set_keep_aspect(self, keep_aspect, aspect):
        self.keep_aspect = keep_aspect
        self.aspect = aspect


class ConfigWindow:
    def __init__(self, master):
        self.master = master
        self.master.title('Screen Capture Settings')

        self.keep_aspect = tk.IntVar()
        self.keep_aspect.set(1)
        self.capture_window_pos = None

        self.root_selection_window = None
        self.btn_selection_window = tk.Button(self.master, text='Select area', command=self.open_selection_window)
        self.lbl_output_size = tk.Label(self.master, text='Output Size')
        self.entry_output_x = tk.Spinbox(self.master, from_=1, to=1000, width=5) # TODO: validator
        self.entry_output_y = tk.Spinbox(self.master, from_=1, to=1000, width=5)
        self.lbl_x = tk.Label(self.master, text='X')
        self.lbl_y = tk.Label(self.master, text='Y')
        self.lbl_capt_pos = tk.Label(self.master, text='Capture Position')
        self.lbl_capt_size = tk.Label(self.master, text='Capture Size')
        self.lbl_data_capt_pos = tk.Label(self.master, text='')
        self.lbl_data_capt_size = tk.Label(self.master, text='')
        self.chk_keep_aspect = tk.Checkbutton(self.master, text='Keep Aspect Ratio', variable=self.keep_aspect, command=self.click_chk_keep_aspect)
        

        self.lbl_x.grid                 (row=0,column=1)
        self.lbl_y.grid                 (row=0,column=2)
        self.lbl_output_size.grid       (row=1, column=0)
        self.entry_output_x.grid        (row=1, column=1)
        self.entry_output_y.grid        (row=1, column=2)
        self.lbl_capt_pos.grid          (row=2, column=0)
        self.lbl_capt_size.grid         (row=3, column=0)
        self.lbl_data_capt_pos.grid     (row=2, column=1, columnspan=2)
        self.lbl_data_capt_size.grid    (row=3, column=1, columnspan=2)
        
        self.btn_selection_window.grid(columnspan=3)
        self.chk_keep_aspect.grid(columnspan=3)

    def open_selection_window(self):
        # only open one selection window
        if not self.root_selection_window:
            self.root_selection_window = tk.Toplevel(self.master)
            self.root_selection_window.protocol('WM_DELETE_WINDOW', self.handle_selection_window_closed)
            self.selection_window = SelectionWindow(self.root_selection_window, self.handle_window_changed, self.capture_window_pos)
            self.click_chk_keep_aspect()
            self.start_capture_task()
        else:
            self.root_selection_window.lift()

    def start_capture_task(self):
        if not hasattr(self, 'capture_task'):
            self.capture_task = CaptureTask()

    def click_chk_keep_aspect(self):
        if hasattr(self, 'selection_window'):
            self.selection_window.set_keep_aspect(self.keep_aspect.get(), int(self.entry_output_x.get()) / int(self.entry_output_y.get()))

    def handle_selection_window_closed(self):
        self.root_selection_window.destroy()
        self.root_selection_window = None

    def handle_window_changed(self, pos, size, capture_window_pos = None):
        self.capture_window_pos = capture_window_pos
        self.lbl_data_capt_pos.config(text="{}x{}".format(pos[0], pos[1]))
        self.lbl_data_capt_size.config(text="{}x{}".format(size[0], size[1]))
        self.capture_task.handle_config_update(pos, size, (64, 64))

def main():
    root = tk.Tk()
    app = ConfigWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
