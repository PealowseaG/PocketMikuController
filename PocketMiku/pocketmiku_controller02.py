# python3
import tkinter as tk
from tkinter import ttk
#from tkinter.constants import FALSE, TRUE
import time
import threading, queue
import os, glob
import mido
from pocketmiku_data_set import reverb_set, chorus_set, variation_set, instrument_set
from mikucode_translate01 import mikucode_translate

# Constant Value
#  for GUI
FGCOLOR = 'spring green'
BGCOLOR = 'dim gray' # back ground color
BTNWIDTH = 3
SELWIDTH = 18
VALWIDTH = 6
DISPHIGHT = 3

LABELWIDTH = 6
DISPWIDTH = 18
DISPWIDTHN = 8
#  for GUI Select frame
MIDI_SELECT = 0
INSTRUMENT_SELECT = 1
LYRIC_SELECT = 2
#  for GUI Effect frame
REVERB_SELECT = 0
CHORUS_SELECT = 1
VARIATION_SELECT = 2
#  for midiout_state
MIDIOUT_EXIST = 0
NO_MIDIOUT = 1
#  for MIDIOUT channel
CHANNEL_MIKU = 0
CHANNEL_INST = 1
CHANNEL_DRUM = 9
#  for lyric_send
WAIT_SEND = 0.05
FORWARD_CHAR = 1
BACK_CHAR = -1
FORWARD_SKIP = 2
BACK_SKIP = -2
POST_LENGTH = 4
# Dictionary
mikucode_to_char = {0:"ア", 1:"イ", 2:"ウ", 3:"エ", 4:"オ", 5:"カ", 6:"キ", 7:"ク", 8:"ケ", 9:"コ",
            10:"ガ", 11:"ギ", 12:"グ", 13:"ゲ", 14:"ゴ", 15:"キャ", 16:"キュ", 17:"キョ", 18:"ギャ", 19:"ギュ",
            20:"ギョ", 21:"サ", 22:"スィ", 23:"ス", 24:"セ", 25:"ソ", 26:"ザ", 27:"ズィ", 28:"ズ", 29:"ゼ",
            30:"ゾ", 31:"シャ", 32:"シ", 33:"シュ", 34:"シェ", 35:"ショ", 36:"ジャ", 37:"ジ", 38:"ジュ", 39:"ジェ",
            40:"ジョ", 41:"タ", 42:"ティ", 43:"トゥ", 44:"テ", 45:"ト", 46:"ダ", 47:"ディ", 48:"ドゥ", 49:"デ",
            50:"ド", 51:"テュ", 52:"デュ", 53:"チャ", 54:"チ", 55:"チュ", 56:"チェ", 57:"チョ", 58:"ツァ", 59:"ツィ",
            60:"ツ", 61:"ツェ", 62:"ツォ", 63:"ナ", 64:"ニ", 65:"ヌ", 66:"ネ", 67:"ノ", 68:"ニャ", 69:"ニュ",
            70:"ニョ", 71:"ハ", 72:"ヒ", 73:"フ", 74:"ヘ", 75:"ホ", 76:"バ", 77:"ビ", 78:"ブ", 79:"ベ",
            80:"ボ", 81:"パ", 82:"ピ", 83:"プ", 84:"ペ", 85:"ポ", 86:"ヒャ", 87:"ヒュ", 88:"ヒョ", 89:"ビャ",
            90:"ビュ", 91:"ビョ", 92:"ピャ", 93:"ピュ", 94:"ピョ", 95:"ファ", 96:"フィ", 97:"フュ", 98:"フェ", 99:"フォ",
            100:"マ", 101:"ミ", 102:"ム", 103:"メ", 104:"モ", 105:"ミャ", 106:"ミュ", 107:"ミョ", 108:"ヤ", 109:"ユ",
            110:"ヨ", 111:"ラ", 112:"リ", 113:"ル", 114:"レ", 115:"ロ", 116:"リャ", 117:"リュ", 118:"リョ", 119:"ワ",
            120:"ウィ", 121:"ウェ", 122:"ヲ", 123:"ン", 124:"ン", 125:"ン", 126:"ン", 127:"ン"}

# set threading control
lock_port = threading.Lock()
el = threading.Event()  # for pause for lyric_send
e1 = threading.Event()  # for quit lyric_send
q_lyrcnt = queue.Queue()
q_lyrpos = queue.Queue()
 
