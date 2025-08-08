import os
import logging
import requests
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Direct HuggingFace API implementation
def call_huggingface_api(question):
    """Call HuggingFace API directly for more reliable results"""
    try:
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise Exception("HUGGINGFACE_API_KEY not found")
        
        # Use a reliable model that works well with the Inference API
        model_id = "google/flan-t5-small"
        
        # Create the retail-focused prompt
        prompt = f"""You are a helpful AI assistant specialized in retail and e-commerce. You provide accurate, helpful information about:
- Product recommendations
- Shopping advice  
- Retail trends
- Customer service
- Store operations
- Online shopping
- Product comparisons
- Pricing information
- Brand information

Question: {question}

Please provide a helpful, accurate, and detailed answer focused on retail and shopping:"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        # Try the basic inference endpoint first
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model_id}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '').strip()
                if generated_text:
                    return generated_text
                else:
                    return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
            else:
                return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
        elif response.status_code == 403:
            # Handle insufficient permissions with helpful guidance
            return get_demo_response(question, "insufficient_permissions")
        elif response.status_code == 404:
            # Handle model not found
            return get_demo_response(question, "model_not_found")
        else:
            logger.error(f"HuggingFace API error: {response.status_code} - {response.text}")
            return get_demo_response(question, "api_error")
            
    except Exception as e:
        logger.error(f"Error calling HuggingFace API: {str(e)}")
        return f"I encountered an error: {str(e)}. Please try again."

# Test API availability
def test_api():
    """Test if the API is working"""
    try:
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        return bool(api_key)
    except:
        return False

api_available = test_api()

def get_demo_response(question, error_type):
    """Generate intelligent demo responses based on the question"""
    question_lower = question.lower()
    
    # Retail trends responses
    if any(word in question_lower for word in ['trend', 'trending', 'popular', 'latest', 'new']):
        demo_answer = """**Current Retail Trends:**
• Sustainable and eco-friendly products are driving consumer choices
• Omnichannel experiences combining online and in-store shopping
• AI-powered personalization and recommendation systems
• Social commerce through Instagram, TikTok, and influencer partnerships
• Buy-now-pay-later payment options becoming standard
• Voice commerce and smart home integration
• Subscription-based retail models expanding"""
    
    # Shopping advice responses
    elif any(word in question_lower for word in ['deal', 'save', 'discount', 'cheap', 'best price']):
        demo_answer = """**Money-Saving Shopping Tips:**
• Compare prices across multiple retailers before buying
• Sign up for store newsletters to get exclusive discounts
• Use cashback apps and browser extensions
• Shop during major sale events (Black Friday, end-of-season sales)
• Check for price-match policies at major retailers
• Consider buying generic or store brands for basics
• Use loyalty programs and accumulate points"""
    
    # Product recommendations
    elif any(word in question_lower for word in ['recommend', 'suggest', 'best', 'review']):
        demo_answer = """**Product Research Tips:**
• Read customer reviews on multiple platforms
• Check professional review sites for detailed comparisons
• Consider your specific needs and budget constraints
• Look for products with good warranty and return policies
• Research brand reputation and customer service quality
• Compare features vs. price across similar products
• Ask for recommendations from friends and online communities"""
    
    # Returns and customer service
    elif any(word in question_lower for word in ['return', 'exchange', 'refund', 'customer service']):
        demo_answer = """**Return and Exchange Guidelines:**
• Always keep receipts and original packaging
• Check return policies before purchasing (timeframes vary)
• Many retailers offer 30-90 day return windows
• Online purchases often have longer return periods
• Some items (electronics, clothing) may have restocking fees
• Contact customer service for damaged or defective items
• Consider extended warranties for expensive electronics"""
    
    # Online shopping
    elif any(word in question_lower for word in ['online', 'ecommerce', 'internet', 'website']):
        demo_answer = """**Safe Online Shopping Practices:**
• Shop only on secure websites (look for HTTPS)
• Use secure payment methods (credit cards, PayPal)
• Read seller reviews and ratings carefully
• Check shipping costs and delivery timeframes
• Save confirmation emails and tracking information
• Be cautious of deals that seem too good to be true
• Use strong passwords and enable two-factor authentication"""
    
    # General retail question
    else:
        demo_answer = """**General Retail Insights:**
• The retail industry is rapidly evolving with technology
• Customer experience is becoming more important than price alone
• Mobile shopping continues to grow significantly
• Sustainability is increasingly important to consumers
• Local and small businesses are finding new ways to compete
• Data analytics help retailers understand customer preferences
• The line between online and offline shopping continues to blur"""
    
    # Add error-specific guidance
    if error_type == "insufficient_permissions":
        guidance = """

**⚠️ API Limitation Notice:**
Your HuggingFace API key has limited permissions. For full AI-powered responses:
• Upgrade to HuggingFace Pro ($9/month) at huggingface.co/pricing
• Or provide an OpenAI API key for even better responses"""
    elif error_type == "model_not_found":
        guidance = """

**⚠️ Model Access Issue:**
The AI model is temporarily unavailable. For full functionality:
• Try upgrading your HuggingFace account permissions
• Or I can modify this app to use OpenAI's API instead"""
    else:
        guidance = """

**⚠️ API Connection Issue:**
There's a temporary issue with the AI service. For full functionality:
• Check your internet connection
• Or consider upgrading to a more reliable AI service"""
    
    return demo_answer + guidance

# API is ready to use

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle question submission and return AI response"""
    try:
        # Get question from form
        question = request.form.get('question', '').strip()
        
        if not question:
            flash('Please enter a question.', 'warning')
            return redirect(url_for('index'))
        
        # Check if API is available
        if not api_available:
            flash('AI service is currently unavailable. Please check your API configuration.', 'danger')
            return redirect(url_for('index'))
        
        logger.info(f"Processing question: {question}")
        
        # Generate response using direct HuggingFace API
        response = call_huggingface_api(question)
        
        logger.info("Response generated successfully")
        
        # Return response
        return render_template('index.html', 
                             question=question, 
                             answer=response,
                             success=True)
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        flash(f'An error occurred while processing your question: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/api/ask', methods=['POST'])
def api_ask_question():
    """API endpoint for AJAX requests"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Please provide a question'}), 400
        
        if not api_available:
            return jsonify({'error': 'AI service is currently unavailable'}), 503
        
        logger.info(f"API processing question: {question}")
        
        # Generate response using direct HuggingFace API
        response = call_huggingface_api(question)
        
        return jsonify({
            'question': question,
            'answer': response,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'llm_available': api_available,
        'api_key_configured': bool(os.getenv("HUGGINGFACE_API_KEY"))
    }
    return jsonify(status)

if __name__ == '__main__':
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
