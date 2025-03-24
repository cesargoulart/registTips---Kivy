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
        
        # Initially load the Tips section
        self.show_tips(None)
        
        return self.main_layout
    
    def show_tips(self, instance):
        # Clear the main layout except for the top buttons
        self.main_layout.clear_widgets()
        
        # Re-add the top buttons layout
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
        
        # Change background to dark theme
        self.main_layout.canvas.before.clear()
        with self.main_layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # Dark gray color (R,G,B,A)
            Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        
        # Update the rectangle size when layout size changes
        def update_rect(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0.1, 0.1, 0.1, 1)  # Dark gray color (R,G,B,A)
                Rectangle(pos=instance.pos, size=instance.size)
        
        self.main_layout.bind(size=update_rect, pos=update_rect)
    
    def show_main_interface(self, instance):
        # Rebuild the main interface
        self.main_layout.canvas.before.clear()
        self.main_layout.clear_widgets()
        self.build()
    
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
        # Clear the main layout except for the top buttons
        self.main_layout.clear_widgets()
        
        # Re-add the top buttons layout
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
        
        # Create form layout
        form_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Add form fields
        self.team1_input = TextInput(hint_text='Team 1')
        self.team2_input = TextInput(hint_text='Team 2')
        self.competition_input = TextInput(hint_text='Competition', size_hint_x=0.7)
        self.value_input = TextInput(hint_text='Value', size_hint_x=0.3)
        self.bet_input = TextInput(hint_text='Bet')
        self.sport_input = TextInput(hint_text='Sport')
        self.date_input = TextInput(hint_text='Date')
        self.live_input = Spinner(text='Yes', values=('Yes', 'No'))

        self.team1_input.size_hint_x = 0.8
        self.team2_input.size_hint_x = 0.8
        self.competition_input.size_hint_x = 0.5
        self.value_input.size_hint_x = 0.2
        self.bet_input.size_hint_x = 0.4
        self.sport_input.size_hint_x = 0.4
        form_layout.add_widget(self.team1_input)
        form_layout.add_widget(self.team2_input)

        # Add Competition and Value fields on the same line
        competition_value_layout = BoxLayout(orientation='horizontal', spacing=10)
        competition_value_layout.add_widget(Label(text='Competition:'))
        competition_value_layout.add_widget(self.competition_input)
        competition_value_layout.add_widget(Label(text='Value:'))
        competition_value_layout.add_widget(self.value_input)
        form_layout.add_widget(competition_value_layout)

        # Add Bet and Sport fields on the same line
        bet_sport_layout = BoxLayout(orientation='horizontal', spacing=10)
        bet_sport_layout.add_widget(Label(text='Bet:'))
        bet_sport_layout.add_widget(self.bet_input)
        bet_sport_layout.add_widget(Label(text='Sport:'))
        bet_sport_layout.add_widget(self.sport_input)
        form_layout.add_widget(bet_sport_layout)
        
        # Add Date and Live fields on the same line
        date_live_layout = BoxLayout(orientation='horizontal', spacing=10)
        date_live_layout.add_widget(Label(text='Date:'))
        date_live_layout.add_widget(self.date_input)
        date_live_layout.add_widget(Label(text='Live:'))
        date_live_layout.add_widget(self.live_input)
        form_layout.add_widget(date_live_layout)

        # Add "Insert Tips" button
        insert_tips_button = Button(text="Insert Tips", size_hint_y=None, height=40)
        insert_tips_button.bind(on_press=self.insert_tips)
        form_layout.add_widget(insert_tips_button)

        # Add form layout to main layout
        self.main_layout.add_widget(form_layout)

        # Change background to dark theme
        self.main_layout.canvas.before.clear()
        with self.main_layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # Dark gray color (R,G,B,A)
            Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        
        # Update the rectangle size when layout size changes
        def update_rect(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0.1, 0.1, 0.1, 1)  # Dark gray color (R,G,B,A)
                Rectangle(pos=instance.pos, size=instance.size)
        
        self.main_layout.bind(size=update_rect, pos=update_rect)
    
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

    def insert_tips(self, instance):
        # Placeholder for inserting tips
        pass

if __name__ == '__main__':
    MainApp().run()
