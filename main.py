from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from plyer import tts

class CopilotoLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=20, **kwargs)
        
        self.label = Label(
            text="¡Copiloto activado!", 
            font_size='28sp'
        )
        self.add_widget(self.label)
        
        self.btn_hablar = Button(
            text="Probar Voz", 
            size_hint=(1, 0.3),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.btn_hablar.bind(on_press=self.hablar)
        self.add_widget(self.btn_hablar)

    def hablar(self, instance):
        try:
            tts.speak("Hola Enrique, el copiloto está listo para la ruta")
        except Exception as e:
            self.label.text = "Error de voz"

class CopilotoApp(App):
    def build(self):
        return CopilotoLayout()

if __name__ == '__main__':
    CopilotoApp().run()
