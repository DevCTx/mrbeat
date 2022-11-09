from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton

DEBUG_INIT = True

TRACK_WIDGET_SIZE_MAX = dp(90)
TRACK_WIDGET_SIZE_MIN = dp(50)

class TrackStepButton(ToggleButton):
    pass

class TrackSoundButton(Button):
    pass

class TrackWidget(BoxLayout):
    audio_engine = None     # Lecteur de son passé en initialisation pour les boutons
    sound = None            # son à jouer dans ce TrackWidget
    track_source = None     # son à jouer
    nb_steps = 0            # nombre de boutons dans la sequence
    step_buttons = []       # états des boutons de la sequence
    id_track = 0            # index extérieur permettant de savoir de quel track il s'agit


    def __init__(self, sound, audio_engine, track_source, id_track, nb_steps, steps_left_align, **kwargs):
        super(TrackWidget, self).__init__(**kwargs)

        self.sound = sound
        self.audio_engine = audio_engine
        self.nb_steps = nb_steps
        self.track_source = track_source
        self.id_track = id_track

        # Taille min et max de tout un widget
        self.size_hint_max_y = TRACK_WIDGET_SIZE_MAX
        self.size_hint_min_y = TRACK_WIDGET_SIZE_MIN

        # Association du Sound button et du separator dans un Boxlayout
        sound_button_separator = BoxLayout()
        sound_button_separator.size_hint_x = None
        sound_button_separator.width = steps_left_align
        self.add_widget(sound_button_separator)

        # Sound Button
        sound_button = TrackSoundButton()
        sound_button.background_normal = "images/sound_button_normal.png"
        sound_button.background_down = "images/sound_button_down.png"
        # sound_button.text = self.sound.displayname + "\nVolume : " + str(self.sound.volume)
        sound_button.text = self.sound.displayname
        sound_button.bold = True
        sound_button.on_press = self.on_sound_button_press
        sound_button_separator.add_widget(sound_button)

        # Separator
        separator_image = Image(source="images/track_separator.png")
        separator_image.size_hint_x = None
        separator_image.width = dp(15)
        sound_button_separator.add_widget(separator_image)

        # Step buttons
        self.step_buttons = []
        for i in range(0, self.nb_steps):
            step_button = TrackStepButton()
            if int( i/4) % 2 == 0 :
                step_button.background_normal = "images/step_normal1.png"
            else:
                step_button.background_normal = "images/step_normal2.png"
            step_button.background_down = "images/step_down.png"
            if self.track_source.steps_sequence[i] == 1:
                step_button.state='down'
            step_button.bind(state=self.on_step_button_state)
            self.step_buttons.append(step_button)
            self.add_widget(step_button)

    def on_sound_button_press(self):
        self.audio_engine.play_one_shot_sound(self.sound.frames, self.sound.volume)


    def on_step_button_state(self, widget, value):
        steps_sequence = []
        for i in range(0, self.nb_steps):
            if self.step_buttons[i].state == "down":
                steps_sequence.append(1)
            else:
                steps_sequence.append(0)
        self.track_source.set_track_sequence( steps_sequence )


