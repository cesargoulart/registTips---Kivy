import os
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
import threading
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

import firebase_admin
from firebase_admin import credentials, firestore

# --- Configuration ---
SERVICE_ACCOUNT_KEY_PATH = "revelo-512ee-firebase-adminsdk-jvu9y-179785bc1f.json"  # UPDATE THIS PATH

# --- Firebase Initialization ---
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase Initialized Successfully.")
    FIREBASE_INITIALIZED = True
except FileNotFoundError:
    print(f"Error: Service account key file not found at {SERVICE_ACCOUNT_KEY_PATH}")
    db = None
    FIREBASE_INITIALIZED = False
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    db = None
    FIREBASE_INITIALIZED = False

# --- Custom Input Filter Functions ---
def letters_and_space(text, from_undo):
    """Allow only letters and spaces."""
    return re.sub(r'[^A-Za-z\s]', '', text)

def date_filter(text, from_undo):
    """Allow only digits and hyphens (for a format like YYYY-MM-DD)."""
    text = re.sub(r'[^0-9\-]', '', text)
    return text[:10]

def odd_filter(text, from_undo):
    """Allow only numbers and one decimal point, max 4 digits total."""
    if not text:
        return ''
    # Remove any non-digit and non-decimal characters
    filtered = re.sub(r'[^0-9\.]', '', text)
    # Ensure only one decimal point
    parts = filtered.split('.')
    if len(parts) > 2:
        filtered = parts[0] + '.' + parts[1]
    # Limit total length to 4 characters (excluding decimal point)
    digits = filtered.replace('.', '')
    if len(digits) > 4:
        if '.' in filtered:
            dec_pos = filtered.index('.')
            filtered = filtered[:dec_pos + (5-dec_pos)]
        else:
            filtered = filtered[:4]
    return filtered

# --- Helper Function for Rounded Borders ---
def add_rounded_background(widget, bg_color, radius_dp=15):
    """Adds a rounded rectangle background to a widget's canvas.before."""
    with widget.canvas.before:
        Color(*bg_color)
        widget._rounded_rect_bg = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=[dp(radius_dp)]
        )

    def update_rect(instance, value):
        if hasattr(instance, '_rounded_rect_bg'):
            instance._rounded_rect_bg.pos = instance.pos
            instance._rounded_rect_bg.size = instance.size

    widget.bind(pos=update_rect, size=update_rect)

