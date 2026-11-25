import streamlit as st
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


st.set_page_config(
    page_title="Disney Park Advisor",
    page_icon="🏰"
)

st.title("🏰 Disney Park Advisor")
st.write(
    "Your friendly assistant for planning a magical Disney World vacation!"
)

api_key = st.secrets["GOOGLE_API_KEY"]

model = GoogleModel(
    "gemini-3.5-flash-lite",
    provider=GoogleProvider(api_key=api_key)
)

agent = Agent(
    model,
    instructions="""
    You are Disney Park Advisor, a friendly and knowledgeable
    assistant who helps visitors plan enjoyable Walt Disney World
    vacations.

    Your responsibilities:
    - Give helpful advice about Disney World attractions and parks.
    - Suggest general strategies for planning a park visit.
    - Help visitors think about ride priorities, breaks, and schedules.
    - Be friendly, positive, and easy to understand.
    - Keep answers reasonably short and organized.

    Important limitations:
    - You do not have access to live attraction wait times.
    - You cannot check current park hours, ticket prices, or availability.
    - Do not pretend to have access to real-time information.
    - If someone asks for live information, explain that you cannot
      retrieve it and suggest checking Disney's official website.

    Stay focused on Walt Disney World and vacation planning.
    """
)


if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "agent_history" not in st.session_state:
    st.session_state.agent_history = []



for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



prompt = st.chat_input("Ask me anything about Disney World...")

if prompt:

    # Display the user's message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Ask Gemini for a response
    with st.chat_message("assistant"):

        try:
            with st.spinner("Planning something magical..."):

                result = agent.run_sync(
                    prompt,
                    message_history=st.session_state.agent_history
                )

                response = result.output

                # Save the conversation for the next question
                st.session_state.agent_history = result.all_messages()

            st.markdown(response)

        except Exception as e:
            response = (
            "Sorry, something went wrong while contacting "
            "the AI assistant. Please try again."
            )

            st.error(response)
      

    # Save the response for display
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": response
    })




if st.sidebar.button("Clear Conversation"):
    st.session_state.chat_messages = []
    st.session_state.agent_history = []
    st.rerun()
