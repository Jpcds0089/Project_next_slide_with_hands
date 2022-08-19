import cv2
from json import loads
import multiprocessing
import mediapipe as mp
from time import sleep
from scripts.Os import Os
from scripts.Pygame import Pygame
from scripts.Pyautogui import Pyautogui


class Detector:
    def __init__(self):
        # Scripts
        self.Os = Os()
        self.Pygame = Pygame()
        self.Pyautogui = Pyautogui()

        # Folders
        self.init_folder = self.Os.pasta_atual()[0:-8].replace(r"\source", "")
        self.main_folders = {"songs": r"{}\data\songs".format(self.init_folder),
                             "configs": r"{}\data\configs".format(self.init_folder),
                             "imagens": r"{}\data\imagens".format(self.init_folder),
                             "programs": r"{}\data\programs".format(self.init_folder)}
        self.songs = {"beep1": r"{}\beep1.mp3".format(self.main_folders["songs"]),
                      "beep2": r"{}\beep2.mp3".format(self.main_folders["songs"])}

        # Importando configurações
        self.init_configs = loads(open(r"{}\config.json".format(self.main_folders["configs"])).read())

        # Mediapipe
        self.video_capture = cv2.VideoCapture(self.init_configs["video_capture"])
        self.hand = mp.solutions.hands
        self.mpDrawn = mp.solutions.drawing_utils
        self.Hand = self.hand.Hands(max_num_hands=1,
                                    model_complexity=0,
                                    min_tracking_confidence=0.5,
                                    min_detection_confidence=0.5)

        # Global variables
        self.millis = 0
        self.in_zone = None
        self.safe_zone = None
        self.left_hand = False
        self.right_hand = False
        self.reproduzindo = False
        self.ja_reproduziu = False
        self.command_executed = None
        self.left_fingers_counter = 0
        self.right_fingers_counter = 0
        self.acionamento_concluido = False
        self.posicao_inicial_da_mao = None
        self.time_to_decid = self.init_configs["time_to_decid"]
        self.delay_for_soung = self.init_configs["delay_for_soung"]
        self.time_to_define_if_the_hand_is_left = self.init_configs["time_to_define_if_the_hand_is_left_or_right"]
        self.time_to_define_if_the_hand_is_right = self.init_configs["time_to_define_if_the_hand_is_left_or_right"]
        self.fingers_points = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16], [17, 18, 19, 20]]
        self.fingerstips = [self.fingers_points[0][-1], self.fingers_points[1][-1], self.fingers_points[2][-1], self.fingers_points[3][-1], self.fingers_points[4][-1]]

        # Multiprocessos
        self.parent_conn, self.child_conn = multiprocessing.Pipe()
        multiprocessing.Process(target=self.Pygame.reproduzir, args=([self.songs["beep1"], self.songs["beep2"]], self.child_conn)).start()

    def start(self):
        self.hands()

    def hands(self):
        global points
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

                # Classificando se é a mão direita do user
                if hand_classification_label == "Left" and float(hand_classification_score[0:3]) >= 0.7:
                    sleep(0.001)
                    self.time_to_define_if_the_hand_is_right -= 1
                    if self.time_to_define_if_the_hand_is_right == self.init_configs["time_to_define_if_the_hand_is_left_or_right"] - 5:
                        self.right_hand = True
                    if self.time_to_define_if_the_hand_is_right <= 0:
                        self.right_hand = True
                        self.time_to_define_if_the_hand_is_right = self.init_configs["time_to_define_if_the_hand_is_left_or_right"]
                else:
                    self.right_hand = False

                # Classificando se é a mão esquerda do user
                if hand_classification_label == "Right" and float(hand_classification_score[0:3]) >= 0.7:
                    self.time_to_define_if_the_hand_is_left -= 1
                    if self.time_to_define_if_the_hand_is_left == self.init_configs["time_to_define_if_the_hand_is_left_or_right"] - 5:
                        self.right_hand = True
                    if self.time_to_define_if_the_hand_is_left <= 0:
                        self.right_hand = True
                        self.time_to_define_if_the_hand_is_left = self.init_configs["time_to_define_if_the_hand_is_left_or_right"]
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
                            if list_hand_points[0][1] > list_hand_points[5][1] and list_hand_points[0][1] > list_hand_points[9][1] or list_hand_points[0][1] > list_hand_points[13][1] and list_hand_points[0][1] > list_hand_points[17][1]:
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
                            if list_hand_points[0][1] > list_hand_points[5][1] and list_hand_points[0][1] > list_hand_points[9][1] or list_hand_points[0][1] > list_hand_points[13][1] and list_hand_points[0][1] > list_hand_points[17][1]:
                                if list_hand_points[x][1] < list_hand_points[x - 2][1]:
                                    self.right_fingers_counter += 1
                    else:
                        self.right_fingers_counter = 0

                # Deve haver um acionamento inicial para que o programa saiba que o ultilizador está tentando
                # execultar algum comando. Esse "acionamento inicial" será definido logo abaixo
                if self.right_fingers_counter == 5 or self.left_fingers_counter == 5 or self.time_to_decid + 1 <= self.millis <= self.time_to_decid * 3:
                    self.millis += 1
                    print(self.millis)

                    # Guardando posição inicial da mão e definindo largura e altura da safe_zone que será criada
                    if self.millis == 1:
                        self.command_executed = False
                        self.posicao_inicial_da_mao = list_hand_points[0]
                        if self.right_fingers_counter == 5:
                            self.safe_zone = int((list_hand_points[5][0] - list_hand_points[17][0]) * 2), int((list_hand_points[0][1] - list_hand_points[9][1]) * 2)
                        elif self.left_fingers_counter == 5:
                            self.safe_zone = int((list_hand_points[17][0] - list_hand_points[5][0]) * 2), int((list_hand_points[0][1] - list_hand_points[9][1]) * 2)

                    # Criando uma "safe_zone" para a mão
                    elif self.millis > 1:
                        if self.posicao_inicial_da_mao[0] + self.safe_zone[0] > list_hand_points[0][0] > self.posicao_inicial_da_mao[0] - self.safe_zone[0] and self.posicao_inicial_da_mao[1] + self.safe_zone[1] > list_hand_points[1][1] > self.posicao_inicial_da_mao[1] - self.safe_zone[1]:
                            self.in_zone = True
                        else:
                            self.safe_zone = 0
                            self.in_zone = False
                            self.posicao_inicial_da_mao = 0
                            self.millis = -abs(int(self.time_to_decid * 2))

                    # Lógica do acionamento
                    if self.in_zone and self.millis > 1:
                        cv2.putText(image, str("Dentro da zona"), (6, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        if 2 <= self.millis <= self.time_to_decid:
                            cv2.putText(image, str("Fique parado"), (250, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                            if self.delay_for_soung >= self.init_configs["delay_for_soung"]:
                                self.parent_conn.send("1")
                                self.delay_for_soung = 0
                            self.delay_for_soung += 1
                        elif self.time_to_decid + 1 == self.millis:
                            self.parent_conn.send("2")
                            self.acionamento_concluido = True
                    else:
                        cv2.putText(image, str("Fora da zona"), (6, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    # Lógica da execulsão do comando
                    if self.acionamento_concluido and not self.command_executed:
                        if self.time_to_decid + 2 <= self.millis <= self.time_to_decid * 3:
                            cv2.putText(image, str("Execulte o comando"), (200, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

                            # Execultando comandos
                            if self.right_hand:
                                if self.right_fingers_counter == 0:
                                    self.Pyautogui.pressionar("right")
                                    self.command_executed = True
                            elif self.left_hand:
                                if self.left_fingers_counter == 0:
                                    self.Pyautogui.pressionar("left")
                                    self.command_executed = True
                            elif self.command_executed:
                                self.millis = 0
                                self.safe_zone = 0
                                self.delay_for_soung = 0
                                self.parent_conn.send("0")
                                self.posicao_inicial_da_mao = 0

                        elif self.millis > self.time_to_decid * 3:
                            cv2.putText(image, str("Nenhum comando encontrado"), (140, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

                else:
                    self.millis = 0
                    self.safe_zone = 0
                    self.delay_for_soung = 0
                    self.parent_conn.send("0")
                    self.posicao_inicial_da_mao = 0

                # Desenhando na tela o número de dedos
                if self.left_hand:
                    cv2.putText(image, str(self.right_fingers_counter + self.left_fingers_counter), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 51, 51), 3)
                if self.right_hand:
                    cv2.putText(image, str(self.right_fingers_counter + self.left_fingers_counter), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (51, 255, 51), 3)

            # Abrindo janela
            res = cv2.resize(image, dsize=(800, 600), interpolation=cv2.INTER_CUBIC)
            cv2.imshow("imagem", res)
            cv2.waitKey(1)


if __name__ == "__main__":
    bot = Detector()
    bot.start()