# --- Main App Class ---
class MainApp(App):
    def build(self):
        Window.clearcolor = (0.15, 0.15, 0.15, 1)
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        self.create_top_buttons()
        self.show_tips(None) # Start by showing tips
        return self.main_layout

    def create_top_buttons(self):
        """Creates the top 'Tips' and 'Insert' navigation buttons."""
        self.top_buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(20),
            padding=[dp(10), dp(10)]
        )

        # --- Tips Button ---
        tips_button_color = (0.2, 0.6, 0.8, 1)
        tips_button = Button(
            text='Tips',
            size_hint_x=0.5,
            background_normal='', background_down='', background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1), font_size='18sp'
        )
        add_rounded_background(tips_button, tips_button_color, radius_dp=10)
        tips_button.bind(on_press=self.show_tips)

        # --- Insert Button ---
        insert_button_color = (0.8, 0.4, 0.4, 1)
        insert_button = Button(
            text='Insert',
            size_hint_x=0.5,
            background_normal='', background_down='', background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1), font_size='18sp'
        )
        add_rounded_background(insert_button, insert_button_color, radius_dp=10)
        insert_button.bind(on_press=self.show_insert_form)

        self.top_buttons_layout.add_widget(tips_button)
        self.top_buttons_layout.add_widget(insert_button)
        # Ensure top buttons are always added first if they were cleared
        if not self.top_buttons_layout.parent:
             self.main_layout.add_widget(self.top_buttons_layout, index=len(self.main_layout.children)) # Add to top visually

    def show_insert_form(self, instance):
        """Clears the layout and displays the tip insertion form."""
        self.main_layout.clear_widgets()
        self.create_top_buttons() # Re-add top buttons

        form_bg_color = (0.25, 0.25, 0.25, 1) # Optional: background for the whole form area
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        # If you want a background for the form itself:
        # add_rounded_background(form_layout, form_bg_color, radius_dp=15)

        input_bg_color = (0.3, 0.3, 0.3, 1) # Background color for the input fields
        input_height = dp(40)
        input_radius = 8

        # --- Helper function to create an input container (NEW APPROACH) ---
        def create_input_container(hint_text, input_filter=None):
            container = BoxLayout(size_hint_y=None, height=input_height)
            add_rounded_background(container, input_bg_color, input_radius)

            text_input = TextInput(
                hint_text=hint_text,
                font_size='16sp',
                multiline=False,
                size_hint=(1, 1), # Fill the container
                height=input_height, # Height managed by container
                background_normal='',    # Disable default bg
                background_active='',    # Disable default focus bg
                background_color=(0, 0, 0, 0), # Make TextInput bg transparent
                foreground_color=(1, 1, 1, 1), # Text color
                hint_text_color=(0.7, 0.7, 0.7, 1), # Hint text color
                cursor_color=(1, 1, 1, 1),         # Cursor color
                padding=[dp(10), (input_height - dp(16))/2], # Horizontal padding, vertical centering
                input_filter=input_filter,
                is_focusable=True
            )
            container.add_widget(text_input)
            # Store the actual TextInput widget on the container for easy access
            container.text_input_widget = text_input
            return container

        # --- Create Input Containers using the helper ---
        self.user_input_container = create_input_container("User", letters_and_space)
        self.team1_input_container = create_input_container("Team 1", letters_and_space)
        self.team2_input_container = create_input_container("Team 2", letters_and_space)
        self.competition_input_container = create_input_container("Competition", letters_and_space)
        self.value_input_container = create_input_container("Value", 'float')
        self.bet_input_container = create_input_container("Bet Description")
        self.sport_input_container = create_input_container("Sport", letters_and_space)
        # Make date input shorter
        date_container = create_input_container("YYYY-MM-DD", date_filter)
        date_container.size_hint_x = 0.7  # Make the date field shorter
        self.date_input_container = date_container
        # Add odd input with custom filter
        self.odd_input_container = create_input_container("Odd", odd_filter)

        # --- Live Spinner (Keep styling as it worked) ---
        self.live_input = Spinner(
            text='No',
            values=('No', 'Yes'),
            font_size='16sp',
            size_hint=(1, None), # Let it fill available width in grid
            height=input_height,
            background_normal='', background_down='', # Disable default visuals
            background_color=(0, 0, 0, 0), # Make background transparent
            color=(1, 1, 1, 1) # Text color
        )
        # Apply rounded background to the Spinner itself
        add_rounded_background(self.live_input, input_bg_color, input_radius)
        # Adjust spinner padding if text isn't centered
        # self.live_input.padding = [dp(10), (input_height - dp(16))/2] # Example

        # --- Arrange Inputs and Labels in a Layout ---
        # Using BoxLayout rows for better alignment control
        label_width_hint = 0.2
        rows_data = [
            ('User:', self.user_input_container, '', None), # User on its own row, None placeholder
            ('Team 1:', self.team1_input_container, 'Team 2:', self.team2_input_container),
            ('Competition:', self.competition_input_container, 'Value:', self.value_input_container),
            ('Bet:', self.bet_input_container, 'Sport:', self.sport_input_container),
            ('Date:', self.date_input_container, 'Odd:', self.odd_input_container),
            ('Live:', self.live_input, '', None)
        ]

        for row_items in rows_data:
            row_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=input_height)
            # First Label-Input pair (always present)
            row_layout.add_widget(Label(text=row_items[0], size_hint_x=label_width_hint, height=input_height, halign='right', valign='middle', text_size=(None, input_height)))
            row_layout.add_widget(row_items[1]) # Add the container or Spinner

            # Second Label-Input pair (check if it exists)
            if row_items[3] is not None:
                row_layout.add_widget(Label(text=row_items[2], size_hint_x=label_width_hint, height=input_height, halign='right', valign='middle', text_size=(None, input_height)))
                row_layout.add_widget(row_items[3]) # Add the container or Spinner
            else:
                # Add dummy widgets to fill space if the second pair is missing
                # This keeps the first input aligned correctly
                row_layout.add_widget(Label(text='', size_hint_x=label_width_hint)) # Empty label
                row_layout.add_widget(BoxLayout(size_hint_x=1)) # Empty space filler

            form_layout.add_widget(row_layout)

        # --- Insert Tip Button ---
        insert_tip_button_color = (0.3, 0.7, 0.5, 1)
        insert_button = Button(
            text="Insert Tip",
            size_hint_y=None,
            height=dp(50),
            background_normal='', background_down='', background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1), font_size='18sp'
        )
        add_rounded_background(insert_button, insert_tip_button_color, radius_dp=10)
        insert_button.bind(on_press=self.insert_tip_to_firebase)
        form_layout.add_widget(Label(size_hint_y=None, height=dp(10)))  # Space before button
        form_layout.add_widget(insert_button)

        # --- Status Label ---
        self.status_label = Label(text="", size_hint_y=None, height=dp(30))
        form_layout.add_widget(self.status_label)

        # Add the form to the main layout
        self.main_layout.add_widget(form_layout)

    def insert_tip_to_firebase(self, instance):
        """Validates input and inserts tip data into Firebase Firestore."""
        if not FIREBASE_INITIALIZED or not db:
            self.show_popup("Error", "Firebase not initialized. Check key file and connection.")
            return

        try:
            # Access the text from the TextInput widget *inside* the container
            value_text = self.value_input_container.text_input_widget.text.strip()
            if not value_text:
                raise ValueError("Value cannot be empty")

            # Get odd value and validate
            odd_text = self.odd_input_container.text_input_widget.text.strip()
            if not odd_text:
                raise ValueError("Odd cannot be empty")

            tip_data = {
                'user': self.user_input_container.text_input_widget.text.strip(),
                'team1': self.team1_input_container.text_input_widget.text.strip(),
                'team2': self.team2_input_container.text_input_widget.text.strip(),
                'competition': self.competition_input_container.text_input_widget.text.strip(),
                'value': float(value_text),
                'odd': float(odd_text),  # Add odd field
                'bet': self.bet_input_container.text_input_widget.text.strip(),
                'sport': self.sport_input_container.text_input_widget.text.strip(),
                'date': self.date_input_container.text_input_widget.text.strip(),
                'live': self.live_input.text == 'Yes',
                'inserted_at': firestore.SERVER_TIMESTAMP,
                'status': 'Pending'
            }

            # Basic Validation: check if required fields are filled
            if not all([tip_data['user'], tip_data['team1'], tip_data['team2'], tip_data['competition'],
                        tip_data['bet'], tip_data['sport'], tip_data['date']]):
                raise ValueError("Please fill in all required fields (User, Team1, Team2, Competition, Bet, Sport, Date).")

            # Optional: Add more specific validation (e.g., date format) here if needed
            # Example: Validate date format
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', tip_data['date']):
                 raise ValueError("Date must be in YYYY-MM-DD format.")

        except ValueError as e:
            self.show_popup("Input Error", str(e))
            return
        except Exception as e: # Catch any other unexpected errors during data prep
            self.show_popup("Input Error", f"Invalid input: {e}")
            return

        # --- Perform Firestore Insertion ---
        try:
            # Disable button temporarily to prevent double clicks? (Optional)
            # instance.disabled = True
            doc_ref = db.collection('tips').add(tip_data)
            self.status_label.text = f"Tip inserted successfully! ID: {doc_ref[1].id[:8]}..."
            self.status_label.color = (0.3, 0.9, 0.3, 1) # Green for success
            Clock.schedule_once(self.clear_insert_fields, 0.1) # Clear fields shortly after
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', ''), 5) # Clear status message after 5s
        except Exception as e:
            self.status_label.text = f"Firebase Error: {e}"
            self.status_label.color = (0.9, 0.3, 0.3, 1) # Red for error
            print(f"Firebase insertion error: {e}") # Log detailed error
            self.show_popup("Firebase Error", f"Could not insert tip: {e}")
        finally:
            # Re-enable button if it was disabled (Optional)
            # instance.disabled = False
            pass

    def clear_insert_fields(self, dt):
        """Clears the text in all input fields after successful insertion."""
        input_containers = [
            'user_input_container',
            'team1_input_container',
            'team2_input_container',
            'competition_input_container',
            'value_input_container',
            'odd_input_container',  # Added odd field
            'bet_input_container',
            'sport_input_container',
            'date_input_container'
        ]
        
        # Clear all text input containers
        for container_name in input_containers:
            if hasattr(self, container_name):
                getattr(self, container_name).text_input_widget.text = ""
        
        # Reset spinner to default
        if hasattr(self, 'live_input'):
            self.live_input.text = "No"

    def show_popup(self, title, message):
        """Displays a simple popup message."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, size_hint_y=None, height=dp(80), text_size=(dp(250), None)))
        close_button = Button(text='Close', size_hint_y=None, height=dp(40))
        content.add_widget(close_button)
        popup_height = dp(180)
        popup = Popup(title=title, content=content, size_hint=(0.7, None), height=popup_height, auto_dismiss=False)
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_tips(self, instance):
        """Clears the layout and displays the list of tips from Firebase."""
        self.main_layout.clear_widgets()
        self.create_top_buttons() # Re-add top buttons
        if FIREBASE_INITIALIZED and db:
            self.loading_label = Label(text="Loading tips...", font_size='18sp', size_hint_y=None, height=dp(50))
            self.main_layout.add_widget(self.loading_label)
            threading.Thread(target=lambda: self.fetch_tips_from_firebase(), daemon=True).start()
        else:
            self.main_layout.add_widget(Label(
                text="Firebase not initialized or connection error.\nPlease check service key path and network.",
                font_size='16sp', color=(0.9, 0.5, 0.5, 1)
            ))

    def fetch_tips_from_firebase(self, user_filter=None):
        """Fetches tip data from Firestore with optional user filter."""
        tips_data = []
        error_message = None
        try:
            # Base query
            query = db.collection('tips')
            
            # Apply filters based on user_filter
            if user_filter:
                # When filtering by user, order by inserted_at after the filter
                query = query.where('user', '==', user_filter)
                query = query.order_by('inserted_at', direction=firestore.Query.DESCENDING)
            else:
                # When showing all tips, just order by inserted_at
                query = query.order_by('inserted_at', direction=firestore.Query.DESCENDING)
            
            # Execute query with limit
            tips_query = query.limit(50).stream()
            for tip_doc in tips_query:
                tip_dict = tip_doc.to_dict()
                tips_data.append({'id': tip_doc.id, 'data': tip_dict})
        except Exception as e:
            error_message = f"Error fetching tips: {e}"
            print(error_message)
        Clock.schedule_once(lambda dt: self.display_tips(tips_data, error_message, user_filter), 0)

    def display_tips(self, tips_data, error_message, user_filter=None):
        """Updates the UI to display the fetched tips with optional filter."""
        """Updates the UI to display the fetched tips or an error message."""
        if hasattr(self, 'loading_label') and self.loading_label.parent:
            self.main_layout.remove_widget(self.loading_label)

        if error_message:
            self.main_layout.add_widget(Label(text=error_message, font_size='16sp', color=(0.9, 0.5, 0.5, 1)))
            return
        if not tips_data:
            no_tips_label = Label(
                text=f"No tips found{f' for user {user_filter}' if user_filter else ''}.",
                font_size='16sp'
            )
            self.main_layout.add_widget(no_tips_label)
            if user_filter:
                clear_filter_btn = Button(
                    text="Clear Filter", size_hint=(None, None),
                    size=(dp(120), dp(40)), pos_hint={'center_x': 0.5},
                    background_normal='', background_color=(0.4, 0.4, 0.6, 1),
                    color=(1, 1, 1, 1)
                )
                clear_filter_btn.bind(on_press=lambda x: self.show_tips(None))
                self.main_layout.add_widget(clear_filter_btn)
            return

        scrollview = ScrollView(size_hint=(1, 1), bar_width=dp(10), scroll_type=['bars', 'content'])
        table_layout = GridLayout(
            cols=10,  # Increased for new Odd column
            size_hint_y=None,
            spacing=dp(2),
            padding=dp(10),
            row_default_height=dp(35),
            row_force_default=True
        )
        table_layout.bind(minimum_height=table_layout.setter('height'))
        headers = ["User", "Team1", "Team2", "Bet", "Competition", "Date", "Value", "Odd", "Profit", "Actions"]
        header_bg_color = (0.4, 0.4, 0.4, 1)

        for header in headers:
            header_label = Label(
                text=header, bold=True, font_size='16sp',
                size_hint_y=None, height=dp(40)
            )
            with header_label.canvas.before:
                Color(*header_bg_color)
                header_label._header_bg = Rectangle(pos=header_label.pos, size=header_label.size)
            header_label.bind(
                pos=lambda instance, value: setattr(instance._header_bg, 'pos', instance.pos) if hasattr(instance, '_header_bg') else None,
                size=lambda instance, value: setattr(instance._header_bg, 'size', instance.size) if hasattr(instance, '_header_bg') else None
            )
            table_layout.add_widget(header_label)

        row_colors = [(0.22, 0.22, 0.22, 1), (0.20, 0.20, 0.20, 1)]

        # Add filter indicator if active
        if user_filter:
            filter_label = Label(
                text=f"Showing tips for {user_filter}",
                font_size='16sp',
                color=(0.8, 0.8, 1, 1),
                size_hint_y=None,
                height=dp(30)
            )
            clear_filter_btn = Button(
                text="Show All Tips",
                size_hint=(None, None),
                size=(dp(120), dp(30)),
                pos_hint={'center_x': 0.5},
                background_normal='',
                background_color=(0.4, 0.4, 0.6, 1),
                color=(1, 1, 1, 1)
            )
            clear_filter_btn.bind(on_press=lambda x: self.show_tips(None))
            filter_box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70), spacing=dp(10))
            filter_box.add_widget(filter_label)
            filter_box.add_widget(clear_filter_btn)
            self.main_layout.add_widget(filter_box)

        for i, tip_item in enumerate(tips_data):
            tip_id = tip_item['id']
            tip = tip_item['data']
            bg_color = row_colors[i % 2]
            user_name = tip.get('user', 'N/A')
            data_points = [
                user_name,
                tip.get('team1', 'N/A'),
                tip.get('team2', 'N/A'),
                tip.get('bet', 'N/A'),
                tip.get('competition', 'N/A'),
                tip.get('date', 'N/A'),
                str(tip.get('value', 'N/A')),
                str(tip.get('odd', 'N/A')),
                str((float(tip.get('value', 0)) * float(tip.get('odd', 0))) - float(tip.get('value', 0))) if tip.get('status') == 'Win'
                    else str(-float(tip.get('value', 0))) if tip.get('status') == 'Loose'
                    else 'Pending'
            ]

            for i_data, data in enumerate(data_points):
                # Create cell widget (button for username, label for others)
                if i_data == 0 and data != "User":  # First column (username) but not header
                    cell = Button(
                        text=data,
                        font_size='14sp',
                        size_hint_y=None,
                        height=dp(30),
                        halign='center',
                        valign='middle',
                        background_normal='',
                        background_down='',
                        background_color=(0, 0, 0, 0),
                        color=(0.8, 0.8, 1, 1)  # Light blue text for username
                    )
                    cell.bind(on_press=lambda btn, name=data: self.filter_tips_by_user(name))
                else:
                    cell = Label(
                        text=data,
                        font_size='14sp',
                        size_hint_y=None,
                        height=dp(30),
                        halign='center',
                        valign='middle'
                    )

                # Add background to cell
                with cell.canvas.before:
                    Color(*bg_color)
                    cell._bg = Rectangle(pos=cell.pos, size=cell.size)
                
                # Bind position and size updates
                cell.bind(
                    pos=lambda instance, value: setattr(instance._bg, 'pos', instance.pos),
                    size=lambda instance, value: setattr(instance._bg, 'size', instance.size)
                )
                
                # Set cell text size for proper text alignment
                if isinstance(cell, Label):
                    cell.text_size = (None, dp(30))
                    cell.shorten = True
                    cell.shorten_from = 'right'
                
                # Add cell to table
                table_layout.add_widget(cell)

            # --- Add Action Buttons with conditional display ---
            action_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(35))  # Increased height and spacing
            tip_status = tip.get('status', 'Pending')
            
            if tip_status == 'Win':
                # Show disabled Win status button with subtle animation
                status_button = Button(
                    text="✓ WIN", font_size='14sp', size_hint_x=1,
                    background_normal='', background_down='',
                    background_color=(0.2, 0.7, 0.2, 0.9),  # More solid green
                    color=(1, 1, 1, 0.9),  # Slightly transparent white text
                    bold=True,
                    disabled=True
                )
                add_rounded_background(status_button, (0.2, 0.7, 0.2, 0.9), radius_dp=8)
                action_layout.add_widget(status_button)
            elif tip_status == 'Loose':  # Keeping 'Loose' for consistency with existing data
                # Show disabled Loose status button with subtle animation
                status_button = Button(
                    text="✗ LOOSE", font_size='14sp', size_hint_x=1,
                    background_normal='', background_down='',
                    background_color=(0.8, 0.3, 0.3, 0.9),  # More solid red
                    color=(1, 1, 1, 0.9),  # Slightly transparent white text
                    bold=True,
                    disabled=True
                )
                add_rounded_background(status_button, (0.8, 0.3, 0.3, 0.9), radius_dp=8)
                action_layout.add_widget(status_button)
            else:  # Pending status
                # Win button with hover effect
                win_button = Button(
                    text="WIN", font_size='14sp', size_hint_x=0.5,
                    background_normal='', background_down='',
                    background_color=(0.2, 0.7, 0.2, 0.8),
                    color=(1, 1, 1, 0.9),
                    bold=True
                )
                add_rounded_background(win_button, (0.2, 0.7, 0.2, 0.8), radius_dp=8)
                win_button.bind(
                    on_press=lambda instance, t_id=tip_id: self.update_tip_status(t_id, 'Win', instance),
                    on_release=lambda instance: setattr(instance, 'background_color', (0.2, 0.7, 0.2, 0.8))
                )
                
                # Loose button with hover effect
                loose_button = Button(
                    text="LOOSE", font_size='14sp', size_hint_x=0.5,
                    background_normal='', background_down='',
                    background_color=(0.8, 0.3, 0.3, 0.8),
                    color=(1, 1, 1, 0.9),
                    bold=True
                )
                add_rounded_background(loose_button, (0.8, 0.3, 0.3, 0.8), radius_dp=8)
                loose_button.bind(
                    on_press=lambda instance, t_id=tip_id: self.update_tip_status(t_id, 'Loose', instance),
                    on_release=lambda instance: setattr(instance, 'background_color', (0.8, 0.3, 0.3, 0.8))
                )
                
                action_layout.add_widget(win_button)
                action_layout.add_widget(loose_button)

            # Add background to action layout
            with action_layout.canvas.before:
                Color(*bg_color)
                action_layout._bg = Rectangle(pos=action_layout.pos, size=action_layout.size)
            action_layout.bind(
                pos=lambda instance, value: setattr(instance._bg, 'pos', instance.pos),
                size=lambda instance, value: setattr(instance._bg, 'size', instance.size)
            )

            # Add to table
            table_layout.add_widget(action_layout)

        scrollview.add_widget(table_layout)
        self.main_layout.add_widget(scrollview)

        # Calculate total profit for filtered user view
        if user_filter:
            total_profit = 0
            for tip_item in tips_data:
                tip = tip_item['data']
                if tip.get('status') == 'Win':
                    total_profit += (float(tip.get('value', 0)) * float(tip.get('odd', 0))) - float(tip.get('value', 0))
                elif tip.get('status') == 'Loose':
                    total_profit -= float(tip.get('value', 0))

            # Create total profit display
            total_layout = BoxLayout(
                orientation='horizontal',
                size_hint=(1, None),
                height=dp(50),
                padding=[dp(10), dp(5)]
            )
            spacer = Widget(size_hint_x=0.7)  # Push total to the right
            total_label = Label(
                text=f"Total Profit: {total_profit:.2f}",
                size_hint_x=0.3,
                font_size='18sp',
                bold=True,
                color=(0.3, 0.9, 0.3, 1) if total_profit >= 0 else (0.9, 0.3, 0.3, 1)
            )
            total_layout.add_widget(spacer)
            total_layout.add_widget(total_label)
            self.main_layout.add_widget(total_layout)

    def filter_tips_by_user(self, username):
        """Shows tips filtered for a specific user."""
        self.main_layout.clear_widgets()
        self.create_top_buttons()
        
        # Show loading state
        self.loading_label = Label(
            text=f"Loading tips for {username}...",
            font_size='18sp',
            size_hint_y=None,
            height=dp(50)
        )
        self.main_layout.add_widget(self.loading_label)
        
        # Start fetching in background thread
        threading.Thread(
            target=self.fetch_tips_from_firebase,
            kwargs={'user_filter': username},
            daemon=True
        ).start()

    def update_tip_status(self, tip_id, new_status, button_instance=None):
        """Starts a background thread to update the status of a tip in Firebase."""
        if not FIREBASE_INITIALIZED or not db:
            self.show_popup("Error", "Firebase not initialized.")
            return

        if button_instance and button_instance.parent:
            for child in button_instance.parent.children:
                if isinstance(child, Button):
                    child.disabled = True

        threading.Thread(
            target=self._update_tip_in_background,
            args=(tip_id, new_status, button_instance),
            daemon=True
        ).start()

    def _update_tip_in_background(self, tip_id, new_status, button_instance):
        """Performs the Firestore update in a background thread."""
        success = False
        error_message = None
        try:
            tip_ref = db.collection('tips').document(tip_id)
            tip_ref.update({'status': new_status})
            success = True
            print(f"Successfully updated tip {tip_id} to status {new_status}")
        except Exception as e:
            error_message = f"Error updating tip {tip_id}: {e}"
            print(error_message)
        Clock.schedule_once(lambda dt: self._update_tip_callback(success, error_message, button_instance), 0)

    def _update_tip_callback(self, success, error_message, button_instance):
        if button_instance and button_instance.parent:
             for child in button_instance.parent.children:
                if isinstance(child, Button):
                    child.disabled = False

        if success:
            self.show_tips(None)
        else:
            self.show_popup("Update Error", error_message or "Failed to update tip status.")

# --- Run the App ---
if __name__ == '__main__':
    MainApp().run()
