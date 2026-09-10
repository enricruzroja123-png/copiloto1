import os
from flask import Flask, render_template_string, Response, jsonify
import cv2
import time
from ultralytics import YOLO

app = Flask(__name__)
model = YOLO('yolov8n.pt')

OBJETOS_PRIORITARIOS = {
    0: 'Persona', 1: 'Bicicleta', 2: 'Coche', 5: 'Autobús', 7: 'Camión',
    11: 'Semáforo', 13: 'Señal', 15: 'Banco', 56: 'Silla', 57: 'Sofá',
    59: 'Cama', 60: 'Mesa'
}

ultima_deteccion = {'texto': '', 'timestamp': 0}

def generar_frames():
    global ultima_deteccion
    # Intentar abrir la cámara del sistema
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

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

                    if proporcion_area > 0.03:
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

                        if time.time() - ultima_deteccion['timestamp'] > tiempo_espera:
                            ultima_deteccion = {'texto': texto_voz, 'timestamp': time.time()}

                        color = (0, 0, 255) if es_emergencia else (0, 255, 0)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                        cv2.putText(frame, texto_voz, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Copiloto Uno</title>
            <style>
                body { 
                    background: #121212; 
                    color: white; 
                    text-align: center; 
                    font-family: sans-serif; 
                    margin: 0; 
                    padding: 15px; 
                }
                h1 { font-size: 1.5rem; color: #00e676; margin-bottom: 15px; }
                img.feed { 
                    width: 100%; 
                    max-width: 640px; 
                    border-radius: 10px; 
                    border: 3px solid #00e676; 
                }
                #btnAudio { 
                    background: #00e676; 
                    color: black; 
                    border: none; 
                    padding: 15px 25px; 
                    font-weight: bold; 
                    font-size: 1.1rem; 
                    border-radius: 15px; 
                    margin-bottom: 15px; 
                    cursor: pointer; 
                }
            </style>
        </head>
        <body>
            <h1>COPILOTO UNO</h1>
            <button id="btnAudio" onclick="activarVoz()">Activar Audio de Voz</button><br>
            <img src="{{ url_for('video_feed') }}" class="feed">

            <script>
                let vozActivada = false;
                let ultimoTextoHablado = "";
                let estaHablando = false;

                function activarVoz() {
                    vozActivada = true;
                    const btn = document.getElementById('btnAudio');
                    btn.innerText = 'Audio Activado';
                    btn.style.background = '#00c853';
                    
                    if ('speechSynthesis' in window) {
                        window.speechSynthesis.resume();
                    }
                    hablar("Sistema Copiloto activado. Vigilando obstáculos.", true);
                }

                function hablar(texto, esEmergencia = false) {
                    if (!('speechSynthesis' in window)) return;

                    if (esEmergencia) {
                        window.speechSynthesis.cancel();
                        estaHablando = false;
                    }

                    if (estaHablando && !esEmergencia) return;

                    const mensaje = new SpeechSynthesisUtterance(texto);
                    mensaje.lang = 'es-ES';
                    mensaje.rate = esEmergencia ? 1.35 : 1.15;

                    mensaje.onstart = () => { estaHablando = true; };
                    mensaje.onend = () => { estaHablando = false; };
                    mensaje.onerror = () => { estaHablando = false; };

                    window.speechSynthesis.speak(mensaje);
                }

                setInterval(() => {
                    if (!vozActivada) return;
                    fetch('/alerta_audio')
                        .then(res => res.json())
                        .then(data => {
                            if (data.texto && data.texto !== ultimoTextoHablado) {
                                ultimoTextoHablado = data.texto;
                                const esEmergencia = data.texto.includes("Peligro");
                                hablar(data.texto, esEmergencia);
                            }
                        });
                }, 400);
            </script>
        </body>
        </html>
    ''')

@app.route('/video_feed')
def video_feed():
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alerta_audio')
def alerta_audio():
    global ultima_deteccion
    return jsonify(ultima_deteccion)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
