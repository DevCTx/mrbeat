
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget


class PlayIndicatorLight(Image):
    state = False

# class PlayIndicatorButton(ToggleButton):
#     pass

class PlayIndicatorWidget(BoxLayout):
    nb_steps = 0    # nombre de steps
    # buttons = []
    lights = []

    def set_current_screen_step_index(self, index):
        # ajout de la liste des boutons
        if 0 <= index <= self.nb_steps:
            for i in range(0, self.nb_steps):
                if i == index: #ON
                    # self.buttons[i].state = "down"
                    self.lights[i].source = "images/indicator_light_on.png"
                else:
                    # self.buttons[i].state = "normal"
                    self.lights[i].source = "images/indicator_light_off.png"

    def set_nb_steps(self, nb_steps, steps_left_align):
        if nb_steps != self.nb_steps:
            self.nb_steps = nb_steps

            # ajout d'un faux bouton pour mettre un décalage au widget
            unused_widget = Widget()
            unused_widget.size_hint_x = None
            unused_widget.width = steps_left_align
            self.add_widget(unused_widget)

            # ajout de la liste des boutons
            # self.buttons = []
            self.lights = []
            for i in range(0, self.nb_steps):
                # button = PlayIndicatorButton()
                light = PlayIndicatorLight()
                # button.background_color = (0.5, 0.5, 1, 1)
                # button.background_disabled_normal = "images/indicator_light_off.png"
                # button.background_disabled_down = "images/indicator_light_on.png"
                # button.disabled = True
                # button.background_disabled_down = ''
                light.source = "images/indicator_light_off.png"
                if i == 0 :
                    # button.state = "down"
                    light.state = True
                self.lights.append(light)
                self.add_widget(light)
