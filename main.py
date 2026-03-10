from kivy.app import App
from kivy.uix.label import Label

class DoramaDownApp(App):
    def build(self):
        return Label(text="DoramaDown funcionando!")

if __name__ == "__main__":
    DoramaDownApp().run()
