from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from flask_cors import CORS
import traceback

# Load environment variables
load_dotenv()

# Check if API key is present
if not os.getenv('GROQ_API_KEY'):
    print("Warning: GROQ_API_KEY not found in environment variables")

app = Flask(__name__)
CORS(app)

# Initialize nutrition agent
try:
    from phi.agent import Agent
    from phi.model.groq import Groq
    from phi.tools.wikipedia import WikipediaTools
    from phi.tools.duckduckgo import DuckDuckGo

    nutrition_agent = Agent(
        name="Nutrition Diet Planner Agent",
        model=Groq(id="meta-llama/llama-4-maverick-17b-128e-instruct"),
        tools=[
            WikipediaTools(),
            DuckDuckGo()
        ],
        instructions=[
            "ALWAYS respond using proper markdown formatting for all structured content.",
            "ONLY provide answers related to nutrition, dietary science, wellness, and human health.",
            "If a question is unrelated to nutrition or health, dont give any asnwers just respond with: '⚠️ I am a Nutrition and Health Specialist AI Agent. Please ask questions related only to nutrition, diet, or health-related wellness topics.'",
            "Use bullet points for lists and steps.",
            "Format headings using ## symbols.",
            "Use **bold** for important terms and metrics.",
            "Separate sections with horizontal rules (---)",
            "You are a certified nutrition specialist and diet planner with expertise in human nutrition, dietary sciences, and wellness.",
            "Create personalized meal plans based on user's goals, preferences, allergies, medical conditions, and dietary patterns.",
            "Always present meal plans and schedules in well-structured tables.",
            "Ask for key information if not provided: age, weight, height, gender, activity level, dietary preferences, medical conditions, food allergies, and specific goals.",
            "Calculate personalized caloric and macronutrient needs based on user information.",
            "Provide nutritional guidance for health goals like weight loss, muscle gain, energy boosting, or medical condition support.",
            "Suggest food item substitutions if necessary based on preferences or restrictions.",
            "Include recovery strategies such as hydration, gut health support, and mindful eating.",
            "Use markdown formatting to enhance readability of your responses.",
            "Cite reputable sources for any specific claims or dietary recommendations.",
            "Prioritize user safety and recommend professional consultation when appropriate.",
            "Track user progress and adjust plans based on feedback.",
            "Include measurement units in both metric and imperial when relevant.",
        ],
        show_tool_calls=False,
        markdown=True,
    )
    print("Successfully initialized nutrition agent")
except Exception as e:
    print(f"Error initializing nutrition agent: {str(e)}")
    print(traceback.format_exc())
    nutrition_agent = None

# Serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Chatbot endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Check if nutrition_agent was properly initialized
        if nutrition_agent is None:
            return jsonify({'response': 'The nutrition agent failed to initialize. Check server logs.'}), 500

        data = request.json
        if not data:
            return jsonify({'response': 'No data received'}), 400

        user_message = data.get('message', '')
        if not user_message:
            return jsonify({'response': 'Please provide a message'}), 400

        # Get response from nutrition agent
        print(f"Processing message: {user_message}")
        response_obj = nutrition_agent.run(user_message)

        # Extract the string content from the RunResponse object
        print(f"Response type: {type(response_obj)}")

        if hasattr(response_obj, 'content'):
            response_text = response_obj.content
        elif hasattr(response_obj, 'text'):
            response_text = response_obj.text
        elif hasattr(response_obj, '__str__'):
            response_text = str(response_obj)
        else:
            response_text = "Received a response from the AI but couldn't extract the text content."

        print(f"Response extracted: {response_text[:100]}...")  # Print first 100 chars

        # Return the response
        return jsonify({'response': response_text})
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error in /chat endpoint: {str(e)}")
        print(error_traceback)
        return jsonify({'response': f'Server error: {str(e)}. Please check server logs for details.'}), 500

if __name__ == '__main__':
    # Run the app
    app.run(debug=True, port=3012)
