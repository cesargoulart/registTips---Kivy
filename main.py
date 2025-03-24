from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

class MainApp(App):
    def build(self):
        # Create the main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Create horizontal layout for combobox and edit button
        combo_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10
        )
        
        # Create combobox
        self.combo = Spinner(
            text='Select Option',
            values=('Option 1', 'Option 2', 'Option 3'),
            size_hint_x=0.8
        )
        
        # Create edit button for combobox
        edit_combo_button = Button(
            text='Edit',
            size_hint_x=0.2
        )
        edit_combo_button.bind(on_press=self.show_edit_popup)
        
        # Add widgets to combo layout
        combo_layout.add_widget(self.combo)
        combo_layout.add_widget(edit_combo_button)
        
        # Create date input
        date_input = TextInput(
            hint_text='Date',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        team1_input = TextInput(
            hint_text='Team 1',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        team2_input = TextInput(
            hint_text='Team 2',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        competition_input = TextInput(
            hint_text='Competition',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        bet_input = TextInput(
            hint_text='Bet',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        sport_input = TextInput(
            hint_text='Sport',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        live_input = TextInput(
            hint_text='Live',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        result_input = TextInput(
            hint_text='Result',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        # Add text inputs to layout
        layout.add_widget(combo_layout)
        layout.add_widget(date_input)
        layout.add_widget(team1_input)
        layout.add_widget(team2_input)
        layout.add_widget(competition_input)
        layout.add_widget(sport_input)
        layout.add_widget(bet_input)
        layout.add_widget(live_input)
        layout.add_widget(result_input)
        
        # Add insert button
        insert_button = Button(
            text='Insert',
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5}
        )
        insert_button.bind(on_press=self.on_insert)
        layout.add_widget(insert_button)
        
        return layout
    
    def on_insert(self, instance):
        print("Insert button pressed")
    
    def show_edit_popup(self, instance):
        # Create content for popup
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Create input for new value
        self.new_value_input = TextInput(
            hint_text='Enter new value',
            multiline=False
        )
        
        # Create buttons layout
        buttons_layout = BoxLayout(
            size_hint_y=None,
            height=40,
            spacing=5
        )
        
        # Create buttons
        add_btn = Button(text='Add')
        add_btn.bind(on_press=self.add_combo_value)
        
        delete_btn = Button(text='Delete Selected')
        delete_btn.bind(on_press=self.delete_combo_value)
        
        # Add widgets to buttons layout
        buttons_layout.add_widget(add_btn)
        buttons_layout.add_widget(delete_btn)
        
        # Add widgets to content
        content.add_widget(Label(text='Edit Combobox Values'))
        content.add_widget(self.new_value_input)
        content.add_widget(buttons_layout)
        
        # Create and show popup
        self.edit_popup = Popup(
            title='Edit Combobox',
            content=content,
            size_hint=(None, None),
            size=(300, 200)
        )
        self.edit_popup.open()
    
    def add_combo_value(self, instance):
        new_value = self.new_value_input.text.strip()
        if new_value:
            values = list(self.combo.values)
            if new_value not in values:
                values.append(new_value)
                self.combo.values = values
                self.new_value_input.text = ''
    
    def delete_combo_value(self, instance):
        if self.combo.text in self.combo.values:
            values = list(self.combo.values)
            values.remove(self.combo.text)
            if values:
                self.combo.values = values
                self.combo.text = values[0]
            else:
                self.combo.values = ('Option 1',)
                self.combo.text = 'Option 1'

if __name__ == '__main__':
    MainApp().run()