## base
def main_basement(e):
    #  Cycilc operation
    # polling
    while not e.isSet():
        # polling interval
        time.sleep(0.05)
        #display lyric
        if not q_lyrpos.empty():
            present_lyric = q_lyrpos.get()
            lyric_display(present_lyric)
            if channel_out != CHANNEL_MIKU:
                v_lyric.set('')
# lyric display
def lyric_display(present_lyric):
    # get lyric present position
    #if not q_lyrpos.empty():
    #    present_lyric = q_lyrpos.get()
    lyric_code = present_lyric[0]
    present_line = present_lyric[1]
    present_column = present_lyric[2]
    # initialize
    lyric_str = ''
    #lyric_forward = []
    lyric_backward = []
    lyric_size = [len(v) for v in lyric_code]
    # get backward lyric
    lyric_line = present_line
    lyric_column = present_column
    i = 0
    while i < POST_LENGTH:
        if lyric_column <= 0:  # when top of line
            if lyric_line <= 0:  # back line
                lyric_line = len(lyric_size) - 1
            else:
                lyric_line -= 1
            lyric_column = lyric_size[lyric_line] - 1  # set end of backed line
        else:
            lyric_column -= 1
        lyric_backward.append(mikucode_to_char[lyric_code[lyric_line][lyric_column]])
        i += 1
    i = POST_LENGTH - 1
    while i >= 0:
        lyric_str += lyric_backward[i]
        i -= 1
    # add present position
    lyric_str += '[' + mikucode_to_char[lyric_code[present_line][present_column]] + ']'
    # get forward lyric
    lyric_line = present_line
    lyric_column = present_column
    i = 0
    while i < POST_LENGTH:
        lyric_column += 1
        if lyric_column >= lyric_size[lyric_line]:
            lyric_column = 0
            lyric_line += 1
            if lyric_line >= len(lyric_size):
                lyric_line = 0
        lyric_str += mikucode_to_char[lyric_code[lyric_line][lyric_column]]
        i += 1
    #print(lyric_str)    # for debug
    v_lyric.set(lyric_str)
    #return lyric_str
## call back
def midi_exchange(message):
    msgtx = message.copy(channel = channel_out)
    # send midi message
    lock_port.acquire()
    outport.send(msgtx)
    lock_port.release() 
    if msgtx.type == 'note_on' and channel_out == CHANNEL_MIKU :
        el.set()   # relese pause to lyric_send
## thread def
def lyric_send(lyric_code, e):
    # lyric_code check
    lyric_size = [len(v) for v in lyric_code]
    #print(lyric_size)   # for debug
    # lylic display
    lyric_line = 0
    lyric_column = 0
    while not e.isSet():
        # pause to command from other procedure
        el.wait()   # wait for set ep
        # delay to sending lyric code for miss touch
        time.sleep(WAIT_SEND)
        if not q_lyrcnt.empty():
            lyric_cnt = q_lyrcnt.get()
            # revise lyric code position (FOWARD_CHAR is else)
            if lyric_cnt == BACK_CHAR:    # Backward 1 char (send last char again)
                if present_column <= 0:  # when top of line
                    if present_line <= 0:  # back line
                        lyric_line = len(lyric_size) - 1
                    else:
                        lyric_line = present_line - 1
                    lyric_column = lyric_size[lyric_line] - 1  # set end of backed line
                else:
                    lyric_line = present_line   # when not top of line
                    lyric_column = present_column - 1
            elif lyric_cnt == FORWARD_SKIP: # Forward skip (always next line)
                lyric_column = 0
                if present_line >= len(lyric_size) - 1:
                    lyric_line = 0
                else:
                    lyric_line = present_line + 1
            elif lyric_cnt == BACK_SKIP:    # Backward skip
                lyric_column = 0
                if present_column <= 0:    # when top of line, decriment line.
                    if present_line <= 0:
                        lyric_line = len(lyric_size) - 1
                    else:
                        lyric_line = present_line - 1
                else:
                    lyric_line = present_line   # when not top of line, keep same line.
        # create lyric code message
        lyric_data = [67, 121, 9, 17, 10, 0, lyric_code[lyric_line][lyric_column]]
        #print(lyric_data) # for debug
        msg_lyric = mido.Message('sysex', data = lyric_data)
        # send lyric code message
        lock_port.acquire()
        outport.send(msg_lyric)
        lock_port.release()
        # put lyric code position
        present_lyric = [lyric_code, lyric_line, lyric_column]
        q_lyrpos.put(present_lyric)
        #lyric_display(lyric_code, present_lyric)   # deadlock at v_lyric.set(lyric_str)
        # backup lyric code position
        present_line = lyric_line
        present_column = lyric_column
        # revise lyric code position
        lyric_column += 1
        if lyric_column >= lyric_size[lyric_line]:
            lyric_column = 0
            lyric_line += 1
            if lyric_line >= len(lyric_size):
                lyric_line = 0
        # clear signal of end of play_song
        el.clear()
