Markdown
# 👁️ Copiloto AI - Asistente de Visión Artificial e Inteligencia Accesible

Un sistema de asistencia por computador y visión artificial diseñado para **ayudar a personas con discapacidad visual o baja visión** a percibir su entorno en tiempo real mediante alertas de voz en español totalmente offline.

Este proyecto nació con el propósito de ser una **herramienta comunitaria y de código abierto**, libre para que cualquier desarrollador, técnico o entidad enfocada en la accesibilidad pueda continuarlo, mejorarlo o adaptarlo.

---

## 🎯 Objetivo del Proyecto

Ofrecer una solución accesible, económica y funcional que procese el vídeo capturado por la cámara (móvil o webcam) y emita alertas sonoras/habladas espaciales ("persona al frente, cerca", "coche a la derecha, muy cerca") para facilitar la orientación y movilidad.

---

## 🛠️ Arquitectura Técnica

- **Motor de Visión:** YOLOv8 (Ultralytics) enfocado en la detección de elementos prioritarios (personas, vehículos, semáforos, obstáculos).
- **Servidor Local:** Python 3 con Flask para transmisión e interfaz web.
- **Voz Offline:** `pyttsx3` (síntesis de voz local en español, sin necesidad de conexión a Internet).
- **Procesamiento:** Diseñado para utilizar la GPU local del servidor/sobremesa para un procesamiento de baja latencia.

---

## 🚀 Estado Actual del Proyecto

El proyecto cuenta con la base técnica y funcional lista para entornos de red local:
- [x] Modelo de IA y filtrado de objetos prioritarios implementado.
- [x] Motor de avisos por voz offline en español con intervalos de frecuencia.
- [x] Servidor web Flask y transmisión local de vídeo entre dispositivos.
- [ ] **Pendiente:** Optimización de latencia en transmisión WebRTC / HTML5 directa.
- [ ] **Pendiente:** Empaquetado en ejecutable sencillo o app móvil nativa.

---

## 🤝 ¿Cómo contribuir?

Este proyecto está **abierto a toda la comunidad de desarrolladores y expertos en accesibilidad**. Si deseas colaborar:

1. Haz un **Fork** de este repositorio.
2. Crea una rama con tu mejora (`git checkout -b mejora-accesibilidad`).
3. Envía un **Pull Request** explicando tus cambios.

Toda ayuda es bienvenida para hacer de esta herramienta una ayuda real y efectiva.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**, lo que significa que es de uso, modificación y distribucion
