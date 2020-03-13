import tkinter as tk
import tkinter.ttk as ttk
#import configparser

class Style(ttk.Style):
    def __init__(self):
        ttk.Style.__init__(self)

    def create_theme(self, name, bg , lightbg, fg, highlight,  inactivebg, inactivefg):#, defaultFont):
        self.theme_create(themename=name, settings={
            '.':                {'configure': { 'background'    : bg ,
                                                'foreground'    : fg ,
                                                'highlightcolor': highlight ,
                                                #'font'          : defaultFont,
                                                'relief'        : 'flat'}},

            'TFrame':           {'configure': { #'relief'        : tk.RIDGE,
                                                'relief'        : tk.FLAT,
                                                'padding'       : 10}},

            'TLabel':           {'configure': { #'font'          : defaultFont,
                                                'padding'       : 2,
                                                'borderwidth'   : 1,
                                                'relief'        : 'groove',
                                                'width'         : -15,
                                                'background'    : lightbg},
                                'map'       : { 'background'    : [('disabled', inactivebg)],
                                                'foreground'    : [('disabled', inactivefg)],
                                                'foreground'    : [('active', highlight)]}},

            'TButton':          {'configure': { #'font'          : defaultFont,
                                                'background'    : lightbg,
                                                'padding'       : 2,
                                                'borderwidth'   : 2,
                                                'anchor'        : tk.CENTER,
                                                'relief'        : tk.RAISED},
                                'map'       : { 'relief'        : [('pressed', tk.SUNKEN)],
                                                'background'    : [('disabled', inactivebg)],
                                                'foreground'    : [('disabled', inactivefg)],
                                                'background'    : [('active', bg)],
                                                }},

            'TEntry':           {'configure': { 'foreground'    : bg ,
                                                #'selectbackground': highlight ,
                                                'borderwidth'   : 1,
                                                'padding'       : 2,},
                                'map'       : { 'background'    : [('disabled', inactivebg)],
                                                'foreground'    : [('disabled', inactivefg)]}},

            'TScale':           {'configure': { 'background'    : bg,
                                                'borderwidth'   : 1,
                                                'groovewidth'   : 0,
                                                'relief'        : tk.RAISED},
                                'map'       : { 'background '   : [('active', highlight )]}},
        })