## event process
def e_button_select(event):
    if v_selbtn.get() == button_select_sel[MIDI_SELECT]:
        select_switch = INSTRUMENT_SELECT
    elif v_selbtn.get() == button_select_sel[INSTRUMENT_SELECT]:
        select_switch = LYRIC_SELECT
    else:
        select_switch = MIDI_SELECT
    # revise button & combo list
    v_selbtn.set(button_select_sel[select_switch])
    #
    combo_select.configure(values = list_sel[select_switch])
    select_values = list_sel[select_switch]
    combo_select.set(select_values[select_current[select_switch]])

#def e_combo_select(event):
#    print(combo_select.current(), ":", combo_select.get())

def e_button_enter(event):
    global channel_out
    global inport
    if midiout_state == MIDIOUT_EXIST:
        if v_selbtn.get() == button_select_sel[MIDI_SELECT]:
            midiin = midiport[combo_select.current()]
            inport = mido.open_input(midiin, callback=midi_exchange)
            #inport.callback = midi_exchange
            select_current[MIDI_SELECT] = combo_select.current()
            v_status.set('Select Instrument & Ent!')
        elif v_selbtn.get() == button_select_sel[INSTRUMENT_SELECT]:
            channel_out = instrument_set[combo_select.current()][1]
            msg_program_change = mido.Message('program_change', channel = channel_out, program = instrument_set[combo_select.current()][2])
            lock_port.acquire()
            outport.send(msg_program_change)
            lock_port.release() 
            #print(msg_program_change)   # for debug
            # quit lyric_send thread when channel_out is not CHANNEL_MIKU 
            if channel_out != CHANNEL_MIKU:
                for t in threading.enumerate():
                    if t.getName() == 'send_lyric':
                        e1.set()  # set signal of end of lyric_send
                        el.set()   # relese pause to lyric_send for 1st char 
                        t.join()
                v_status.set('')
                #v_lyric.set('')
            else:
                v_status.set('Select Lyric & Ent!')
            select_current[INSTRUMENT_SELECT] = combo_select.current()
            # revise effect value
            if v_effectbtn.get() == button_effect_sel[REVERB_SELECT]:
                effect_displayed = REVERB_SELECT
            elif v_effectbtn.get() == button_effect_sel[CHORUS_SELECT]:
                effect_displayed = CHORUS_SELECT
            else:
                effect_displayed = VARIATION_SELECT
            # revise combo list
            combo_effect_val.configure(values = effect_val_sel[effect_displayed])
            effect_val_values = effect_val_sel[effect_displayed]
            combo_effect_val.set(effect_val_values[effect_val_current[effect_displayed][channel_out]])
        elif v_selbtn.get() == button_select_sel[LYRIC_SELECT]:
            if channel_out == CHANNEL_MIKU :
                # quit lyric_send already started
                for t in threading.enumerate():
                    if t.getName() == 'send_lyric':
                        e1.set()  # set signal of end of lyric_send
                        el.set()   # relese pause to lyric_send for 1st char 
                        t.join()
                # start lyric_send
                lyric_code = mikucode_translate(lyricfiles[combo_select.current()])
                e1.clear()  # clear signal of end of lyric_send
                el.set()   # relese pause to lyric_send for 1st char 
                # set thread
                t1 = threading.Thread(name = 'send_lyric',target = lyric_send, args = (lyric_code, e1, ))
                # set thread daemon
                t1.setDaemon(True)
                # start thread object
                t1.start()
                select_current[LYRIC_SELECT] = combo_select.current()
                v_status.set('')
            else:
                v_status.set('Lyric is not actual on this instrument!')

