from array import array
from functools import partial

from audiostream.sources.thread import ThreadSource
from kivy.clock import Clock

from audio_source_track import AudioSourceTrack, AudioSourceTrack_MAX, AudioSourceTrack_MIN

DEBUG_INIT = False

#   Mixer reçoit l'ensemble des son du kits -> Start (appelle à get_bytes)
#       get_bytes (géré par la carte son)
#           -> audio_source_track ( mais non start )
#               get_bytes (géré en interne à la main)
#           -> audio_source_track ( mais non start )
#               get_bytes (géré en interne à la main)
#           -> audio_source_track ( mais non start )
#               get_bytes (géré en interne à la main)
#           -> audio_source_track ( mais non start )
#               get_bytes (géré en interne à la main)
#
class AudioSourceMixer(ThreadSource):
    tracks = []     # Ensemble de AudioSourceTrack correspondant aux différents sons à jouer
    nb_steps = 0                    # Nombre de steps dans la sequence (identique pour tous les sons)

    bpm = 0
    min_bpm=0

    mixer_buffer = None             # buffer de NB_FRAMES_IN_CHUNK * 16 bits, à remplir à 0 si non utilisé
    silent_buffer = None            # buffer de NB_FRAMES_IN_CHUNK * 16 bits, rempli à 0, utilisé pour optimisation
    saturation = 0
    nb_frames_per_step=0            # step_nb_sample / nombre de frames par step
    nb_frames_per_step_max=0        # step_nb_sample / nombre de frames par step

    get_bytes_step_index = 0          # index du dernier step envoyé dans le buffer (0 à NB_TRACK_STEPS-1)
    on_clock_mixer_get_bytes = None   # Fonction appelée (si besoin) lors des changements de steps

    is_playing = False      # permet de savoir si le son doit être joué ou non

    def __init__(self, output_stream, all_wav_frames, all_wav_volumes,
                 bpm, min_bpm, fps, nb_steps, on_clock_mixer_get_bytes, *args, **kwargs):
        ThreadSource.__init__(self, output_stream, *args, **kwargs)

        self.tracks = []
        # self.tracks.clear()
        for i in range (0, len(all_wav_frames)):
            track = AudioSourceTrack(output_stream, i, all_wav_frames[i], all_wav_volumes[i], bpm, min_bpm, fps)
            track.set_track_sequence( (0,) * nb_steps)  # nombre de steps fix pour tous les sons du mixer

            if DEBUG_INIT:
                if i == 0 or i == 7 or i == 10 or i == 13 or i == 19 or i == 22 or i == 25 or i == 28 :
                    track.set_track_sequence( (1,0,0,0,0,0,0,0,) * 2)  # nombre de steps fix pour tous les sons du mixer
                if i == 1 or i == 4 or i == 11 or i == 14 or i == 18 or i == 21 or i == 24 or i == 31 :
                    track.set_track_sequence( (0,0,0,0,1,0,0,0,) * 2)  # nombre de steps fix pour tous les sons du mixer
                if i == 2 or i == 5 or i == 8 or i == 15 or i == 17 or i == 20 or i == 27 or i == 30 :
                    track.set_track_sequence( (0,0,1,1,0,0,1,1,) * 2)  # nombre de steps fix pour tous les sons du mixer
                if i == 3 or i == 6 or i == 9 or i == 12 or i == 16 or i == 23 or i == 26 or i == 29 :
                    track.set_track_sequence( (1,0,1,0,1,0,1,0,) * 2)  # nombre de steps fix pour tous les sons du mixer

            self.tracks.append(track)

        # initialisation du buffer avec une taille maximal en fonction du min_bpm (identique sur tous les tracks)
        self.set_mixer_buffer_and_min_bpm(min_bpm)

        # mais utilisation d'une partie de celui ci seulement selon le bpm en cours (identique également)
        self.set_mixer_bpm_and_nb_frames_per_step(bpm)
        self.bpm_new = self.bpm     # identique si aucun changement demandé

        self.nb_steps = nb_steps
        self.on_clock_mixer_get_bytes = on_clock_mixer_get_bytes


    def set_mixer_buffer_and_min_bpm(self, min_bpm):
        self.min_bpm = self.tracks[0].min_bpm
        self.nb_frames_per_step_max = self.tracks[0].nb_frames_per_step_max
        self.mixer_buffer = array('h', b"\x00\x00" * self.nb_frames_per_step_max)
        self.silent_buffer = array('h', b"\x00\x00" * self.nb_frames_per_step_max)

    def ask_new_bpm(self, bpm):
        self.bpm_new = bpm

    def set_mixer_bpm_and_nb_frames_per_step(self, bpm):
        for i in range(0, len(self.tracks)):
            self.tracks[i].set_track_bpm_and_nb_frames_per_step(bpm)
        self.bpm = self.tracks[0].bpm
        self.nb_frames_per_step = self.tracks[0].nb_frames_per_step

    def set_audio_play(self):
        self.is_playing = True

    def set_audio_stop(self):
        self.is_playing = False

    def sum_16bits(self, track_bytes):
        sum_bytes = sum(track_bytes)
        if sum_bytes >= AudioSourceTrack_MAX:
            self.saturation_mixer += 1
            return AudioSourceTrack_MAX
        elif sum_bytes <= AudioSourceTrack_MIN:
            self.saturation_mixer += 1
            return AudioSourceTrack_MIN
        else:
            return sum_bytes

    # Fonction appelée en parallèle par le ThreadSource
    # pour implémenter le buffer de la carte son avec des paquets
    def get_bytes (self, *args, **kwargs):
        # modification du bpm du mixeur et des tracks au nouvel appel de get_bytes uniquement
        # pour être certain que les tailles des track_buffers et du mixer_buffer soient les mêmes
        if self.bpm_new != self.bpm:
            self.set_mixer_bpm_and_nb_frames_per_step(self.bpm_new)

        if self.is_playing is False:
            self.mixer_buffer = self.silent_buffer[0:self.nb_frames_per_step]
        else :
            # fonction appelée à chaque changement de step (buffer = taille d'un step donc à chaque get_bytes)
            if self.on_clock_mixer_get_bytes is not None:
                # declenche un évenement pour que la fonction passée soit lu dès que possible
                # la notion de partial permet de passer des éléments en paramètres à la fonction non connue pour le moment
                Clock.schedule_once(partial(self.on_clock_mixer_get_bytes, self.get_bytes_step_index), -1)

            track_buffers = []
            # track_buffers.clear()
            for i in range(0, len(self.tracks)):
                track = self.tracks[i]
                track_buffer = track.get_bytes_array(self.get_bytes_step_index)
                track_buffers.append(track_buffer)

            # Fait la somme de chaque byte des track_buffers et on vérifie si volume est saturé
            self.saturation_mixer = 0
            # self.mixer_buffer = array('h', map(self.map_check_volume_mixer, map(sum, zip(*track_buffers)) ))
            self.mixer_buffer = array('h', map(self.sum_16bits, zip(*track_buffers)) )
            # if (self.saturation_mixer > 0):
            #     print(f"saturation_mixer : {self.saturation_mixer} : step : {self.get_bytes_step_index}")

            # boucle sur la sequence
            self.get_bytes_step_index += 1
            if self.get_bytes_step_index >= self.nb_steps:
                self.get_bytes_step_index = 0

        if self.mixer_buffer is None:
            print("mixer_buffer is None")
        elif len(self.mixer_buffer) != self.nb_frames_per_step:
            print("len(self.mixer_buffer) != self.nb_frames_per_step")

        return self.mixer_buffer[0:self.nb_frames_per_step].tobytes()