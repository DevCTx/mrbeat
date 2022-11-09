import wave
from array import array


class Sound:
    filename = None         # nom du fichier .wav à ouvrir
    displayname = None      # nom à afficher dans l'interface Widget
    volume = 1

    frames = None           # tableau de frames en 16bits correspondant au fichier wav lu

    def __init__(self, filename, displayname, volume):
        self.filename = filename
        self.displayname = displayname
        self.volume = volume
        self.load_sound()

    def load_sound(self):
        wav_file = wave.open(self.filename, mode='rb')  # ouverture du fichier filename en lecture

        nb_frames = wav_file.getnframes()               # nb de fragments à lire du fichier .wav
        frames_bytes = wav_file.readframes(nb_frames)   # Lit max nb_frames et retourne une suite de bytes
        self.frames = array('h', frames_bytes)          # decoupe les bytes par serie de 2 (16bits)


class SoundKit:
    sounds = ()                     # Tupple de Sound à initialiser

    def get_nb_tracks(self):
        return len(self.sounds)

    def get_all_samples(self):
        all_samples = []
        # all_samples.clear()
        for i in range(0,len(self.sounds)):
            all_samples.append(self.sounds[i].frames)
        return all_samples

    def get_all_volumes(self):
        all_volumes = []
        # all_volumes.clear()
        for i in range(0,len(self.sounds)):
            all_volumes.append(self.sounds[i].volume)
        return all_volumes

class SoundKit1(SoundKit):
    # initialisation du Tupple de Sound
    sounds = ( Sound("sounds/kit1/kick.wav", "KICK", 1),
              Sound("sounds/kit1/clap.wav", "CLAP", 1),
              Sound("sounds/kit1/shaker.wav", "SHAKER", 10),
              Sound("sounds/kit1/snare.wav", "SNARE", 1),
              )

class SoundKit2(SoundKit):
    # initialisation du Tupple de Sound
    sounds = (  Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/clap.wav", "CLAP", 1),
                Sound("sounds/kit1/shaker.wav", "SHAKER", 10),
                Sound("sounds/kit1/snare.wav", "SNARE", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/clap.wav", "CLAP", 1),
                Sound("sounds/kit1/shaker.wav", "SHAKER", 10),
                Sound("sounds/kit1/snare.wav", "SNARE", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/clap.wav", "CLAP", 1),
                Sound("sounds/kit1/shaker.wav", "SHAKER", 10),
                Sound("sounds/kit1/snare.wav", "SNARE", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/clap.wav", "CLAP", 1),
                Sound("sounds/kit1/shaker.wav", "SHAKER", 10),
                Sound("sounds/kit1/snare.wav", "SNARE", 1),
                )

class SoundKit3(SoundKit):
    # initialisation du Tupple de Sound
    sounds = (  Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1),
                Sound("sounds/kit1/kick.wav", "KICK", 1))

class SoundKit4(SoundKit):
    # initialisation du Tupple de Sound
    sounds = ( Sound("sounds/kit1/kick.wav", "KICK", 1),
              Sound("sounds/kit1/clap.wav", "CLAP", 1),
              Sound("sounds/kit1/shaker.wav", "SHAKER", 10),
              Sound("sounds/kit1/snare.wav", "SNARE", 1),
              Sound("sounds/kit1/pluck.wav", "PLUCK", 1),
              Sound("sounds/kit1/bass.wav", "BASS", 1),
              )

class SoundKitAll(SoundKit):
    # initialisation du Tupple de Sound
    sounds = ( Sound("sounds/kit1/kick.wav", "KICK", 1),
              Sound("sounds/kit1/clap.wav", "CLAP", 1),
              Sound("sounds/kit1/shaker.wav", "SHAKER", 10),
              Sound("sounds/kit1/snare.wav", "SNARE", 1),
              Sound("sounds/kit1/bass.wav", "BASS", 1),
              Sound("sounds/kit1/effects.wav", "EFFECTS", 1),
              Sound("sounds/kit1/pluck.wav", "PLUCK", 1),
              Sound("sounds/kit1/vocal_chop.wav", "VOCAL", 1),
              )


class SoundKitService:
    soundkit = SoundKitAll()                      # bibliothèque de sons chargés en format 16 bits

    def get_nb_tracks(self):
        return self.soundkit.get_nb_tracks()

    def get_sound_at(self, index):
        if index < 0 or index >= len(self.soundkit.sounds):
            return None
        return self.soundkit.sounds[index]

    def get_all_samples(self):
        return self.soundkit.get_all_samples()

    def get_all_volumes(self):
        return self.soundkit.get_all_volumes()

