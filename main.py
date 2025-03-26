import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock  # Import Clock for delayed actions like clearing fields

# --- Firebase Admin Setup ---
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# --- IMPORTANT: Replace with the actual path to your downloaded service account key ---
SERVICE_ACCOUNT_KEY_PATH = "revelo-512ee-firebase-adminsdk-jvu9y-179785bc1f.json" 
# Example: SERVICE_ACCOUNT_KEY_PATH = "my-firebase-project-key.json" 
# Put the key file in the same directory as main.py for this example,
# or provide the full path.

# --- Firebase Initialization ---
try:
    # Check if the app is already initialized to prevent errors on potential reloads
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client() # Get the Firestore client instance
    print("Firebase Initialized Successfully.")
    FIREBASE_INITIALIZED = True
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    print("Firebase functionality will be disabled.")
    db = None # Ensure db is None if initialization fails
    FIREBASE_INITIALIZED = False
# --- End Firebase Setup ---


class MainApp(App):
    def build(self):
        # Set a consistent dark background for the entire window
        Window.clearcolor = (0.15, 0.15, 0.15, 1)

        # Create the main layout with extra padding and spacing for a modern look
        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Add top buttons layout
        self.create_top_buttons()

        # Initially load the Tips section
        self.show_tips(None)
        return self.main_layout

    def create_top_buttons(self):
        # Create a dedicated layout for the top buttons with enhanced spacing
        self.top_buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=20,
            padding=[10, 10]
        )

        # Create the Tips button with accent color and increased font size
        tips_button = Button(
            text='Tips',
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        tips_button.bind(on_press=self.show_tips)

        # Create the Insert button with a complementary color
        insert_button = Button(
            text='Insert',
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.8, 0.4, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        insert_button.bind(on_press=self.on_insert)

        self.top_buttons_layout.add_widget(tips_button)
        self.top_buttons_layout.add_widget(insert_button)

        # Ensure the top buttons are always at the top
        self.main_layout.add_widget(self.top_buttons_layout)

    def show_tips(self, instance):
        # Clear existing widgets while keeping the top buttons
        self.main_layout.clear_widgets()
        self.create_top_buttons()

        # Display a sample tip label with improved styling
        tips_text = 'Here are some useful tips for using the app!'
        if not FIREBASE_INITIALIZED:
             tips_text += "\n\n[Warning: Firebase connection failed. Check key path and console.]"

        tips_label = Label(
            text=tips_text,
            font_size='20sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        self.main_layout.add_widget(tips_label)

        # Set a dark background using canvas instructions
        with self.main_layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.rect = Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        self.main_layout.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, instance, value):
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size

    def on_insert(self, instance):
        self.main_layout.clear_widgets()
        self.create_top_buttons()

        # Create a form layout with ample spacing and padding
        form_layout = BoxLayout(orientation='vertical', spacing=15, padding=20) # Adjusted spacing

        # Define TextInput fields with consistent styling
        self.team1_input = TextInput(
            hint_text='Team 1', font_size='16sp', multiline=False,
            size_hint_y=None, height=40
        )
        self.team2_input = TextInput(
            hint_text='Team 2', font_size='16sp', multiline=False,
            size_hint_y=None, height=40
        )
        self.competition_input = TextInput(
            hint_text='Competition', font_size='16sp', multiline=False,
            size_hint_y=None, height=40
        )
        self.value_input = TextInput(
            hint_text='Value (e.g., 1.85)', font_size='16sp', multiline=False,
            size_hint_y=None, height=40, input_filter='float' # Suggest numeric input
        )
        self.bet_input = TextInput(
            hint_text='Bet Description', font_size='16sp', multiline=False,
            size_hint_y=None, height=40
        )
        self.sport_input = TextInput(
            hint_text='Sport', font_size='16sp', multiline=False,
            size_hint_y=None, height=40
        )
        self.date_input = TextInput(
            hint_text='Date (YYYY-MM-DD)', font_size='16sp', multiline=False,
            size_hint_y=None, height=40
        )
        self.live_input = Spinner(
            text='No', # Default to No
            values=('No', 'Yes'),
            font_size='16sp',
            size_hint=(None, None), # Allow setting specific width
            width=100, # Give spinner a fixed width
            height=40,
            background_normal='',
            background_color=(0.4, 0.4, 0.4, 1),
            color=(1, 1, 1, 1)
        )

        # --- Create Input Rows (using BoxLayout for better alignment) ---

        # Row 1: Team 1, Team 2
        row1 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        row1.add_widget(Label(text='Team 1:', size_hint_x=0.2, font_size='16sp', color=(1, 1, 1, 1)))
        row1.add_widget(self.team1_input)
        row1.add_widget(Label(text='Team 2:', size_hint_x=0.2, font_size='16sp', color=(1, 1, 1, 1)))
        row1.add_widget(self.team2_input)
        form_layout.add_widget(row1)

        # Row 2: Competition, Value
        row2 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        row2.add_widget(Label(text='Competition:', size_hint_x=0.2, font_size='16sp', color=(1, 1, 1, 1)))
        row2.add_widget(self.competition_input)
        row2.add_widget(Label(text='Value:', size_hint_x=0.2, font_size='16sp', color=(1, 1, 1, 1)))
        row2.add_widget(self.value_input)
        form_layout.add_widget(row2)

        # Row 3: Bet, Sport
        row3 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        row3.add_widget(Label(text='Bet:', size_hint_x=0.2, font_size='16sp', color=(1, 1, 1, 1)))
        row3.add_widget(self.bet_input)
        row3.add_widget(Label(text='Sport:', size_hint_x=0.2, font_size='16sp', color=(1, 1, 1, 1)))
        row3.add_widget(self.sport_input)
        form_layout.add_widget(row3)

        # Row 4: Date, Live
        row4 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        row4.add_widget(Label(text='Date:', size_hint_x=0.2, font_size='16sp', color=(1, 1, 1, 1)))
        row4.add_widget(self.date_input)
        row4.add_widget(Label(text='Live:', size_hint_x=0.2, font_size='16sp', color=(1, 1, 1, 1)))
        row4.add_widget(self.live_input)
        # Add a spacer to push the spinner left if desired, or adjust size_hint_x of labels/inputs
        row4.add_widget(BoxLayout(size_hint_x=0.4)) # Example spacer
        form_layout.add_widget(row4)

        # Add some vertical space before the button
        form_layout.add_widget(BoxLayout(size_hint_y=None, height=20))

        # Create an "Insert Tips" button with accent styling
        insert_tips_button = Button(
            text="Insert Tip", # Changed text slightly
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.3, 0.7, 0.5, 1),
            font_size='18sp',
            color=(1, 1, 1, 1)
        )
        insert_tips_button.bind(on_press=self.insert_tip_to_firebase) # Bind to the new method
        form_layout.add_widget(insert_tips_button)

        # Add a status label (optional, for feedback)
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=30,
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        form_layout.add_widget(self.status_label)

        self.main_layout.add_widget(form_layout)

        # Apply a dark canvas background to the layout
        with self.main_layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.rect = Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
        self.main_layout.bind(size=self.update_rect, pos=self.update_rect)

    def insert_tip_to_firebase(self, instance):
        # Check if Firebase is initialized
        if not FIREBASE_INITIALIZED or not db:
            self.show_popup("Error", "Firebase is not initialized. Cannot insert data.")
            return
            
        # --- 1. Get data from input fields ---
        team1 = self.team1_input.text.strip()
        team2 = self.team2_input.text.strip()
        competition = self.competition_input.text.strip()
        value_str = self.value_input.text.strip()
        bet = self.bet_input.text.strip()
        sport = self.sport_input.text.strip()
        date = self.date_input.text.strip()
        live = self.live_input.text == 'Yes' # Convert to boolean

        # --- 2. Basic Validation (Optional but recommended) ---
        if not all([team1, team2, competition, value_str, bet, sport, date]):
            self.show_popup("Input Error", "Please fill in all fields.")
            return

        try:
            # Try converting value to float
            value_float = float(value_str)
        except ValueError:
            self.show_popup("Input Error", "Invalid format for 'Value'. Please enter a number (e.g., 1.85).")
            return

        # --- 3. Prepare data dictionary ---
        tip_data = {
            'team1': team1,
            'team2': team2,
            'competition': competition,
            'value': value_float, # Store as number
            'bet': bet,
            'sport': sport,
            'date': date,       # Store as string for now, consider datetime objects later
            'live': live,       # Store as boolean
            'inserted_at': firestore.SERVER_TIMESTAMP # Add a server timestamp
        }

        # --- 4. Insert data into Firestore ---
        try:
            # Add a new document with an auto-generated ID to the 'tips' collection
            doc_ref = db.collection('tips').add(tip_data)
            print(f"Document added with ID: {doc_ref[1].id}") # doc_ref is a tuple (timestamp, DocumentReference)
            
            # Provide user feedback
            self.status_label.text = f"Tip inserted successfully! (ID: {doc_ref[1].id[:8]}...)"
            self.status_label.color = (0.3, 0.9, 0.3, 1) # Green color for success
            
            # Clear fields after successful insertion (using Clock.schedule_once for safety)
            Clock.schedule_once(self.clear_insert_fields, 0.1) 

        except Exception as e:
            print(f"Error adding document to Firestore: {e}")
            self.show_popup("Firebase Error", f"Failed to insert tip: {e}")
            self.status_label.text = "Insertion failed. See console/popup."
            self.status_label.color = (0.9, 0.3, 0.3, 1) # Red color for error

    def clear_insert_fields(self, dt):
        """Clears the input fields in the insert form."""
        if hasattr(self, 'team1_input'): self.team1_input.text = ""
        if hasattr(self, 'team2_input'): self.team2_input.text = ""
        if hasattr(self, 'competition_input'): self.competition_input.text = ""
        if hasattr(self, 'value_input'): self.value_input.text = ""
        if hasattr(self, 'bet_input'): self.bet_input.text = ""
        if hasattr(self, 'sport_input'): self.sport_input.text = ""
        if hasattr(self, 'date_input'): self.date_input.text = ""
        if hasattr(self, 'live_input'): self.live_input.text = "No" # Reset spinner
        # Optionally clear the status label after a delay
        # Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', ''), 5)


    def show_popup(self, title, message):
        """Helper function to display a popup message."""
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message, size_hint_y=0.8))
        close_button = Button(text='Close', size_hint_y=0.2)
        popup_layout.add_widget(close_button)

        popup = Popup(title=title,
                      content=popup_layout,
                      size_hint=(0.7, 0.4)) # Adjust size as needed
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    # Removed insert_tips method as it's replaced by insert_tip_to_firebase
    # def insert_tips(self, instance):
    #     pass


if __name__ == '__main__':
    MainApp().run()