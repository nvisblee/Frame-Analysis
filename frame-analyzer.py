import base64
from openai import OpenAI
import streamlit as st

# OpenAI client setup
client = OpenAI()

# Function to encode the image
def encode_image(image):
    return base64.b64encode(image.read()).decode("utf-8")

# Streamlit app
st.title("Tennis Strategy Analyzer")
st.write("Directions: Provide both your and your opponent's strengths and weaknesses. The more specific you are, the better coaching advice we can give! Then, upload an image for strategy analysis. Make sure that the image shows us the entire court and your opponent. ")

# User inputs
strengths = st.text_input("What are your strengths?")
weaknesses = st.text_input("What are your weaknesses?")
opponent_strength = st.text_input("What are your opponents strengths?")
opponent_weakness = st.text_input("What are your opponents weaknesses?")
handed = st.text_input("Are you right handed or left handed? (type 'right' or 'left')")

# Upload an image (mandatory)
uploaded_image = st.file_uploader("Upload an image (required)", type=["png", "jpg", "jpeg"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a professional tennis coach, and you are an expert at match strategy."}
    ]

# Check for uploaded image and validate inputs
if uploaded_image:
    # Encode the image
    base64_image = encode_image(uploaded_image)

    # Trigger analysis only after button click
    if st.button("Analyze Strategy"):
        if not strengths or not weaknesses or not opponent_strength or not opponent_weakness:
            st.warning("Please provide your strengths, weaknesses, and your opponent's traits!")
        else:
            # First API call to identify the shot
            shot_identification_prompt = [
                {
                    "type": "text",
                    "text": "You are a tennis expert. Please identify what type of shot the player is about to hit in this image (forehand, backhand, slice, etc.). Only provide the shot type and stance - be brief and confident in your assessment. If the image is unclear or doesn't show enough information to determine the shot type, please say so."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]

            with st.spinner("Identifying shot type..."):
                try:
                    shot_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a tennis expert focused on identifying shots."},
                            {"role": "user", "content": shot_identification_prompt}
                        ],
                        max_tokens=300, 
                        temperature=0.7
                    )
                    shot_type = shot_response.choices[0].message.content
                    st.write(f"Shot identified: {shot_type}")

                    # Construct user input message with the identified shot type
                    user_input = [
                        {
                            "type": "text",
                            "text": f"""
                            I am hitting a {shot_type}. My strengths are {strengths}, my weaknesses are {weaknesses}, and I believe my opponent's strengths are {opponent_strength} and weaknesses are {opponent_weakness}.
                            I am about to hit a shot during a tennis match. Based on the following criteria, provide a detailed shot strategy analysis:

                            - **Forehand/backhand Technique**: Should I use an open stance or closed stance? Remember a closed stance should be when the player is comfortable getting to the ball, like inside of the court or in the middle of the court.
                            - **Shot Placement**: Should I aim down the line or cross-court? Look at where both of the players are on the court and determine where it would be best to hit the ball.
                            - **Shot Type**: Should I use a slice, a spin-heavy shot, or a flat shot? Look at all of the types of shots you can hit in tennis, even be creative with it, whatever is possible for a human being playing tennis help us with that.
                            - **Special Shots**: Should I hit a lob, drop shot, or dip the ball at my opponent's feet? (Hint: Look at the other player on the other side of the court and take into account what type of shot. For example, if the opponent is at the net, look to see if we could lob or hit a passing shot, etc).

                            Additional Considerations:
                            - Factor in potential opponent positioning and tactical advantages/disadvantages. You have to try and take as many possibilities where we should hit the shot but come up with the most logical shot that can be hit for winning the point.
                            - Based on the opponent's strengths and weaknesses, take into consideration where they should hit the shot. For example, if the opponent's weaknesses are backhands and the ball is in the middle of the court, tell them to hit it to the backhand.
                            - Provide reasoning for your recommendations. For example, if you tell them to hit cross-court, tell them why this would be the best choice.
                            - Give specific advice for the shot itself based on where both players are on the court. For example, if the person is on one side of the court like to the left, the other can hit it to the right unless there are circumstances that are obvious like their clear weaknesses that the user clarified.
                            - Take your time, look where the players are positioned on the court, if it's inconclusive, you can tell the user; otherwise, devise the strategy.
                            - Sound more human-like, make it seem like you are the coach and not making it sound AI-generated. Like make it more interactive to make the player really understand why it's a good shot.
                            - If you feel like the image is not positioned correctly (ideally positioned to where you can see the entire court and not just the player), please say it and ask to upload another image. If you cannot see the other player on the other side, then don't give a response no matter what. You need to see the player near this side, the player on the far side, and if it's anything else, please don't give them a response and say upload another image or something along those lines.
                            - If their weaknesses or strengths they stated are not relevant to the shot they should/are about to hit, then just ignore it. Like, for example, if they are going to hit a forehand and their backhand is their weakness, just ignore it.
                            - You need to take into account which is the best shot to hit. For example, if the player on the opposite side is moved to the very left or right, then we should probably hit to the open court (this is only an example and shouldn't be used if you don't think that's the proper shot to hit when the user uploads it).
                            - You need to also let the user know if the shot they should have hit be risky or safe (an example is when the other player is at the net, we should rip like a flat shot because we are positioned weirdly outside of the court).
                            - Look at what type of shot the person is about to hit. If they are about to hit a backhand slice, for example, give them specific advice there. If they are hitting a forehand, tell them where to go. Also, please look at the positioning of the players. Look how close they are to the baseline, service line, etc., and give specific advice for their positions as well.
                            - The examples are meant to guide you in assisting the players. They provide a baseline for what to look for, but you should only apply them if relevant to the specific image and situation. But please if it's not applied to the image please don't apply it as my examples might not be good so trust your own gut.
                            """
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]

                    st.session_state.messages.append({"role": "user", "content": user_input})

                    # Second API call for strategy (your existing code)
                    with st.spinner("Analyzing strategy..."):
                        try:
                            response = client.chat.completions.create(
                                model="gpt-4o", 
                                messages=st.session_state.messages,
                                max_tokens=2048
                            )
                            reply = response.choices[0].message.content
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                            st.chat_message("assistant").write(reply)
                        except Exception as e:
                            st.error(f"Error in strategy analysis: {e}")
                except Exception as e:
                    st.error(f"Error in shot identification: {e}")

# Follow-up chat input
user_query = st.chat_input("Ask for further clarifications or strategies...")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.spinner("Thinking..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                max_tokens=1024
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").write(reply)
        except Exception as e:
            st.error(f"Error: {e}")