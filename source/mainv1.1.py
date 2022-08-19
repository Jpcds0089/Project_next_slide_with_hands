import cv2
import mediapipe as mp
from time import sleep
from scripts.Os import Os
from scripts.Pygame import Pygame


# Variáveis globais
video = cv2.VideoCapture("http://192.168.0.101:4747/video")
hand = mp.solutions.hands
Hand = hand.Hands(max_num_hands=1, model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDrawn = mp.solutions.drawing_utils

Os = Os()
millis = 0
Pygame = Pygame()
pasta_inicial = Os.pasta_atual()[0:-8].replace(r"\source", "")
acionamento_concluido = False
pasta_beep1 = r"{}\data\songs\beep1.mp3".format(pasta_inicial)
pasta_beep2 = r"{}\data\songs\beep2.mp3".format(pasta_inicial)
print(pasta_beep1, pasta_beep2)

while True:
    # Tratando a imagem
    check, img = video.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = Hand.process(imgRGB)

    # Pontos da mão
    handsPoints = results.multi_hand_landmarks
    h, w, _ = img.shape
    pontos = []

    # Obter cordenadas dos pontos da mão e converte-las em pixels
    if handsPoints:
        for points in handsPoints:
            mpDrawn.draw_landmarks(img, points, hand.HAND_CONNECTIONS)
            for id, cord in enumerate(points.landmark):
                cx, cy = int(cord.x * w), int(cord.y * h)
                # cv2.putText(img, str(id), (cx, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                pontos.append((cx, cy))

        # Lógica da contagem dos dedos levantados
        contador = 0
        dedos = [8, 12, 16, 20]
        if points:
            # Lógica do dedão
            if pontos[4][0] < pontos[2][0]:
                contador += 1

            # Lógica dos outros 4 dedos
            for x in dedos:
                if pontos[0][1] > pontos[5][1] and pontos[0][1] > pontos[9][1] or pontos[0][1] > pontos[13][1] and \
                        pontos[0][1] > pontos[17][1]:
                    if pontos[x][1] < pontos[x - 2][1]:
                        contador += 1

        # Deve haver um acionamento inicial para que o programa saiba que o ultilizador está tentando
        # execultar algum comando. Esse "acionamento inicial" será definido logo abaixo
        if contador == 5:
            sleep(0.001)
            millis += 1
            print(millis)

            if millis == 1:
                posicao_inicial_da_mao = pontos[0]
                zona_livre = int((pontos[17][0] - pontos[5][0]) * 2), int((pontos[0][1] - pontos[9][1]) * 2)

            #cv2.rectangle(img,
            #              (posicao_inicial_da_mao[0] - zona_livre[0],
            #               posicao_inicial_da_mao[1] - zona_livre[1]),
            #              (posicao_inicial_da_mao[0] + zona_livre[0],
            #               posicao_inicial_da_mao[1] + zona_livre[1]),
            #              (255, 0, 0), -1)
            if posicao_inicial_da_mao[0] + zona_livre[0] > pontos[0][0] > posicao_inicial_da_mao[0] - zona_livre[0] \
                    and posicao_inicial_da_mao[1] + zona_livre[1] > pontos[1][1] > posicao_inicial_da_mao[1] - zona_livre[1]:
                cv2.putText(img, str("Dentro da zona"), (1, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)
                if millis >= 31:
                    Pygame.reproduzir(pasta_beep1)
                    acionamento_concluido = True
            else:
                millis = 0
                zona_livre = 0
                posicao_inicial_da_mao = 0
                cv2.putText(img, str("Fora da zona"), (1, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1)

        else:
            millis = 0
            zona_livre = 0
            posicao_inicial_da_mao = 0

        # Caso o acionamento esteja concluído, definir qual gesto o ultilizador está fazendo
        if acionamento_concluido:
            Pygame.reproduzir(pasta_beep2)

        # Escrevendo na tela o número de dedos na tela
        cv2.putText(img, str(contador), (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 0, 0), 5)
        #cv2.rectangle(img, (80, 10), (200, 110), (10, 10, 10), -1)

    # Abrindo janela
    res = cv2.resize(img, dsize=(800, 600), interpolation=cv2.INTER_CUBIC)
    cv2.imshow("imagem", res)
    cv2.waitKey(1)