def e_button_effect(event):
    if v_effectbtn.get() == button_effect_sel[REVERB_SELECT]:
        effect_switch = CHORUS_SELECT
    elif v_effectbtn.get() == button_effect_sel[CHORUS_SELECT]:
        effect_switch = VARIATION_SELECT
    else:
        effect_switch = REVERB_SELECT
    # revise button & combo list
    v_effectbtn.set(button_effect_sel[effect_switch])
    #
    combo_effect.configure(values = effect_sel[effect_switch])
    effect_values = effect_sel[effect_switch]
    combo_effect.set(effect_values[effect_current[effect_switch]])
    #
    combo_effect_val.configure(values = effect_val_sel[effect_switch])
    effect_val_values = effect_val_sel[effect_switch]
    combo_effect_val.set(effect_val_values[effect_val_current[effect_switch][channel_out]])

def e_combo_effect(event):
    #print(combo_effect.current(), ":", combo_effect.get())
    if midiout_state == MIDIOUT_EXIST:
        # create effect message & current backup
        if v_effectbtn.get() == button_effect_sel[REVERB_SELECT]:
            effect_data = [0x43, 0x10, 0x4C, 0x02, 0x01, 0x00, reverb_set[combo_effect.current()][1], reverb_set[combo_effect.current()][2]]
            effect_current[REVERB_SELECT] = combo_effect.current()
        elif v_effectbtn.get() == button_effect_sel[CHORUS_SELECT]:
            effect_data = [0x43, 0x10, 0x4C, 0x02, 0x01, 0x20, chorus_set[combo_effect.current()][1], chorus_set[combo_effect.current()][2]]
            effect_current[CHORUS_SELECT] = combo_effect.current()
        else:
            effect_data = [0x43, 0x10, 0x4C, 0x02, 0x01, 0x40, variation_set[combo_effect.current()][1], variation_set[combo_effect.current()][2]]
            effect_current[VARIATION_SELECT] = combo_effect.current()
        msg_effect = mido.Message('sysex', data = effect_data)
        # send effect message
        lock_port.acquire()
        outport.send(msg_effect)
        lock_port.release()
        #print(msg_effect) # for debug

def e_combo_effect_val(event):
    #print(combo_effect_val.current(), ":", combo_effect_val.get())
    if midiout_state == MIDIOUT_EXIST:
        # create effect send message & current backup
        if v_effectbtn.get() == button_effect_sel[REVERB_SELECT]:
            msg_effect_val = mido.Message('control_change', channel = channel_out, control = 0x5B, value = combo_effect_val.current())
            effect_val_current[REVERB_SELECT][channel_out] = combo_effect_val.current()
        elif v_effectbtn.get() == button_effect_sel[CHORUS_SELECT]:
            msg_effect_val = mido.Message('control_change', channel = channel_out, control = 0x5D, value = combo_effect_val.current())
            effect_val_current[CHORUS_SELECT][channel_out] = combo_effect_val.current()
        else:
            msg_effect_val = mido.Message('control_change', channel = channel_out, control = 0x5E, value = combo_effect_val.current())
            effect_val_current[VARIATION_SELECT][channel_out] = combo_effect_val.current()
        # send effect send message
        lock_port.acquire()
        outport.send(msg_effect_val)
        lock_port.release()
        #print(msg_effect_val) # for debug

def e_button_back(event):
    if channel_out == CHANNEL_MIKU :
        q_lyrcnt.put(BACK_CHAR) 
        el.set()   # relese pause to lyric_send
        #print("<") # for debug

def e_button_forward(event):
    if channel_out == CHANNEL_MIKU :
        q_lyrcnt.put(FORWARD_CHAR) 
        el.set()   # relese pause to lyric_send
        #print(">") # for debug

def e_button_fb(event):
    if channel_out == CHANNEL_MIKU :
        q_lyrcnt.put(BACK_SKIP) 
        el.set()   # relese pause to lyric_send
        #print("<<") # for debug

def e_button_ff(event):
    if channel_out == CHANNEL_MIKU :
        q_lyrcnt.put(FORWARD_SKIP) 
        el.set()   # relese pause to lyric_send
        #print(">>") # for debug

# initialize
channel_out = CHANNEL_MIKU
# List generation
#  Effect
reverb_sel = []
for set in reverb_set:
    reverb_sel.append(set[0])
#
chorus_sel = []
for set in chorus_set:
    chorus_sel.append(set[0])
#
variation_sel = []
for set in variation_set:
    variation_sel.append(set[0])
