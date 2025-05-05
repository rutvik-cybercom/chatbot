from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector
from mysql.connector import Error

class ActionGetUserData(Action):
    def name(self) -> Text:
        return "action_get_user_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the user_id slot from the tracker
        user_id = tracker.get_slot("user_id")
        print(f"User ID: {user_id}")  # Logging for debugging

        # If user_id is not provided, inform the user
        if not user_id:
            dispatcher.utter_message(text="I couldn't find a user ID in your message.")
            return []

        try:
            # Try converting user_id to integer (if possible)
            user_id = int(user_id)
        except ValueError:
            dispatcher.utter_message(text="Invalid user ID format. It should be numeric.")
            return []

        # Attempt to connect to the MySQL database
        try:
            conn = mysql.connector.connect(
                host="192.168.0.204",
                user="cccsql",
                password="ccc123",
                database="psr_stp_stage"
            )
            cursor = conn.cursor(dictionary=True)

            # Execute the query with the user_id
            # query = "SELECT employee_name, emp_position_code FROM gbq_users WHERE employee_cd = %s"
            query = "select doctor_name from psr_stp_stage.gbq_psr_hcp_mappings gphm  where employee_code = %s"
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()

            # Assuming the value you want is in the first column of each row
            usernames = [row["doctor_name"] for row in results]

            comma_separated = ", ".join(usernames)
            print(comma_separated)
            # Check if the user data is found
            # if comma_separated:
            #     # message = f"User {result['employee_name']} holds the position code: {result['emp_position_code']}."
            #     message = f"Users: {comma_separated}"
            if usernames:
                    message = f"Doctors:\n" + "\n".join(f"- {name}" for name in usernames)
            else:
                message = f"No user found with ID {user_id}."

            dispatcher.utter_message(text=message)

        except Error as e:
            # Handle any database connection or query execution errors
            dispatcher.utter_message(text=f"Database connection failed: {e}")

        finally:
            # Ensure the cursor and connection are properly closed
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

        return []
