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
    # Limit length for safety
    text = re.sub(r'[^0-9\-]', '', text)
    return text[:10] # Max length for YYYY-MM-DD

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
        self.user_input_container = create_input_container("User", letters_and_space) # Added User container
        self.team1_input_container = create_input_container("Team 1", letters_and_space)
        self.team2_input_container = create_input_container("Team 2", letters_and_space)
        self.competition_input_container = create_input_container("Competition", letters_and_space)
        self.value_input_container = create_input_container("Value", 'float')
        self.bet_input_container = create_input_container("Bet Description")
        self.sport_input_container = create_input_container("Sport", letters_and_space)
        self.date_input_container = create_input_container("Date (YYYY-MM-DD)", date_filter)

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
            ('Date:', self.date_input_container, 'Live:', self.live_input)
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

            tip_data = {
                'user': self.user_input_container.text_input_widget.text.strip(), # Added user field
                'team1': self.team1_input_container.text_input_widget.text.strip(),
                'team2': self.team2_input_container.text_input_widget.text.strip(),
                'competition': self.competition_input_container.text_input_widget.text.strip(),
                'value': float(value_text), # Convert to float
                'bet': self.bet_input_container.text_input_widget.text.strip(),
                'sport': self.sport_input_container.text_input_widget.text.strip(),
                'date': self.date_input_container.text_input_widget.text.strip(),
                'live': self.live_input.text == 'Yes', # Boolean based on Spinner text
                'inserted_at': firestore.SERVER_TIMESTAMP # Use server time
            }

            # Basic Validation: check if required fields are filled
            if not all([tip_data['user'], tip_data['team1'], tip_data['team2'], tip_data['competition'], # Added user validation
                        tip_data['bet'], tip_data['sport'], tip_data['date']]):
                raise ValueError("Please fill in all required fields (User, Team1, Team2, Competition, Bet, Sport, Date).") # Updated error message

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
        # Access the TextInput widget *inside* the container to set its text
        if hasattr(self, 'user_input_container'): # Added user field clearing
            self.user_input_container.text_input_widget.text = ""
        if hasattr(self, 'team1_input_container'):
            self.team1_input_container.text_input_widget.text = ""
        if hasattr(self, 'team2_input_container'):
            self.team2_input_container.text_input_widget.text = ""
        if hasattr(self, 'competition_input_container'):
            self.competition_input_container.text_input_widget.text = ""
        if hasattr(self, 'value_input_container'):
            self.value_input_container.text_input_widget.text = ""
        if hasattr(self, 'bet_input_container'):
            self.bet_input_container.text_input_widget.text = ""
        if hasattr(self, 'sport_input_container'):
            self.sport_input_container.text_input_widget.text = ""
        if hasattr(self, 'date_input_container'):
            self.date_input_container.text_input_widget.text = ""
        if hasattr(self, 'live_input'):
            self.live_input.text = "No" # Reset Spinner to default

    def show_popup(self, title, message):
        """Displays a simple popup message."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text=message, size_hint_y=None, height=dp(80), text_size=(dp(250), None))) # Allow text wrapping
        close_button = Button(text='Close', size_hint_y=None, height=dp(40))
        content.add_widget(close_button)
        popup_height = dp(180) # Adjust height as needed
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
            # Fetch tips in a separate thread to avoid blocking the UI
            threading.Thread(target=self.fetch_tips_from_firebase, daemon=True).start()
        else:
            self.main_layout.add_widget(Label(
                text="Firebase not initialized or connection error.\nPlease check service key path and network.",
                font_size='16sp', color=(0.9, 0.5, 0.5, 1)
            ))

    def fetch_tips_from_firebase(self):
        """Fetches tip data from Firestore in a background thread."""
        tips_data = []
        error_message = None
        try:
            # Query Firestore, order by insertion time descending, limit results
            tips_query = db.collection('tips').order_by(
                'inserted_at', direction=firestore.Query.DESCENDING
            ).limit(50).stream() # Get up to 50 most recent tips
            # Convert documents to dictionaries
            tips_data = [tip_doc.to_dict() for tip_doc in tips_query]
        except Exception as e:
            error_message = f"Error fetching tips: {e}"
            print(error_message) # Log the error

        # Schedule the UI update back on the main Kivy thread
        Clock.schedule_once(lambda dt: self.display_tips(tips_data, error_message), 0)

    def display_tips(self, tips_data, error_message):
        """Updates the UI to display the fetched tips or an error message."""
        # Remove loading label if it exists
        if hasattr(self, 'loading_label') and self.loading_label.parent:
            self.main_layout.remove_widget(self.loading_label)

        if error_message:
            self.main_layout.add_widget(Label(text=error_message, font_size='16sp', color=(0.9, 0.5, 0.5, 1)))
            return
        if not tips_data:
            self.main_layout.add_widget(Label(text="No tips found.", font_size='16sp'))
            return

        # --- Create Scrollable Table for Tips ---
        scrollview = ScrollView(size_hint=(1, 1), bar_width=dp(10), scroll_type=['bars', 'content'])

        table_layout = GridLayout(
            cols=7, # Number of columns (Increased to 7 for User)
            size_hint_y=None, # Allow vertical expansion based on content
            spacing=dp(2),    # Spacing between cells
            padding=dp(10),   # Padding around the grid
            row_default_height=dp(35), # Default height for rows
            row_force_default=True     # Force default height
        )
        # Make the GridLayout height fit its content
        table_layout.bind(minimum_height=table_layout.setter('height'))

        headers = ["User", "Team1", "Team2", "Bet", "Competition", "Date", "Value"] # Added User header
        header_bg_color = (0.4, 0.4, 0.4, 1)

        # Add Header Row
        for header in headers:
            header_label = Label(
                text=header, bold=True, font_size='16sp',
                size_hint_y=None, height=dp(40) # Fixed height for header
            )
            # Optional: Add background to header cells
            with header_label.canvas.before:
                Color(*header_bg_color)
                header_label._header_bg = Rectangle(pos=header_label.pos, size=header_label.size)
            header_label.bind(
                pos=lambda instance, value: setattr(instance._header_bg, 'pos', instance.pos) if hasattr(instance, '_header_bg') else None,
                size=lambda instance, value: setattr(instance._header_bg, 'size', instance.size) if hasattr(instance, '_header_bg') else None
            )
            table_layout.add_widget(header_label)

        # Alternating Row Colors
        row_colors = [(0.22, 0.22, 0.22, 1), (0.20, 0.20, 0.20, 1)]

        # Add Data Rows
        for i, tip in enumerate(tips_data):
            bg_color = row_colors[i % 2] # Alternate color based on row index
            data_points = [
                tip.get('user', 'N/A'), # Added User data
                tip.get('team1', 'N/A'), # Use .get() for safety if keys might be missing
                tip.get('team2', 'N/A'),
                tip.get('bet', 'N/A'),
                tip.get('competition', 'N/A'),
                tip.get('date', 'N/A'),
                str(tip.get('value', 'N/A')) # Convert value to string
            ]

            for data in data_points:
                cell_label = Label(
                    text=data, font_size='14sp',
                    size_hint_y=None, height=dp(30), # Row height set by grid default
                    halign='center', valign='middle',
                    shorten=True, shorten_from='right', # Ellipsize long text
                    text_size=(None, None) # Allow label to determine its size initially
                )
                # Set background color for the cell
                with cell_label.canvas.before:
                    Color(*bg_color)
                    cell_label._cell_bg = Rectangle(pos=cell_label.pos, size=cell_label.size)

                # Update background rect on pos/size change
                cell_label.bind(
                    pos=lambda instance, value: setattr(instance._cell_bg, 'pos', instance.pos) if hasattr(instance, '_cell_bg') else None,
                    size=lambda instance, value: setattr(instance._cell_bg, 'size', instance.size) if hasattr(instance, '_cell_bg') else None
                )
                # Bind text_size to width for wrapping/shortening (adjust padding as needed)
                cell_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value - dp(10), None)))

                table_layout.add_widget(cell_label)

        scrollview.add_widget(table_layout)
        self.main_layout.add_widget(scrollview)

# --- Run the App ---
if __name__ == '__main__':
    MainApp().run()