#
reverb_val = []
chorus_val = []
variation_val = []
i = 0
while i < 128:
    reverb_val.append(i)
    chorus_val.append(i)
    variation_val.append(i)
    i += 1
select_current = [0, 0, 0]
effect_current = [0, 5, 30]
effect_val_current = [[0x10, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
# midi port list
midiport = mido.get_output_names()
#  Instruments
instruments_sel = []
for set in instrument_set:
    instruments_sel.append(set[0])
# lyric text list
#  change dir to this py file
os.chdir(os.path.dirname(os.path.abspath('__file__')))
print('getcwd:      ', os.getcwd())
lyricfiles = glob.glob('./lyric/*.txt')
lyric_sel = []
for file in lyricfiles:
    lyric_sel.append(os.path.basename(file))
# list select
list_sel = [midiport, instruments_sel, lyric_sel]
button_select_sel = ('Key', 'Inst', 'Lyr')
#  effect
effect_sel = [reverb_sel, chorus_sel, variation_sel]
effect_val_sel = [reverb_val, chorus_val, variation_val]
button_effect_sel = ['Rev', 'Cho', 'Var']
# GUI
root = tk.Tk()
root.geometry('300x200+0+0')  # window size:XxY, display edge position:+X+Y
root.title("PocketMiku Controller")
root.configure(bg = BGCOLOR)
 
v_selbtn = tk.StringVar()
v_selbtn.set(button_select_sel[MIDI_SELECT])
v_select = tk.StringVar()

v_effectbtn = tk.StringVar()
v_effectbtn.set(button_effect_sel[REVERB_SELECT])
v_effectselect = tk.StringVar()
v_effectvalselect = tk.StringVar()

v_reverb = tk.StringVar()
v_reverb_val = tk.StringVar()
v_chorus = tk.StringVar()
v_chorus_val = tk.StringVar()
v_variation = tk.StringVar()
v_variation_val = tk.StringVar()

v_lyric = tk.StringVar()
v_lyric.set('')
v_status =  tk.StringVar()
v_status.set("StatusLabel")
#---------------------------------------
#  Title frame
#---------------------------------------
frame_title = tk.Frame(root, bg = BGCOLOR)
# label
label = tk.Label(frame_title, text = "PocketMiku Controller", fg = FGCOLOR, bg = BGCOLOR)
# set objects in frame
label.pack(side = tk.LEFT)
# set frame in window
frame_title.pack(side = tk.TOP, fill = tk.X)
#---------------------------------------
#  Select frame
#---------------------------------------
frame_select = tk.Frame(root, bg = BGCOLOR)
# objects
button_select = tk.Button(frame_select, width = BTNWIDTH, textvariable = v_selbtn)
button_select.bind("<Button-1>", e_button_select)
combo_select = ttk.Combobox(frame_select, height = DISPHIGHT, width = SELWIDTH, justify= "left", values = list_sel[MIDI_SELECT], textvariable = v_select )
select_values = list_sel[MIDI_SELECT]
combo_select.set(select_values[select_current[MIDI_SELECT]])
#combo_select.bind('<<ComboboxSelected>>', e_combo_select)
button_enter = tk.Button(frame_select, width = BTNWIDTH, text = 'Ent')
button_enter.bind("<Button-1>", e_button_enter)
# set objects in frame
button_select.pack(padx = 5, side = tk.LEFT)
combo_select.pack(side = tk.LEFT)
button_enter.pack(padx = 10, side = tk.LEFT)
# set frame in window
frame_select.pack(pady = 1, fill = tk.X)
#---------------------------------------
#  Effect frame
#---------------------------------------
frame_effect = tk.Frame(root, bg = BGCOLOR)
# objects
button_effect = tk.Button(frame_effect, width = BTNWIDTH, textvariable = v_effectbtn)
button_effect.bind("<Button-1>", e_button_effect)
combo_effect = ttk.Combobox(frame_effect, height = DISPHIGHT, width = SELWIDTH, justify= "left", values = effect_sel[REVERB_SELECT], textvariable = v_effectselect )
effect_values = effect_sel[REVERB_SELECT]
combo_effect.set(effect_values[effect_current[REVERB_SELECT]])
combo_effect.bind('<<ComboboxSelected>>', e_combo_effect)
combo_effect_val = ttk.Combobox(frame_effect, height = DISPHIGHT, width = VALWIDTH, justify= "right", values = effect_val_sel[REVERB_SELECT], textvariable = v_effectvalselect )
effect_val_values = effect_val_sel[REVERB_SELECT]
combo_effect_val.set(effect_val_values[effect_val_current[REVERB_SELECT][channel_out]])
combo_effect_val.bind('<<ComboboxSelected>>', e_combo_effect_val)
# set objects in frame
button_effect.pack(padx = 5, side = tk.LEFT)
combo_effect.pack(side = tk.LEFT)
combo_effect_val.pack(padx = 5, side = tk.LEFT)
# set frame in window
frame_effect.pack(pady = 3, fill = tk.X)
#---------------------------------------
#  Lyric title frame
#---------------------------------------
frame_tlyric = tk.Frame(root, bg = BGCOLOR)
# objects
label_lyric = tk.Label(frame_tlyric, width = LABELWIDTH, anchor = "w", text = "Lyric ", fg = FGCOLOR, bg = BGCOLOR)
button_fb = tk.Button(frame_tlyric, width = BTNWIDTH, text = '<<')
button_fb.bind("<Button-1>", e_button_fb)
button_ff = tk.Button(frame_tlyric, width = BTNWIDTH, text = '>>')
button_ff.bind("<Button-1>", e_button_ff)
# set objects in frame
label_lyric.pack(padx = 5, side = tk.LEFT)
button_fb.pack(padx = 0, side = tk.LEFT)
button_ff.pack(padx = 10, side = tk.LEFT)
# set frame in window
frame_tlyric.pack(pady = 2, fill = tk.X)

#---------------------------------------
#  Lyric frame
#---------------------------------------
frame_lyric = tk.Frame(root, bg = BGCOLOR)
# objects
button_back = tk.Button(frame_lyric, width = 2, text = '<')
button_back.bind("<Button-1>", e_button_back)
label_dsplylic = tk.Label(frame_lyric, width = 23, anchor = "c", relief = tk.SUNKEN, bd =3, textvariable = v_lyric )
button_forward = tk.Button(frame_lyric, width = 2, text = '>')
button_forward.bind("<Button-1>", e_button_forward)
# set objects in frame
button_back.pack(padx = 5, side = tk.LEFT)
label_dsplylic.pack(side = tk.LEFT)
button_forward.pack(padx = 5, side = tk.LEFT)
# set frame in window
frame_lyric.pack(pady = 1, fill = tk.X)
#---------------------------------------
#  Status bar frame
#---------------------------------------
# Frame
frame_statusbar = tk.Frame(root, relief = tk.SUNKEN, bd = 2)
# label in frame
label_status = tk.Label(frame_statusbar, textvariable = v_status)
# set objects in frame
label_status.pack(side = tk.LEFT)
# set frame in window
frame_statusbar.pack(side = tk.BOTTOM, fill = tk.X)
#---------------------------------------
#  remaining area
#---------------------------------------
frame = tk.Frame(root, relief = tk.SUNKEN, bd = 2, bg = BGCOLOR)
frame.pack(expand = True, fill = tk.BOTH)

#---------------------------------------
#  midi part
#---------------------------------------
# set midiout
midiout = 'NSX-39:NSX-39 MIDI 1'
try:
    outport = mido.open_output(midiout)
    midiout_state = MIDIOUT_EXIST
    # connect effect variation
    effect_data = [0x43, 0x10, 0x4C, 0x02, 0x01, 0x5A, 0x7F]
    msg_effect = mido.Message('sysex', data = effect_data)
    #  send message
    lock_port.acquire()
    outport.send(msg_effect)
    lock_port.release()
    v_status.set('Select KEY & Ent!')
except OSError:
    midiout_state = NO_MIDIOUT
    #display_1stline('Emergency stop!!')
    v_status.set('No MIDI OUT exists! Check & restart!')
    # close IO
    print('MIDI OUT does not exist!')   # for debug

#---------------------------------------
#  thread start
#---------------------------------------
# main basement start
eb = threading.Event()
tb = threading.Thread(target = main_basement, args=(eb,))
tb.setDaemon(True)
tb.start()
#---------------------------------------
#  GUI start
#---------------------------------------
root.mainloop()
#---------------------------------------
#  thread quit
#---------------------------------------
# Game controller quit
eb.set()
tb.join()
# close IO
try:
    outport.close()
except NameError:
    print('MIDI OUT dose not exist!')
try:
    inport.close()
except NameError:
    print('MIDI IN is not set!')


