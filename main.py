import math

from kivy import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'minimum_width', '720')
Config.set('graphics', 'minimum_height', '280')

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from audio_engine import AudioEngine
from play_indicator import PlayIndicatorWidget
from sound_kit_service import SoundKitService
from track import TrackWidget, TRACK_WIDGET_SIZE_MAX

Builder.load_file("track.kv")
Builder.load_file("play_indicator.kv")

NB_TRACK_STEPS = 16
STEPS_LEFT_ALIGN = dp(120)

class VerticalSpacingWidget(Widget):
    pass

class MainWidget(RelativeLayout):
    tracks_boxlayout = BoxLayout()             # BoxLayout affichant une serie de TrackWidget

    play_indicator_widget = PlayIndicatorWidget()   # Widget(BoxLayout) affichant une serie de bouton pour suivre BPM
    sound_kit_service = None                        # bibliothèque de sons chargés en format 16 bits
    audio_engine = None                             # lecteur de son

    screen_bpm = NumericProperty(115)                # Battements par minutes (initialisé à 60)
    BPM_MAX = 240
    BPM_MIN = 5

    nb_tracks = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MainWidget,self).__init__(**kwargs)   # initialise les éléments du .kv

        self.sound_kit_service = SoundKitService()  # initialise avec SoundKit1 pour le moment
        self.audio_engine = AudioEngine()           # initialise le lecteur de son Mono 44100Hz 1024bits

        sound_kit_service_array_frames = self.sound_kit_service.get_all_samples()
        sound_kit_service_array_volumes = self.sound_kit_service.get_all_volumes()
        self.nb_tracks = self.sound_kit_service.get_nb_tracks()

        self.mixer = self.audio_engine.create_mixer(sound_kit_service_array_frames, sound_kit_service_array_volumes,
                                        self.screen_bpm, self.BPM_MIN, NB_TRACK_STEPS,
                                        self.on_clock_mixer_set_play_indicator_current_step_index)


    # MainWidget est un RelativeLayout qui appelle un BoxLayout donc on a besoin d'identifier le BoxLayout
    def on_parent(self, widget, parent):
        self.play_indicator_widget.set_nb_steps(NB_TRACK_STEPS, STEPS_LEFT_ALIGN)
        for i in range (0,self.nb_tracks):
            sound = self.sound_kit_service.get_sound_at(i)      # charge la liste de sons du sound_kit_service
            self.tracks_boxlayout.add_widget(VerticalSpacingWidget())
            self.tracks_boxlayout.add_widget(TrackWidget( sound,
                                                          self.audio_engine,
                                                          self.mixer.tracks[i],
                                                          i,
                                                          NB_TRACK_STEPS,
                                                          STEPS_LEFT_ALIGN))
        self.tracks_boxlayout.add_widget(VerticalSpacingWidget())
        self.tracks_boxlayout.size_hint_min_y = TRACK_WIDGET_SIZE_MAX * self.nb_tracks


    # fonction asynchrone lancé par Clock à chaque get_bytes du mixer (1 buffer = 1 step)
    def on_clock_mixer_set_play_indicator_current_step_index(self, get_bytes_step_index, dt):
        if self.play_indicator_widget is not None:
            # décalage de steps entre son et lumière en fonction des BPM (dû aux buffers audio)
            # revoir la notion de taille de buffer pour ne pas charger la taille d'un step mais de plus petits
            # pour une meilleure intéraction utilisateur (plus grande réactivité normalement)
            delay_index = get_bytes_step_index + self.delay_light_sound()
            if delay_index < 0:
                delay_index += NB_TRACK_STEPS
            self.play_indicator_widget.set_current_screen_step_index(delay_index)

    def delay_light_sound(self):
        # retourne un délai négatif entre la lumière et le son (au minimum -1)
        # si BPM = 15 , BPM/15=1, Log2 = 0, retourne -1, avance de 1 step
        # si BPM = 30 , BPM/15=2, Log2 = 1, retourne -2, avance de 2 step
        # si BPM = 60 , BPM/15=4, Log2 = 2, retourne -3, avance de 3 steps
        # si BPM = 84 , BPM/15=5.6, Log2 = 2.48..., retourne -3, avance de 3 steps
        # si BPM = 96 , BPM/15=6.4, Log2 = 2.67..., retourne -4, avance de 4 steps
        # si BPM = 120 , BPM/15=8, Log2 = 3, retourne -4, avance de 4 steps
        if( self.screen_bpm > 0 ):
            calc = round( -math.log2(self.screen_bpm/15) ) -2
        delay = calc if calc < -1 else -1
        return delay

    def on_press_start_button(self):
        self.mixer.set_audio_play()

    def on_press_stop_button(self):
        self.mixer.set_audio_stop()

    def on_screen_bpm(self, widget, value):
        # BPM_MIN et BPM_MAX testé directement dans .kv
        # pour éviter l'appel à cette fonction si cela n'est pas nécessaire
        self.mixer.ask_new_bpm( self.screen_bpm )

class MrBeatApp(App):
    pass

MrBeatApp().run()