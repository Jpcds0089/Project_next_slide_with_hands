import cv2
import multiprocessing
import mediapipe as mp
from time import sleep
from scripts.Os import Os
from scripts.Pygame import Pygame


class Detector:
    def __init__(self):
        # Scripts
        self.Os = Os()
        self.Pygame = Pygame()

        self.video_capture = cv2.VideoCapture("http://192.168.0.101:4747/video")
        self.hand = mp.solutions.hands
        self.mpDrawn = mp.solutions.drawing_utils
        self.Hand = self.hand.Hands(max_num_hands=1,
                                    model_complexity=0,
                                    min_tracking_confidence=0.5,
                                    min_detection_confidence=0.5)

        # Folders
        self.init_folder = self.Os.pasta_atual()[0:-8].replace(r"\source", "")
        self.main_folders = {"songs": r"{}\data\songs".format(self.init_folder),
                             "configs": r"{}\data\configs".format(self.init_folder),
                             "imagens": r"{}\data\imagens".format(self.init_folder),
                             "programs": r"{}\data\programs".format(self.init_folder)}
        self.songs = {"beep1": r"{}\beep1.mp3".format(self.main_folders),
                      "beep2": r"{}\beep2.mp3".format(self.main_folders)}

        # Global variables
        self.millis = 0
        self.left_fingers_counter = 0
        self.right_fingers_counter = 0
        self.zona_livre = None
        self.left_hand = False
        self.right_hand = False
        self.reproduzindo = False
        self.ja_reproduziu = False
        self.acionamento_concluido = False
        self.posicao_inicial_da_mao = None
        self.fingers_points = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16], [17, 18, 19, 20]]
        self.fingerstips = [self.fingers_points[0][-1], self.fingers_points[1][-1], self.fingers_points[2][-1],
                            self.fingers_points[3][-1], self.fingers_points[4][-1]]

    def start(self):
        self.hands()

    def hands(self):
        while True:
            # Tratando a imagem
            check, image = self.video_capture.read()
            imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.Hand.process(imgRGB)

            # Obtendo classificação da mão e classificando-a em direita ou esquerda
            if results.multi_handedness is not None:
                hand_classification = str(results.multi_handedness[0])
                hand_classification_score = hand_classification.split("\n")[2].replace("score:", "").replace(" ", "")
                hand_classification_label = str(
                    hand_classification.split("\n")[3].replace("label:", "").replace(" ", "").replace('"', ''))

                # Classificando se é a mão direita ou esquerda
                if hand_classification_label == "Left" and float(hand_classification_score[0:3]) >= 0.7:
                    self.right_hand = True
                else:
                    self.right_hand = False
                if hand_classification_label == "Right" and float(hand_classification_score[0:3]) >= 0.7:
                    self.left_hand = True
                else:
                    self.left_hand = False

            # Obtendo pontos da mão e as suas cordenadas
            hand_points = results.multi_hand_landmarks
            h, w, _ = image.shape
            list_hand_points = []

            # Converter cordenadas da mão em pixels
            if hand_points:
                for points in hand_points:
                    self.mpDrawn.draw_landmarks(image, points, self.hand.HAND_CONNECTIONS)
                    for id, cord in enumerate(points.landmark):
                        cx, cy = int(cord.x * w), int(cord.y * h)
                        # cv2.putText(img, str(id), (cx, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        list_hand_points.append((cx, cy))

                self.left_fingers_counter = 0
                self.right_fingers_counter = 0

                if points:
                    # Lógica dos dedos da mão ESQUERDA
                    if self.left_hand:
                        # Lógica do dedão
                        if list_hand_points[4][0] < list_hand_points[2][0]:
                            self.left_fingers_counter += 1

                        # Lógica dos outros 4 dedos
                        for x in self.fingerstips[1::]:
                            if list_hand_points[0][1] > list_hand_points[5][1] and list_hand_points[0][1] > list_hand_points[9][1] or \
                                    list_hand_points[0][1] > list_hand_points[13][1] and \
                                    list_hand_points[0][1] > list_hand_points[17][1]:
                                if list_hand_points[x][1] < list_hand_points[x - 2][1]:
                                    self.left_fingers_counter += 1
                    else:
                        self.left_fingers_counter = 0

                    # Lógica dos dedos da mão DIREITA
                    if self.right_hand:
                        # Lógica do dedão
                        if list_hand_points[4][0] > list_hand_points[2][0]:
                            self.right_fingers_counter += 1

                        # Lógica dos outros 4 dedos
                        for x in self.fingerstips[1::]:
                            if list_hand_points[0][1] > list_hand_points[5][1] and \
                                    list_hand_points[0][1] > list_hand_points[9][1] or \
                                    list_hand_points[0][1] > list_hand_points[13][1] and \
                                    list_hand_points[0][1] > list_hand_points[17][1]:
                                if list_hand_points[x][1] < list_hand_points[x - 2][1]:
                                    self.right_fingers_counter += 1
                    else:
                        self.right_fingers_counter = 0

            # Deve haver um acionamento inicial para que o programa saiba que o ultilizador está tentando
            # execultar algum comando. Esse "acionamento inicial" será definido logo abaixo
            if hand_points:
                """
                if self.left_fingers_counter == 5:
                    sleep(0.001)
                    self.millis += 1
                    print(self.millis)

                    if self.millis == 1:
                        self.posicao_inicial_da_mao = list_hand_points[0]
                        self.zona_livre = int((list_hand_points[17][0] - list_hand_points[5][0]) * 2), int(
                            (list_hand_points[0][1] - list_hand_points[9][1]) * 2)

                    if self.posicao_inicial_da_mao[0] + self.zona_livre[0] > list_hand_points[0][0] > self.posicao_inicial_da_mao[0] - \
                            self.zona_livre[0] and self.posicao_inicial_da_mao[1] + self.zona_livre[1] > list_hand_points[1][1] > \
                            self.posicao_inicial_da_mao[1] - self.zona_livre[1]:
                        cv2.putText(image, str("Dentro da zona"), (6, 470), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)

                        if 2 <= self.millis <= 60:
                            if self.ja_reproduziu:
                                self.reproduzindo = False
                                self.ja_reproduziu = False
                                self.acionamento_concluido = True
                            else:
                                if not self.reproduzindo:
                                    ja_reproduziu = multiprocessing.Process(target=Pygame.reproduzir,
                                                                            args=(self.songs["beep2"],))
                                    if __name__ == "__main__":
                                        ja_reproduziu.start()
                                        print('Status de "ja_reproduziu":', ja_reproduziu)
                                        self.reproduzindo = True

                    else:
                        self.millis = 0
                        self.zona_livre = 0
                        self.posicao_inicial_da_mao = 0
                        cv2.putText(image, str("Fora da zona"), (6, 470), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

                else:
                    self.millis = 0
                    self.zona_livre = 0
                    self.posicao_inicial_da_mao = 0
                """

                # Caso o acionamento esteja concluído, definir qual gesto o ultilizador está fazendo
                if self.acionamento_concluido:
                    self.Pygame.reproduzir(self.songs["beep2"])
                    self.acionamento_concluido = False

                # Desenhando na tela o número de dedos
                if self.left_hand:
                    cv2.putText(image, str(self.right_fingers_counter + self.left_fingers_counter), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 51, 51), 3)
                if self.right_hand:
                    cv2.putText(image, str(self.right_fingers_counter + self.left_fingers_counter), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (51, 255, 51), 3)

            # Abrindo janela
            res = cv2.resize(image, dsize=(800, 600), interpolation=cv2.INTER_CUBIC)
            cv2.imshow("imagem", res)
            cv2.waitKey(1)


bot = Detector()
bot.start()
