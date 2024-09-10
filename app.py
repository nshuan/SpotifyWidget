import tkinter as tk
from tkinter import font
import time
import threading
from PIL import Image as img, ImageTk as imgTk, ImageDraw as imgDr
from spotifyAPI import SpotifyTrack

class MusicPlayer:
    def __init__(self, root: tk.Tk, spotify: SpotifyTrack):
        self.root = root
        self.spotify = spotify

        self.dimension = (320, 120)
        self.track_image_pos = (19, 19)
        self.track_image_size = (42, 42)
        self.track_name_pos = (160, 22)
        self.track_name_font_size = 10
        self.track_artists_pos = (160, 37)
        self.track_artists_font_size = 8
        self.slider_pos = (80, 96)
        self.slider_size = (160, 2)

        self.play_button_pos = (163, 70)
        self.previous_button_pos = (124, 70)
        self.next_button_pos = (202, 70)
        self.shuffle_button_pos = (89, 70)
        self.repeat_button_pos = (232, 70)

        self.root.geometry(str(self.dimension[0]) + "x" + str(self.dimension[1]))
        self.root.configure(bg="#000000")
        self.track_name_font = font.Font(family="Montserrat", size=self.track_name_font_size, weight="bold")
        self.track_artist_font = font.Font(family="Montserrat", size=self.track_artists_font_size)
        
        self.canvas = tk.Canvas(self.root, width=self.dimension[0], height=self.dimension[1], bg="#000000", relief="flat", bd=0, highlightthickness=0)
        self.canvas.pack()

        self.track_name = self.canvas.create_text(self.track_name_pos[0], self.track_name_pos[1], anchor="center", text="", font=self.track_name_font, fill="#d1d1d1")
        self.track_artists = self.canvas.create_text(self.track_artists_pos[0], self.track_artists_pos[1], anchor="center", text="", font=self.track_artist_font, fill="#9b9b9b")
        # name_cover_image = tk.PhotoImage(file="Texture/name_cover.png")
        # self.canvas.create_image(20, 20, anchor="nw", image=name_cover_image)

        self.design_window()
        self.design_slider()

        # Track currently playing
        self.current_song = None
        self.song_length = 0
        self.is_paused = False

        # Add buttons
        self.play_icon = tk.PhotoImage(file="Texture/play_icon.png")
        self.pause_icon = tk.PhotoImage(file="Texture/pause_icon.png")
        self.play_button = tk.Button(self.root, image=self.play_icon, bg="#000000", activebackground="#000000", relief="flat", borderwidth=0, highlightthickness=0, command=self.play_pause)
        self.play_button.image = self.play_icon
        self.play_button_window = self.canvas.create_window(self.play_button_pos[0], self.play_button_pos[1], window=self.play_button)

        self.previous_icon = tk.PhotoImage(file="Texture/previous_icon.png")
        self.previous_button = tk.Button(self.root, image=self.previous_icon, bg="#000000", activebackground="#000000", relief="flat", borderwidth=0, highlightthickness=0, command=self.previous_track)
        self.previous_button_window = self.canvas.create_window(self.previous_button_pos[0], self.previous_button_pos[1], window=self.previous_button)

        self.next_icon = tk.PhotoImage(file="Texture/next_icon.png")
        self.next_button = tk.Button(self.root, image=self.next_icon, bg="#000000", activebackground="#000000", relief="flat", borderwidth=0, highlightthickness=0, command=self.next_track)
        self.next_button_window = self.canvas.create_window(self.next_button_pos[0], self.next_button_pos[1], window=self.next_button)

        self.shuffle_icon = tk.PhotoImage(file="Texture/shuffle_icon.png")
        self.shuffle_button = tk.Button(self.root, image=self.shuffle_icon, bg="#000000", activebackground="#000000", relief="flat", borderwidth=0, highlightthickness=0, command=self.toggle_shuffle)
        self.shuffle_button_window = self.canvas.create_window(self.shuffle_button_pos[0], self.shuffle_button_pos[1], window=self.shuffle_button)

        self.repeat_icon = tk.PhotoImage(file="Texture/repeat_icon.png")
        self.repeat_button = tk.Button(self.root, image=self.repeat_icon, bg="#000000", activebackground="#000000", relief="flat", borderwidth=0, highlightthickness=0, command=self.update_repeat)
        self.repeat_button_window = self.canvas.create_window(self.repeat_button_pos[0], self.repeat_button_pos[1], window=self.repeat_button)

        # Update
        self.update_thread = threading.Thread(target=self.update)
        self.update_thread.daemon = True
        self.update_thread.start()

    def design_window(self):
        def close_window():
            self.root.destroy()
            if self.is_maximized:
                self.root.geometry("500x400")
                self.is_maximized = False
            else:
                self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
                self.is_maximized = True
        def start_move(event):
            """ Store the offset between the mouse position and the window position. """
            self.offset_x = event.x
            self.offset_y = event.y
        def do_move(event):
            """ Move the window based on the mouse movement. """
            x = event.x_root - self.offset_x
            y = event.y_root - self.offset_y
            self.root.geometry(f"+{x}+{y}")
        def show_context_menu(event):
            self.context_menu.post(event.x_root, event.y_root)
            
        self.root.overrideredirect(True)

        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Close", command=lambda: close_app(self))
        self.root.bind("<Button-3>", show_context_menu)

        self.custom_title_bar = tk.Frame(self.root, bg="#000000", relief="flat", bd=0)
        self.custom_title_bar.pack(side="top", fill="x")

        # Add custom window controls (close, minimize, maximize)
        close_button = tk.Button(self.custom_title_bar, text="✖", bg="#e74c3c", fg="white", command=close_window, relief="flat")
        close_button.pack(side="right", padx=5)

        # Add a label for dragging the window
        title_label = tk.Label(self.custom_title_bar, text="Custom Window", bg="#000000", fg="white")
        title_label.pack(side="left", padx=10)

        # Bind events to move the window
        self.canvas.bind("<Button-1>", start_move)
        self.canvas.bind("<B1-Motion>", do_move)

        # Main content area
        self.main_frame = tk.Frame(self.root, bg="#000000")
        self.main_frame.pack(fill="both", expand=True)

        # Add resizing functionality
        self.is_maximized = False

        # Variables to track window movement
        self.offset_x = 0
        self.offset_y = 0

    def design_slider(self):                
        self.slider_image = tk.PhotoImage(file="Texture/slider_bar.png")
    
        pos = self.slider_pos
        self.canvas.create_image(pos[0], pos[1], anchor="nw", image=self.slider_image)
        slider_size = self.slider_size
        self.fill_handle = self.canvas.create_rectangle(pos[0] + slider_size[1] / 2, pos[1], pos[0] + slider_size[1] / 2, pos[1] + slider_size[1], fill="#ffffff", outline="")
        # self.marker = self.canvas.create_oval(pos[0], pos[1], pos[0] + 4, pos[1] + 4, fill="#ffffff", outline="")

        # Label to show the current value
        self.value_label = tk.Label(self.root, text="Value: 0")
        self.value_label.pack(pady=10)

    def update_play_button(self):
        return
        

    def play_pause(self):
        if self.is_paused:
            self.spotify.play_current_track()
            self.update_play_button(True)
            self.is_paused = False
        else:
            self.spotify.pause_current_track()
            self.update_play_button(False)
            self.is_paused = True
    
    def previous_track(self):
        return
    
    def next_track(self):
        return
    
    def toggle_shuffle(self):
        return
    
    def update_repeat(self):
        return

    def process_track_image(self, image):
        if image is None:
            return None
        track_image_original = image.convert("RGBA")
        image_resize = track_image_original.resize((42, 42))

        # create a mask for rounded corners
        mask = img.new("L", image_resize.size, 0)
        draw = imgDr.Draw(mask)
        draw.rounded_rectangle((0, 0, image_resize.size[0], image_resize.size[1]), radius=4, fill=255)
        
        # Apply the mask to the image
        image_resize.putalpha(mask)

        return image_resize

    def update(self):
        while True:
            playing_track = self.spotify.currently_playing_track()
            if playing_track is None:
                continue


            # update track name and artists
            if not playing_track.name == self.current_song:
                self.current_song = playing_track.name
                self.canvas.itemconfig(self.track_name, text=playing_track.name)
                self.canvas.itemconfig(self.track_artists, text=playing_track.artists_in_str())
                
                # # update track image
                # track_img = self.process_track_image(self.spotify.download_image(playing_track.image_url))
                # if track_img is not None:
                #     self.track_image = tk.PhotoImage(track_img)
                #     self.canvas.create_image(self.track_image_pos[0], self.track_image_pos[1], anchor="nw", image=self.track_image)

            # update slider
            current_pos = playing_track.progress_in_ms
            fill = current_pos / playing_track.duration_in_ms * self.slider_size[0]
            slider_pos = self.slider_pos
            slider_size = self.slider_size
            self.canvas.coords(self.fill_handle, slider_pos[0] + slider_size[1] / 2, slider_pos[1], slider_pos[0] + fill, slider_pos[1] + slider_size[1])

            # update play button
            self.update_play_button(playing_track.is_playing)
            self.is_paused = not playing_track.is_playing
            
            time.sleep(0.02)

    def update_play_button(self, is_playing: bool):
        if is_playing:
            self.is_paused = True
            self.play_button.config(image=self.pause_icon)
            self.play_button.image = self.pause_icon
        else:
            self.is_paused = False
            self.play_button.config(image=self.play_icon)
            self.play_button.image = self.play_icon

    def slide_music(self, val):
        x = 1

def toggle_app(app: MusicPlayer):
    if app.root.state() == 'withdrawn':
        show_app()
    else:
        hide_app()

def close_app(app: MusicPlayer):
    app.root.destroy()

def show_app(app: MusicPlayer):
    app.root.deiconify()
    app.root.lift()

def hide_app(app: MusicPlayer):
    app.root.withdraw()

if __name__ == "__main__":
    root = tk.Tk()
    auth_complete_event = threading.Event()
    spotify = SpotifyTrack(auth_complete_event)
    auth_complete_event.wait()

    app = MusicPlayer(root, spotify)
    app.root.attributes("-topmost", True)
    

    
    
    root.mainloop()



