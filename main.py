import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.audio import SoundLoader

import cv2
import numpy as np
from ultralytics import YOLO

# Cargar modelo YOLOv8 ligero
model = YOLO('yolov8n.pt')

OBJETOS_PRIORITARIOS = {
    0: 'Persona', 1: 'Bicicleta', 2: 'Coche', 5: 'Autobús', 7: 'Camión',
    11: 'Semáforo', 13: 'Señal', 15: 'Banco', 56: 'Silla', 57: 'Sofá',
    59: 'Cama', 60: 'Mesa'
}

class CopilotoApp(App):
    def build(self):
        self.title = "Copiloto Uno"
        self.capturando = False
        self.ultima_deteccion_time = 0
        self.ultimo_texto = ""

        # Layout principal
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Encabezado
        self.lbl_titulo = Label(
            text="[b]COPILOTO UNO[/b]\nAsistente de Movilidad",
            markup=True,
            font_size='22sp',
            size_hint_y=0.15,
            halign='center'
        )
        layout.add_widget(self.lbl_titulo)

        # Visor de cámara (opcional para control)
        self.img_camara = Image(size_hint_y=0.55)
        layout.add_widget(self.img_camara)

        # Etiqueta de estado y alertas
        self.lbl_estado = Label(
            text="Presiona el botón para iniciar",
            font_size='16sp',
            size_hint_y=0.15,
            halign='center'
        )
        layout.add_widget(self.lbl_estado)

        # Botón de control gigante
        self.btn_control = Button(
            text="INICIAR COPILOTO",
            font_size='20sp',
            bold=True,
            size_hint_y=0.15,
            background_color=(0, 0.9, 0.4, 1)
        )
        self.btn_control.bind(on_press=self.toggle_sistema)
        layout.add_widget(self.btn_control)

        return layout

    def toggle_sistema(self, instance):
        if not self.capturando:
            # Iniciar cámara trasera (índice 0 o 1 según el dispositivo)
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                self.capture = cv2.VideoCapture(1)

            if self.capture.isOpened():
                self.capturando = True
                self.btn_control.text = "DETENER COPILOTO"
                self.btn_control.background_color = (0.9, 0.2, 0.2, 1)
                self.lbl_estado.text = "Sistema activo. Vigilando vía pública..."
                
                # Programar actualización de fotogramas (30 fps)
                Clock.schedule_interval(self.actualizar_entorno, 1.0 / 30.0)
            else:
                self.lbl_estado.text = "Error: No se pudo acceder a la cámara"
        else:
            self.capturando = False
            Clock.unschedule(self.actualizar_entorno)
            if hasattr(self, 'capture'):
                self.capture.release()
            self.btn_control.text = "INICIAR COPILOTO"
            self.btn_control.background_color = (0, 0.9, 0.4, 1)
            self.lbl_estado.text = "Sistema detenido"

    def actualizar_entorno(self, dt):
        ret, frame = self.capture.read()
        if not ret or frame is None:
            return

        ancho_pantalla = frame.shape[1]
        alto_pantalla = frame.shape[0]
        area_total = ancho_pantalla * alto_pantalla

        results = model(frame, stream=True, verbose=False)

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                if cls_id in OBJETOS_PRIORITARIOS and conf > 0.45:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    centro_x = (x1 + x2) // 2
                    area_objeto = (x2 - x1) * (y2 - y1)
                    proporcion_area = area_objeto / area_total

                    if proporcion_area > 0.025:
                        if centro_x < ancho_pantalla * 0.35:
                            posicion = "a la izquierda"
                        elif centro_x > ancho_pantalla * 0.65:
                            posicion = "a la derecha"
                        else:
                            posicion = "al frente"

                        if proporcion_area > 0.18:
                            distancia_texto = "muy cerca, atención"
                            es_emergencia = True
                        elif proporcion_area > 0.07:
                            distancia_texto = "cerca"
                            es_emergencia = False
                        else:
                            distancia_texto = "a cierta distancia"
                            es_emergencia = False

                        nombre = OBJETOS_PRIORITARIOS[cls_id]
                        
                        if es_emergencia:
                            texto_voz = f"Peligro, {nombre} {distancia_texto} {posicion}"
                            tiempo_espera = 1.0
                        else:
                            texto_voz = f"{nombre} {distancia_texto}, {posicion}"
                            tiempo_espera = 2.2

                        if time.time() - self.ultima_deteccion_time > tiempo_espera:
                            self.ultima_deteccion_time = time.time()
                            self.lbl_estado.text = f"Alerta: {texto_voz}"
                            # En Android, se llama a la síntesis de voz nativa (pyttsx3 / plyer / android TTS)

                        color = (0, 0, 255) if es_emergencia else (0, 255, 0)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, texto_voz, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Mostrar fotograma en la interfaz Kivy
        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
        self.img_camara.texture = texture

    def on_stop(self):
        if hasattr(self, 'capture') and self.capture.isOpened():
            self.capture.release()

if __name__ == '__main__':
    CopilotoApp().run()
