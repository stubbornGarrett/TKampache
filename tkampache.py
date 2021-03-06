import ampache
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror, showinfo, showwarning
import styleconfig
from PIL import Image, ImageTk
import vlc

#import os, sys

def get_sessionkey(url, user, api_key, format='json'):
    """ Returns session key
        url:        Adress of the Ampache server
        user:       User to login with
        api_key:    API key, manualy generated by admin
        format:     json or xml
    """
    encrypted_key = ampache.encrypt_string(api_key, user)
    if encrypted_key:
        try:
            sessionkey = ampache.handshake(url, encrypted_key, api_format=format)
            if sessionkey:
                return sessionkey
            else:
                showerror("Details incorrect", "Some or all of your details are incorrect!")
                return False
        except ValueError:
            showerror("Invalid URL", "The entered URL is invalid!")
            return False
    else:
        showerror("Encrytion failed", "Encryption of username and API key went wrong!\n(However that happened...)")
        return False

class Player(ttk.Frame):
    """ Player
        GUI element of TKampache-Client
    """
    def __init__(self, master=None, varvolume=None):
        ttk.Frame.__init__(self, master)
        self.img = None

        self.canvas_coverart = tk.Canvas(self, width=300, height=300, bg='grey20')
        self.canvas_coverart_imageID = self.canvas_coverart.create_image(40, 40, image=self.img, anchor='nw')
        self.canvas_coverart_image = None
        self.frame_buttons = ttk.Frame(self)
        self.button_play = ttk.Button( self.frame_buttons, text="Start")
        self.button_toggle_pause = ttk.Button(self.frame_buttons, text="Play/Pause")
        self.button_next = ttk.Button( self.frame_buttons, text="Next")
        self.button_previous = ttk.Button(self.frame_buttons, text="Prev")
        self.scale_volume = ttk.Scale(self.frame_buttons, variable=varvolume, from_=0, to_=100)

        self.canvas_coverart.grid(  row=0, column=0, sticky='news', padx=3, pady=3)
        self.frame_buttons.grid(    row=2, column=0, sticky='news', padx=3, pady=3)
        self.frame_buttons.columnconfigure(1, weight=1)
        self.frame_buttons.columnconfigure(2, weight=1)

        self.button_previous.grid(  row=0, column=0, sticky='news')
        self.button_play.grid(      row=0, column=1, sticky='news')
        self.button_toggle_pause.grid(     row=0, column=2, sticky='news')
        self.button_next.grid(      row=0, column=3, sticky='news')
        self.scale_volume.grid(     row=1, column=0, sticky='we', columnspan=4)


    def set_coverart(self, url, sessionkey, id, t='song', format='json'):
        try:
            ampache.get_art(url, sessionkey, id, type=t, destination='./cover', api_format=format)
            tmpimg = Image.open('./cover')
            tmpimg = tmpimg.resize((self.canvas_coverart.winfo_width(), self.canvas_coverart.winfo_height()))
            self.img = ImageTk.PhotoImage(tmpimg)
            self.canvas_coverart_image = self.canvas_coverart.create_image(0,0, image=self.img, anchor='nw')
        except OSError:
            self.img = None
            self.canvas_coverart_image = self.canvas_coverart.create_image(0,0, image=self.img, anchor='nw')

