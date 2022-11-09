from array import array

from audiostream.sources.thread import ThreadSource

# Son sur 16 bits / Devrait être mutualisé vev AudioSourceTrack
AudioSourceOneShot_MAX = 0x7FFF  # moitié positive de 16 bits (Saturation haute)
AudioSourceOneShot_MIN = -0x7FFF  # moitié négative de 16 bits (Saturation basse)

class AudioSourceOneShot(ThreadSource):
    NB_16BITS_BUFFER = 32       # nombre de paquets de 16bits à envoyer dans le buffer
    oneshot_buffer = None               # buffer de NB_16BITS_PACKET, à remplir à 0 si non utilisé

    wav_frames = None           # fichier wav découpé en frames de 16 bits
    nb_wav_frames = 0           # nombre de frames contenu dans le tableau wav_frames
    wav_frame_index = 0         # index de lecture du fichier wav

    wav_volume = 0              # Volume à laquet doit être joué ces frames

    get_bytes_index = 0

    def __init__(self, output_stream, *args, **kwargs):
        ThreadSource.__init__(self, output_stream, *args, **kwargs)

        # remplissage du buffer avec NB_16BITS_PACKET * 2 bytes (16bits) de 0
        self.oneshot_buffer = array('h', b"\x00\x00" * self.NB_16BITS_BUFFER)


    def set_wav_frames(self,wav_frames, wav_volume):
        # Attention à l'ordre d'appel des fonctions car get_bytes est appelé en parallèle
        self.wav_frames = wav_frames
        self.wav_volume = wav_volume
        self.wav_frame_index = 0
        self.nb_wav_frames = len(wav_frames)


    # Fonction appelée en parallèle par le ThreadSource
    # pour implémenter le buffer de la carte son avec des steps(paquets)
    def get_bytes (self, *args, **kwargs):
        if self.nb_wav_frames > 0:                              # On a un fichier wav à lire
            if self.wav_frame_index >= self.nb_wav_frames:      # On a déjà tout chargé dans le buffer donc reinit
                # reinitialisation des buffer et variables du wav à 0
                self.nb_wav_frames = 0
                self.wav_frame_index = 0
                for buffer_index in range ( 0, self.NB_16BITS_BUFFER):     # On réinitialise le buffer à 0 une seule fois
                    self.oneshot_buffer[buffer_index] = 0
            else:
                for buffer_index in range ( 0, self.NB_16BITS_BUFFER):        # On parcours le buffer
                    # On verifie qu'on n'est pas à la fin du wav sinon 0
                    if self.wav_frame_index < self.nb_wav_frames:

                        # Gestion du volume sur 16 bits, dans le cas où le volume d'un wav serait extremement fort
                        new_wav_byte = self.wav_frames[self.wav_frame_index] * self.wav_volume
                        if new_wav_byte >= AudioSourceOneShot_MAX:
                            self.oneshot_buffer[buffer_index] = AudioSourceOneShot_MAX
                        elif new_wav_byte <= AudioSourceOneShot_MIN:
                            self.oneshot_buffer[buffer_index] = AudioSourceOneShot_MIN
                        else:
                            self.oneshot_buffer[buffer_index] = new_wav_byte

                        # valide la frame lue
                        self.wav_frame_index += 1
                    else:
                        # Buffer à remplir à 0 jusqu'à la fin si fichier terminé
                        self.oneshot_buffer[buffer_index] = 0

        return self.oneshot_buffer.tobytes()

