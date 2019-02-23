from pygame import mixer

class SoundController:

    def __init__(self):

        mixer.pre_init()
        self.initializeSounds()

    def initializeSounds(self):
        # load all the sounds
        mixer.init()

        # self.channel1 = mixer.Channel(1)
        soundRepository = "./sounds/"

        # .mp3 and .wav files aren't working in PyGame, only .ogg
        soundFileAnnoyed = "8ANNOYED.ogg"
        self.soundAnnoyed = mixer.Sound(soundRepository + soundFileAnnoyed)

        soundFileWhistle = "4WOLFWSTL.ogg"
        self.soundWhistle = mixer.Sound(soundRepository + soundFileWhistle)

        soundFileWorried = "26OOH2.ogg"
        self.soundWorried = mixer.Sound(soundRepository + soundFileWorried)

        soundFileScream = "1SCREAM2.ogg"
        self.soundScream = mixer.Sound(soundRepository + soundFileScream)


    def annoyed(self):
        print("sound annoyed")
        self.soundAnnoyed.play()

    def worried(self):
        print("sound worried")
        self.soundWorried.play()

    def whistle(self):
        print("sound whistle")
        self.soundWhistle.play()

    def scream(self):
        print("sound scream")
        self.soundScream.play()

    # start the controller
    def start(self):
        self.running = True

    def stop(self):
        print("[INFO] stopping SoundController")
        self.running = False