class List(ttk.Frame):
    """ List
        GUI element of TKampache-Client
    """
    def __init__(self, master=None, songlistvar=None):
        ttk.Frame.__init__(self, master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Songlist
        self.listbox_songs = tk.Listbox(self, listvariable=songlistvar, selectmode=tk.SINGLE)

        self.listbox_songs.grid(    row=0, column=0, sticky='news')

class TKampache(ttk.Frame):
    """ TKampache
        Desktop client for Ampache-Server
    """
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.grid(row=0, column=0, sticky='news')
        
        ### Data ###
        self.session_key = tk.StringVar()
        self.session_key.set('')
        self.ampache_url = tk.StringVar()
        self.ampache_url.set('http://localhost')
        self.ampache_user = tk.StringVar()
        self.ampache_user.set('admin')
        self.ampache_apikey = tk.StringVar()
        self.ampache_apikey.set('')
        self.ampache_apiformat = tk.StringVar()
        self.ampache_apiformat.set('json')

        self.cache_list_songs = tk.StringVar()
        self.cache_list_songs.set([])
        self.index_songs = []

        self.media_player = None
        self.media_volume = tk.IntVar()
        self.media_volume.set(100)
        self.current_song_id = tk.IntVar()
        self.current_song_id.set(0)


        ### GUI ###

        # Topbar
        self.menu_menubar = tk.Menu(self.winfo_toplevel())

        # Menus
        self.menu_settings = tk.Menu(self.menu_menubar, tearoff=0)
        self.menu_settings.add_command(label='Connect', command=self.popup_connect)
        self.menu_settings.add_command(label='Disconnect', command=self.disconnect)
        self.menu_settings.add_separator()
        self.menu_settings.add_command(label='Reload songs', command=self.update_list_songs)
        self.menu_settings.add_separator()
        self.menu_settings.add_command(label='Exit', command=self.quit)

        self.menu_menubar.add_cascade(label='Settings', menu=self.menu_settings)


        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Player
        self.gui_player = Player(self, self.media_volume)
        self.gui_player.grid(row=0, column=0, sticky='n')
        self.gui_player.button_play.config(command=self.play)
        self.gui_player.button_toggle_pause.config(command=self.toggle_pause)
        self.gui_player.button_next.config(command=self.next)
        self.gui_player.button_previous.config(command=self.previous)
        self.gui_player.scale_volume.config(command=self.update_volume)

        # List
        self.gui_list = List(self, self.cache_list_songs)
        self.gui_list.grid(row=0, column=1, sticky='news', padx=5, pady=5)


        if tk.Tk.winfo_exists(master):
            self.master.title('TK Ampache')
            self.master.resizable(height=False)
            self.master.config(menu=self.menu_menubar)

        self.update_style()

    def update_list_songs(self):
        self.index_songs = ampache.get_indexes(self.ampache_url.get(), self.session_key.get(), "song", api_format=self.ampache_apiformat.get())
        list = []
        for item in self.index_songs:
            string = ''.join('{} - {}'.format(item['title'], item['album']['name']))
            list.append(string)
        self.cache_list_songs.set(list)
        #self.cache_list_songs.set([item.get('title') for item in self.index_songs])

    def play(self, id=0, t='song'):
        try:
            if not id:
                self.current_song_id.set(self.gui_list.listbox_songs.curselection()[0]+1)
            ampache.stream(self.ampache_url.get(), self.session_key.get(), self.current_song_id.get(), t, './buffer', self.ampache_apiformat.get())
            if self.media_player:
                self.media_player.stop()
            else:
                self.update_volume()
            self.media_player = vlc.MediaPlayer('./buffer')
            self.media_player.play()
            self.gui_player.set_coverart(self.ampache_url.get(), self.session_key.get(), self.current_song_id.get(), 'song', format='json')
        except PermissionError:
            showerror("Insuficent permissions", "Can't write stream to disk!")

    def toggle_pause(self):
        self.media_player.pause()

    def previous(self):
        if self.current_song_id.get() > 1:
            self.current_song_id.set(self.current_song_id.get()+1)
            self.play(self.current_song_id.get())
            self.gui_list.listbox_songs.select_clear(self.gui_list.listbox_songs.curselection()[0])
            self.gui_list.listbox_songs.selection_set(self.current_song_id.get()-1)
            self.gui_player.set_coverart(self.ampache_url.get(), self.session_key.get(), self.current_song_id.get(), 'song', format='json')

    def next(self):
        self.current_song_id.set(self.current_song_id.get()+1)
        self.play(self.current_song_id.get())
        self.gui_list.listbox_songs.select_clear(self.gui_list.listbox_songs.curselection()[0])
        self.gui_list.listbox_songs.selection_set(self.current_song_id.get()-1)
        self.gui_player.set_coverart(self.ampache_url.get(), self.session_key.get(), self.current_song_id.get(), 'song', format='json')
    
    def update_volume(self, event=None):
        if self.media_player:
            self.media_player.audio_set_volume(self.media_volume.get())
        #self.media_volume.set(self.media_player.audio_get_volume())

    def connect(self, url=None, user=None, apikey=None, apiformat=None):
        self.disconnect()
        if not url:
            url = self.ampache_url.get()
        if not user:
            user = self.ampache_user.get()
        if not apikey:
            apikey = self.ampache_apikey.get()
        if not apiformat:
            self.ampache_apiformat.get()
        self.session_key.set(get_sessionkey(url, user, apikey, apiformat))
            
        if self.session_key:
            self.ampache_url.set(       url)
            self.ampache_user.set(      user)
            self.ampache_apikey.set(    apikey)
            self.ampache_apiformat.set( apiformat)
            self.update_list_songs()
            self.gui_player.set_coverart(self.ampache_url.get(), self.session_key.get(), 1, t='song', format='json')
            self.gui_list.listbox_songs.selection_set(0)
            return True
        else:
            showinfo("Failed", "Connection Failed!")
            return False

    def disconnect(self):
        if self.session_key.get():
            ampache.goodbye(self.ampache_url.get(), self.ampache_apikey.get(), self.ampache_apiformat.get())
            self.session_key.set('')

    def popup_connect(self):
        window = tk.Toplevel(self, takefocus=True, padx=4, pady=4, bg='#222222')
        window.grab_set()
        window.wm_title("Connect")
        window.transient(self)
        window.resizable(width=False, height=False)
        
        label_url = ttk.Label(window, text="Ampache URL").grid(row=0, column=0, sticky='we')
        entry_url = ttk.Entry(window)
        entry_url.insert(0, self.ampache_url.get())
        entry_url.grid(row=0, column=1, sticky='we')

        label_user = ttk.Label(window, text="Username").grid(row=1, column=0, sticky='we')
        entry_user = ttk.Entry(window)
        entry_user.insert(0, self.ampache_user.get())
        entry_user.grid(row=1, column=1, sticky='we')

        label_apikey = ttk.Label(window, text="API Key").grid(row=2, column=0, sticky='we')
        entry_apikey = ttk.Entry(window, width=35)
        entry_apikey.insert(0, self.ampache_apikey.get())
        entry_apikey.grid(row=2, column=1, sticky='we')

        label_apiformat = ttk.Label(window, text="Format").grid(row=3, column=0, sticky='we')
        entry_apiformat = ttk.Entry(window)
        entry_apiformat.insert(0, self.ampache_apiformat.get())
        entry_apiformat.grid(row=3, column=1, sticky='we')
        
        def connect():
            if self.connect(entry_url.get(), entry_user.get(), entry_apikey.get(), entry_apiformat.get()):
                window.destroy()

        button_startLogin = ttk.Button(window, text="Connect", command=connect )
        button_startLogin.grid(row=4, column=0, sticky='we', columnspan=2, pady=2)

    def update_style(self):
        self.style = styleconfig.Style()
        self.style.create_theme('TKampache-Theme', '#222222', '#444444', '#ffffff', '#111199', '#333333', '#555555')#, '""')
        self.style.theme_use('TKampache-Theme')

    def quit_application(self):
        self.disconnect()
        if self.media_player:
            self.media_player.release()
        self.quit()

def main():
    root = tk.Tk()
    root.resizable(height=False)
    #root.overrideredirect(1)
    tk.Grid.columnconfigure(root, 0, weight=1)
    tk.Grid.rowconfigure(root, 0, weight=1)
    application = TKampache(root)
    root.protocol('WM_DELETE_WINDOW', application.quit_application)
    application.mainloop()

if __name__ == '__main__':
    #ampache.set_debug(True)
    main()