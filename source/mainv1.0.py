import cv2
from time import sleep
import mediapipe as mp
import multiprocessing
from pygame import mixer


def reproduzir(location: str, connection):
    mixer.init()
    mixer.music.load(location)

    while 1:
        print("Esperando resposta")
        msg = connection.recv()
        print("Mensagem recebida:", msg)
        if msg == "1":
            print("Iniciando reprodução")
            mixer.music.play()
            while mixer.music.get_busy() == True:
                continue
            print("Finalizou reprodução")
            return True


def sender(conn, msgs):
    for msg in msgs:
        conn.send(msg)
        print("Sent the message: {}".format(msg))
    conn.close()


video = cv2.VideoCapture("http://192.168.0.101:4747/video")
hand = mp.solutions.hands
Hand = hand.Hands(max_num_hands=1, model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDrawn = mp.solutions.drawing_utils
count = 0

if __name__ == "__main__":
    parent_conn, child_conn = multiprocessing.Pipe()
    multiprocessing.Process(target=reproduzir, args=(r"C:\Users\jp000\PycharmProjects\My Projects\pythonProjectDetectorDeMãos\data\songs\beep2.mp3", child_conn)).start()

    while True:
        # Tratando a imagem
        check, img = video.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = Hand.process(imgRGB)

        # Classificando mão
        if results.multi_handedness is not None:
            hand_classification = str(results.multi_handedness[0])
            hand_classification_score = hand_classification.split("\n")[2].replace("score:", "").replace(" ", "")
            hand_classification_label = str(hand_classification.split("\n")[3].replace("label:", "").replace(" ", "").replace('"', ''))
            #print(hand_classification_label)
            #print("Left")

            # Classificando se é a mão direita ou esquerda
            if hand_classification_label == "Left" and float(hand_classification_score[0:3]) >= 0.8:
                ...
            if hand_classification_label == "Right" and float(hand_classification_score[0:3]) >= 0.8:
                ...

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
                    cv2.putText(img, str(id), (cx + 3, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
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
                    if pontos[0][1] < pontos[5][1] and pontos[0][1] < pontos[9][1] or pontos[0][1] < pontos[13][1] and \
                            pontos[0][1] < pontos[17][1]:
                        if pontos[x][1] > pontos[x - 2][1]:
                            contador += 1
                    elif pontos[0][1] > pontos[5][1] and pontos[0][1] > pontos[9][1] or pontos[0][1] > pontos[13][1] and \
                            pontos[0][1] > pontos[17][1]:
                        if pontos[x][1] < pontos[x - 2][1]:
                            contador += 1

                if contador == 4:
                    sleep(0.001)
                    count += 1
                    print(count)
                    if count == 30:
                        #multiprocessing.Process(target=sender, args=(parent_conn, "1")).start()
                        parent_conn.send("1")
                        count = -100


            # Escrevendo na tela o número de dedos na tela
            cv2.putText(img, str(contador), (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 0, 0), 5)
            #cv2.rectangle(img, (80, 10), (200, 110), (255, 0, 0), -1)

        cv2.imshow("imagem", img)
        cv2.waitKey(1)
