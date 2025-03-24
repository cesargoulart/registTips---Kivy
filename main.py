from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle

class MainApp(App):
    def build(self):
        # Create the main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Create top buttons layout
        top_buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=50,
            spacing=10
        )
        
        # Create Tips button
        tips_button = Button(
            text='Tips',
            size_hint_x=0.5
        )
        tips_button.bind(on_press=self.show_tips)
        
        # Create Insert top button
        insert_top_button = Button(
            text='Insert',
            size_hint_x=0.5
        )
        insert_top_button.bind(on_press=self.on_insert)
        
        # Add buttons to top layout
        top_buttons_layout.add_widget(tips_button)
        top_buttons_layout.add_widget(insert_top_button)
        
        # Add top buttons layout to main layout
        self.main_layout.add_widget(top_buttons_layout)
        
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
        
        # Create yes/no combo layout
        yes_no_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10
        )
        
        # Create yes/no label
        yes_no_label = Label(
            text='Combo: ',
            size_hint_x=0.3
        )
        
        # Create yes/no combo
        self.combo_yes_no = Spinner(
            text='No',
            values=('Yes', 'No'),
            size_hint_x=0.7
        )
        self.combo_yes_no.bind(text=self.on_yes_no_selection)
        
        # Add widgets to yes/no layout
        yes_no_layout.add_widget(yes_no_label)
        yes_no_layout.add_widget(self.combo_yes_no)
        
        # Create date input
        date_input = TextInput(
            hint_text='Date',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        # Create Team1 container (for splitting functionality)
        self.team1_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=5
        )
        
        # Create Team1 field (full width by default)
        self.team1_input = TextInput(
            hint_text='Team 1',
            multiline=False,
            size_hint_x=1
        )
        
        # Create Team1 split fields (hidden by default)
        self.team1_left = TextInput(
            hint_text='Team 1 Left',
            multiline=False,
            size_hint_x=0.5
        )
        self.team1_right = TextInput(
            hint_text='Team 1 Right',
            multiline=False,
            size_hint_x=0.5
        )
        
        # Add the default Team1 field to container
        self.team1_container.add_widget(self.team1_input)
        
        # Create Team2 container (for splitting functionality)
        self.team2_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=5
        )
        
        # Create Team2 field (full width by default)
        self.team2_input = TextInput(
            hint_text='Team 2',
            multiline=False,
            size_hint_x=1
        )
        
        # Create Team2 split fields (hidden by default)
        self.team2_left = TextInput(
            hint_text='Team 2 Left',
            multiline=False,
            size_hint_x=0.5
        )
        self.team2_right = TextInput(
            hint_text='Team 2 Right',
            multiline=False,
            size_hint_x=0.5
        )
        
        # Add the default Team2 field to container
        self.team2_container.add_widget(self.team2_input)
        
        # Create Competition container (for splitting functionality)
        self.competition_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=5
        )
        
        # Create Competition field (full width by default)
        self.competition_input = TextInput(
            hint_text='Competition',
            multiline=False,
            size_hint_x=1
        )
        
        # Create Competition split fields (hidden by default)
        self.competition_left = TextInput(
            hint_text='Competition Left',
            multiline=False,
            size_hint_x=0.5
        )
        self.competition_right = TextInput(
            hint_text='Competition Right',
            multiline=False,
            size_hint_x=0.5
        )
        
        # Add the default Competition field to container
        self.competition_container.add_widget(self.competition_input)
        
        sport_input = TextInput(
            hint_text='Sport',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        # Create bet input field
        self.bet_input = TextInput(
            hint_text='Bet',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        # Create live combo layout
        live_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            spacing=10
        )
        
        # Create live label
        live_label = Label(
            text='Live:',
            size_hint_x=0.3
        )
        
        # Create live combo
        self.combo_live = Spinner(
            text='No',
            values=('Yes', 'No'),
            size_hint_x=0.7
        )
        
        # Add widgets to live layout
        live_layout.add_widget(live_label)
        live_layout.add_widget(self.combo_live)
        
        result_input = TextInput(
            hint_text='Result',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        
        # Add text inputs to layout
        self.main_layout.add_widget(combo_layout)
        self.main_layout.add_widget(yes_no_layout)  # Add the new yes/no combo layout
        self.main_layout.add_widget(date_input)
        self.main_layout.add_widget(self.team1_container)
        self.main_layout.add_widget(self.team2_container)
        self.main_layout.add_widget(self.competition_container)
        self.main_layout.add_widget(sport_input)
        self.main_layout.add_widget(self.bet_input)
        self.main_layout.add_widget(live_layout)
        self.main_layout.add_widget(result_input)
        
        # Add insert button at bottom (changing to "Insert Tips")
        insert_button = Button(
            text='Insert Tips',
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5}
        )
        insert_button.bind(on_press=self.on_insert)
        self.main_layout.add_widget(insert_button)
        
        return self.main_layout
    
    def show_tips(self, instance):
        # Change background to black
        self.main_layout.canvas.before.clear()
        with self.main_layout.canvas.before:
            Color(0, 0, 0, 1)  # Black color (R,G,B,A)
            Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        
        # Update the rectangle size when layout size changes
        def update_rect(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0, 0, 0, 1)
                Rectangle(pos=instance.pos, size=instance.size)
        
        self.main_layout.bind(size=update_rect, pos=update_rect)
    
    def on_yes_no_selection(self, instance, value):
        # Clear the containers first
        self.team1_container.clear_widgets()
        self.team2_container.clear_widgets()
        self.competition_container.clear_widgets()
        
        if value == 'Yes':
            # Split Team1 field into two fields
            self.team1_container.add_widget(self.team1_left)
            self.team1_container.add_widget(self.team1_right)
            
            # Split Team2 field into two fields
            self.team2_container.add_widget(self.team2_left)
            self.team2_container.add_widget(self.team2_right)
            
            # Split Competition field into two fields
            self.competition_container.add_widget(self.competition_left)
            self.competition_container.add_widget(self.competition_right)
        else:
            # Use single fields
            self.team1_container.add_widget(self.team1_input)
            self.team2_container.add_widget(self.team2_input)
            self.competition_container.add_widget(self.competition_input)
    
    def on_insert(self, instance):
        # Do nothing when clicked
        pass
    
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
