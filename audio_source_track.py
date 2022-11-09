from array import array

from audiostream.sources.thread import ThreadSource

# Son sur 16 bits  / Devrait être mutualisé vev AudioSourceOneShot
AudioSourceTrack_MAX = 0x7FFF  # moitié positive de 16 bits (Saturation haute)
AudioSourceTrack_MIN = -0x7FFF  # moitié négative de 16 bits (Saturation basse)


class AudioSourceTrack(ThreadSource):
    index_ext = 0               # index d'identification extérieure
    wav_frames = None           # fichier wav découpé en frames de 16 bits
    nb_wav_frames = 0           # nombre de frames contenu dans le tableau wav_frames
    wav_frame_index = 0         # index de lecture du fichier wav
    wav_volume = 1              # coefficient de volume permettant de jouer plus ou moins ford le son passé

    min_bpm = 1                 # vitesse de lecture minimale (1 par min)
    bpm = 0                     # vitesse de lecture (60 par défaut)
    fps = 0                     # sample_rate / frames par secondes (22050 par défaut)
    nb_frames_per_step=0        # step_nb_samples / nombre de frames par step
    nb_frames_per_step_max=0    # buffer_nb_samples / nombre de frames par step max pour définir la taille du buffer max
    track_buffer = None         # buffer de nb_frames_per_step_max * 16 bits, à remplir à 0 si non utilisé
    silent_buffer = None        # buffer de nb_frames_per_step_max * 16 bits, rempli à 0, utilisé pour optimisation
    saturation = 0

    steps_sequence = ()         # séquence de NB_TRACK_STEPS à jouer
    current_step_index = 0      # index du dernier step envoyé dans le buffer (0 à NB_TRACK_STEPS-1)

    def __init__(self, output_stream, index_ext, wav_frames, wav_volume, bpm, min_bpm, fps, *args, **kwargs):
        ThreadSource.__init__(self, output_stream, *args, **kwargs)

        self.index_ext = index_ext
        self.init_wav_frames(wav_frames, wav_volume)
        self.fps = fps if fps > 0 else 22050

        # definition d'un buffer de taille maximal en fonction du min_bpm
        self.set_track_and_silent_buffer_and_min_bpm(min_bpm)

        # mais utilisation d'une partie seulement selon le bpm en cours
        self.set_track_bpm_and_nb_frames_per_step(bpm)

        self.steps_sequence = ()

    def init_wav_frames(self,wav_frames,wav_volume):
        # Attention à l'ordre d'appel des fonctions car get_bytes est appelé en parallèle
        self.saturation_track = 0
        # Modifie le volume de chaque byte du wav_frames et vérifie la saturation du volume
        self.wav_frames = array('h', map(self.map_check_volume, map(lambda x: x * wav_volume, wav_frames)))
        # if self.saturation_track > 0 :
        #     print( f"self.saturation_track : {self.saturation_track}" )
        self.wav_frame_index = len(wav_frames) # FIX : pour éviter de jouer au démarrage de l'application
        self.nb_wav_frames = len(wav_frames)

    def set_track_and_silent_buffer_and_min_bpm(self, min_bpm):
        self.min_bpm = min_bpm if min_bpm > 1 else 1    # minimum acceptable pour les frames
        self.nb_frames_per_step_max = self.compute_nb_frames_per_step(self.min_bpm)
        self.silent_buffer = array('h', b"\x00\x00" * self.nb_frames_per_step_max)
        self.track_buffer = array('h', b"\x00\x00" * self.nb_frames_per_step_max)

    def set_track_bpm_and_nb_frames_per_step(self, bpm):
        self.bpm = bpm if bpm >= self.min_bpm else 60    # valeur par défaut (1 bat par seconde)
        self.nb_frames_per_step =self.compute_nb_frames_per_step(self.bpm)

    def compute_nb_frames_per_step(self, bpm_value):
        nb_frames_per_step = 0
        if bpm_value > 0 :
            # 44100 F/s à 120 B/min = 44100 F/s pour 2 B/s = 22050 F/B = 5512 F/Step
            # 22050 F/s à 120 B/min = 22050 F/s pour 2 B/s = 11025 F/B = 2756 F/Step
            # 44100 F/s à 60 B/min = 44100 F/s pour 1 B/s = 44100 F/B = 11025 F/Step
            # 22050 F/s à 60 B/min = 22050 F/s pour 1 B/s = 22050 F/B = 5512 F/Step
            # nb_frames_per_step = fps*60 / (4*bpm)
            nb_frames_per_step = int(self.fps*15/bpm_value)
        return nb_frames_per_step

    def set_track_sequence(self,steps_sequence):
        if len(steps_sequence) != len(self.steps_sequence):
            self.current_step_index = 0
        self.steps_sequence = steps_sequence

    def no_step_activated(self):
        # Retourne Vrai si aucune sequence initialisée, ou
        # si une sequence a été initialisée mais que aucun step n'est activé
        for i in range(0, len(self.steps_sequence)):
            if self.steps_sequence[i]==1:
                return False
        return True

    def map_check_volume(self, wav_byte):
        if wav_byte >= AudioSourceTrack_MAX:
            self.saturation_track += 1
            return AudioSourceTrack_MAX
        elif wav_byte <= AudioSourceTrack_MIN:
            self.saturation_track += 1
            return AudioSourceTrack_MIN
        else:
            return wav_byte

    # Fonction appelée en parallèle par le ThreadSource
    # pour implémenter le buffer de la carte son avec des paquets
    def get_bytes_array(self, get_bytes_step_index):
        buf_temp = None

        # si le step de la sequence est activé, on lit le son depuis le début
        if self.steps_sequence[get_bytes_step_index] == 1:
            self.wav_frame_index = 0

        # on retourne du silence si le fichier a été entièrement lu ou si aucun fichier n'est à lire
        if self.wav_frame_index >= self.nb_wav_frames :
            buf_temp = self.silent_buffer[0:self.nb_frames_per_step]
        else:
            # si le reste à lire du fichier wav est plus grand ou égale au step
            #    recopier une partie du wav, d'une taille de step, en commençant par l'index wav actuel
            #    incrementer le wav d'un step
            if self.wav_frame_index + self.nb_frames_per_step <= self.nb_wav_frames :
                self.track_buffer = self.wav_frames[self.wav_frame_index:self.wav_frame_index+self.nb_frames_per_step]
                self.wav_frame_index += self.nb_frames_per_step

            # si le reste du fichier wav est plus petit que 1 step
            #    recopier une partie du wav, de la taille du wav restant, en commençant par l'index wav actuel
            #    completer le buffer avec du silence, et incrementer le wav de la taille du wav restant
            else:
                self.track_buffer = self.wav_frames[self.wav_frame_index:self.nb_wav_frames]
                self.track_buffer.extend(
                    self.silent_buffer[0:self.nb_frames_per_step-(self.nb_wav_frames-self.wav_frame_index)])
                self.wav_frame_index += self.nb_wav_frames-self.wav_frame_index

            buf_temp = self.track_buffer[0:self.nb_frames_per_step]

        return buf_temp

    # Fais la même chose que get_bytes_array excepté que cela retourne les bytes
    # cette fonction est appelé par la carte son et donc nécessite les bytes
    # alors que get_bytes_array est appelé par le mixeur qui veut garder le buffer
    def get_bytes (self, *args, **kwargs):
        return self.get_bytes_array(0).tobytes()
