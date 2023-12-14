import streamlit as st

# Function for LLM API interaction (dummy function for illustration)
def generate_response(user_input):
    # Replace this with your actual LLM API code
    # Example: response = openai.Completion.create(model="text-davinci-002", prompt=user_input, ...)
    # generated_text = response['choices'][0]['text']
    # return generated_text

    # For illustration purposes, a dummy default response
    return "I'm an AI, ask me anything!"

# Streamlit app layout with improved styling
def main():
    # Set page configuration
    st.set_page_config(
        page_title="Easy Data Retrieval and Inferencing Using Python and LangChain",
        page_icon=":speech_balloon:",
        layout="wide",
    )

    # Set a more vivid purple theme
    vivid_purple = "#7E3AC1"
    st.markdown(
        f"""
        <style>
            body {{
                background-color: {vivid_purple};
                color: #ffffff;
            }}
            .css-1aumxhk {{
                width: 85%;
                max-width: 85%;
            }}
            .sidebar .sidebar-content {{
                background-color: {vivid_purple};
            }}
            .css-1s0lmgv {{
                color: #c9c4d1;
            }}
            .css-17eq0hr {{
                color: #ffffff;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Main content for chat-like UI
    st.title("Easy Data Retrieval and Inferencing Using Python and LangChain")

    # Display user input and LLM-generated response in a chat-like format
    with st.form(key='chat_form'):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_area("You:", height=200)
        with col2:
            options = ["Data Retrieval", "Data Inference", "Follow Up"]
            selected_option = st.selectbox("Select an Option", options)
            st.write("")  # Adjusts spacing
            submit_button = st.form_submit_button(label='Send')

        if submit_button:  # Check if the button is pressed
            if user_input:  # If the input field is not empty
                response = generate_response(user_input)

                # Display user input and LLM-generated response in a chat-like format
                st.text("")
                st.text("You: " + user_input)
                st.text("AI: " + response)

if __name__ == "__main__":
    main()
