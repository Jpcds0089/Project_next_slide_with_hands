from pygame import mixer


class Pygame:
    def reproduzir(self, locations: [], connection):
        mixer.init()
        while True:
            msg = connection.recv()
            mixer.music.load(locations[int(msg) - 1])
            mixer.music.play()
            while mixer.music.get_busy() == True:
                if int(msg) == 0:
                    print("msg = 0")
                    mixer.music.pause()
                else:
                    continue
