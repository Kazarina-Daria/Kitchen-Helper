"""
Flask Application for Kitchen Helper Web Application

This is the main application file that sets up Flask routes and handles requests.
To run the application, execute: python app.py

MODIFICATION GUIDE:
- To add new routes: Add new @app.route() decorators below
- To add new pages: Create HTML files in templates/ folder and render them with render_template()
- To add static assets: Place files in static/ folder and reference with url_for('static', filename='...')
- To modify form handling: Update the contact() function below
- To change API key: Set SPOONACULAR_API_KEY environment variable or modify SPOONACULAR_API_KEY below
"""

import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session

# Initialize Flask application
# __name__ tells Flask where to find templates and static files
app = Flask(__name__)

# Enable debug mode for development (shows detailed error messages)
# IMPORTANT: Set to False in production!
app.config['DEBUG'] = True

# Secret key for session management (change this in production!)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Spoonacular API Configuration
# Get API key from environment variable or set it directly here
# To get a free API key, sign up at: https://spoonacular.com/food-api
# 
# Option 1: Set environment variable (recommended for production)
#   Windows: set SPOONACULAR_API_KEY=your_key_here
#   Linux/Mac: export SPOONACULAR_API_KEY=your_key_here
#
# Option 2: Set it directly below (used as fallback if env var not set)
# The environment variable takes precedence if set
SPOONACULAR_API_KEY = os.environ.get('SPOONACULAR_API_KEY', 'af307cfbe92e4047b0ef9c205d310b55')
SPOONACULAR_BASE_URL = 'https://api.spoonacular.com/recipes'


def search_recipes_by_ingredients(ingredients, number=10, ranking=1, ignore_pantry=True):

    if not SPOONACULAR_API_KEY or SPOONACULAR_API_KEY == 'YOUR_API_KEY_HERE':
        return {'error': 'API key not configured. Please set SPOONACULAR_API_KEY environment variable.'}
    
    # Convert ingredients list to comma-separated string
    ingredients_str = ','.join(ingredients)
    
    # API endpoint: https://api.spoonacular.com/recipes/findByIngredients
    url = f"{SPOONACULAR_BASE_URL}/findByIngredients"
    
    # API parameters as per Spoonacular documentation
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'ingredients': ingredients_str,
        'number': number,
        'ranking': ranking,
        'ignorePantry': str(ignore_pantry).lower()
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Spoonacular API: {e}")
        return {'error': f'Failed to fetch recipes: {str(e)}'}


def get_recipe_information(recipe_id):
    """
    Get detailed information about a specific recipe.
    
    Args:
        recipe_id (int): The recipe ID from Spoonacular
    
    Returns:
        dict: Detailed recipe information, or None if error occurred
    
    MODIFICATION GUIDE:
    - To get more recipe details, add parameters like includeNutrition=True
    """
    if not SPOONACULAR_API_KEY or SPOONACULAR_API_KEY == 'YOUR_API_KEY_HERE':
        return {'error': 'API key not configured.'}
    
    url = f"{SPOONACULAR_BASE_URL}/{recipe_id}/information"
    params = {
        'apiKey': SPOONACULAR_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipe information: {e}")
        return {'error': f'Failed to fetch recipe details: {str(e)}'}


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Home page route - handles ingredient submission and displays recipes
    
    GET: Displays the main page with ingredient list, shopping list, and favorites
    POST: Processes ingredient submission, searches for recipes, and displays results
    
    MODIFICATION GUIDE:
    - To change filter behavior, modify the filter logic below
    - To change default shopping list items, modify the initialization
    """
    # Initialize session data if not exists
    if 'shopping_list' not in session:
        session['shopping_list'] = []
    if 'favorites' not in session:
        session['favorites'] = []
    
    recipes = []
    ingredients_list = []
    error_message = None
    filter_type = request.args.get('filter', 'all')  # 'all' or 'favorites'
    
    if request.method == 'POST':
        # Get ingredients from form submission
        # Can come from multiple sources: form field, JSON, or query params
        if request.is_json:
            data = request.get_json()
            ingredients = data.get('ingredients', [])
        else:
            # Get ingredients from form (comma-separated or individual fields)
            ingredients_input = request.form.get('ingredients', '')
            if ingredients_input:
                # Split by comma and clean up whitespace
                ingredients = [ing.strip() for ing in ingredients_input.split(',') if ing.strip()]
            else:
                ingredients = []
        
        if ingredients:
            # Search for recipes using Spoonacular API
            result = search_recipes_by_ingredients(ingredients, number=10)
            
            if 'error' in result:
                error_message = result['error']
            else:
                recipes = result if isinstance(result, list) else []
                # Store ingredients for display
                ingredients_list = ingredients
        else:
            error_message = "Please provide at least one ingredient."
    
    # Filter recipes by favorites if requested
    if filter_type == 'favorites' and recipes:
        favorite_ids = [fav['id'] for fav in session.get('favorites', [])]
        recipes = [r for r in recipes if r.get('id') in favorite_ids]
    
    # Get shopping list and favorites from session
    shopping_list = session.get('shopping_list', [])
    favorites = session.get('favorites', [])
    
    # Calculate shopping list stats
    total_items = len(shopping_list)
    done_items = sum(1 for item in shopping_list if item.get('checked', False))
    
    # If no recipes found and no ingredients searched, get random recipes for inspiration
    random_recipes = []
    if not recipes and not ingredients_list and request.method == 'GET':
        # Get random recipes from Spoonacular API for inspiration
        try:
            random_url = f"{SPOONACULAR_BASE_URL}/random"
            params = {'apiKey': SPOONACULAR_API_KEY, 'number': 5}
            response = requests.get(random_url, params=params, timeout=10)
            if response.status_code == 200:
                random_data = response.json()
                # Handle both single recipe and list of recipes
                if isinstance(random_data, dict):
                    random_recipes = [random_data]
                elif isinstance(random_data, list):
                    random_recipes = random_data
        except Exception as e:
            print(f"Error fetching random recipes: {e}")
            random_recipes = []
    
    return render_template(
        'index.html',
        recipes=recipes,
        ingredients_list=ingredients_list,
        error_message=error_message,
        shopping_list=shopping_list,
        favorites=favorites,
        filter_type=filter_type,
        total_items=total_items,
        done_items=done_items,
        random_recipes=random_recipes
    )


@app.route('/about')
def about():
    """
    About page route - displays information about Kitchen Helper
    
    This route serves the about.html template.
    To modify the about page, edit templates/about.html
    """
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Contact page route - handles both GET and POST requests
    
    GET: Displays the contact form
    POST: Processes form submission and prints data to console
    
    To modify form fields, edit templates/contact.html and update the form processing below.
    """
    if request.method == 'POST':
        # Extract form data from POST request
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Print form data to console (as required)
        print("=" * 50)
        print("FORM SUBMISSION RECEIVED:")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("=" * 50)
        
        # After processing, redirect back to contact page with success message
        # In a real application, you might save this to a database or send an email
        return render_template('contact.html', success=True)
    
    # GET request - just display the form
    return render_template('contact.html', success=False)


@app.route('/api/search', methods=['POST'])
def api_search():
 
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.get_json()
    ingredients = data.get('ingredients', [])
    
    if not ingredients:
        return jsonify({'error': 'Ingredients list is required'}), 400
    
    result = search_recipes_by_ingredients(ingredients, number=10)
    
    if 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result)


@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    """
    Recipe detail page - shows full recipe information
    
    Args:
        recipe_id: The Spoonacular recipe ID
    
    MODIFICATION GUIDE:
    - To add more recipe details, modify get_recipe_information() call
    """
    # Initialize session data if not exists
    if 'favorites' not in session:
        session['favorites'] = []
    
    recipe_info = get_recipe_information(recipe_id)
    
    if 'error' in recipe_info:
        return render_template('error.html', error_message=recipe_info['error']), 500
    
    # Check if recipe is in favorites
    favorites = session.get('favorites', [])
    is_favorite = any(fav.get('id') == recipe_id for fav in favorites)
    
    return render_template('recipe_detail.html', recipe=recipe_info, is_favorite=is_favorite)


# Shopping List Routes
@app.route('/shopping-list/add', methods=['POST'])
def add_shopping_item():
    """
    Add item to shopping list
    
    MODIFICATION GUIDE:
    - To add validation, check item name and quantity before adding
    - To prevent duplicates, check if item already exists
    """
    if 'shopping_list' not in session:
        session['shopping_list'] = []
    
    item_name = request.form.get('item_name', '').strip()
    item_quantity = request.form.get('item_quantity', '').strip()
    
    if item_name:
        new_item = {
            'id': len(session['shopping_list']),
            'name': item_name,
            'quantity': item_quantity if item_quantity else '',
            'checked': False
        }
        session['shopping_list'].append(new_item)
        session.modified = True
        print(f"Added to shopping list: {item_name} ({item_quantity})")
    
    return redirect(url_for('index'))


@app.route('/shopping-list/remove/<int:item_id>', methods=['POST'])
def remove_shopping_item(item_id):
    """
    Remove item from shopping list
    
    MODIFICATION GUIDE:
    - To add confirmation, add a confirmation dialog in the frontend
    """
    if 'shopping_list' in session:
        session['shopping_list'] = [item for item in session['shopping_list'] if item.get('id') != item_id]
        session.modified = True
        print(f"Removed shopping list item ID: {item_id}")
    
    return redirect(url_for('index'))


@app.route('/shopping-list/toggle/<int:item_id>', methods=['POST'])
def toggle_shopping_item(item_id):
    """
    Toggle checked status of shopping list item
    
    MODIFICATION GUIDE:
    - To add bulk toggle, create a new route that accepts multiple IDs
    """
    if 'shopping_list' in session:
        for item in session['shopping_list']:
            if item.get('id') == item_id:
                item['checked'] = not item.get('checked', False)
                session.modified = True
                print(f"Toggled shopping list item ID: {item_id} to {item['checked']}")
                break
    
    return redirect(url_for('index'))


# Favorites Routes
@app.route('/favorites/add', methods=['POST'])
def add_favorite():
    """
    Add recipe to favorites
    
    MODIFICATION GUIDE:
    - To add validation, check if recipe exists before adding
    - To prevent duplicates, check if recipe already in favorites
    """
    if 'favorites' not in session:
        session['favorites'] = []
    
    recipe_id = request.form.get('recipe_id')
    recipe_title = request.form.get('recipe_title', '')
    recipe_image = request.form.get('recipe_image', '')
    
    if recipe_id:
        recipe_id = int(recipe_id)
        # Check if already in favorites
        if not any(fav.get('id') == recipe_id for fav in session['favorites']):
            new_favorite = {
                'id': recipe_id,
                'title': recipe_title,
                'image': recipe_image
            }
            session['favorites'].append(new_favorite)
            session.modified = True
            print(f"Added to favorites: {recipe_title} (ID: {recipe_id})")
        else:
            print(f"Recipe {recipe_id} already in favorites")
    
    # Redirect back to the page that called this
    return_url = request.form.get('return_url', url_for('index'))
    return redirect(return_url)


@app.route('/favorites/remove/<int:recipe_id>', methods=['POST'])
def remove_favorite(recipe_id):
    """
    Remove recipe from favorites
    
    MODIFICATION GUIDE:
    - To add confirmation, add a confirmation dialog in the frontend
    """
    if 'favorites' in session:
        session['favorites'] = [fav for fav in session['favorites'] if fav.get('id') != recipe_id]
        session.modified = True
        print(f"Removed from favorites: Recipe ID {recipe_id}")
    
    # Redirect back to the page that called this
    return_url = request.form.get('return_url', url_for('index'))
    return redirect(return_url)


if __name__ == '__main__':
    """
    Main entry point - runs the Flask development server
    
    The app will be available at http://localhost:5000
    To change the port, add: app.run(port=8080)
    To make it accessible from other machines: app.run(host='0.0.0.0')
    """
    print("Starting Kitchen Helper Flask application...")
    print("Server will be available at http://localhost:5000")
    
    # Check if API key is configured
    if not SPOONACULAR_API_KEY or SPOONACULAR_API_KEY == 'YOUR_API_KEY_HERE':
        print("\n⚠️  WARNING: SPOONACULAR_API_KEY not configured!")
        print("   Set it as an environment variable or modify app.py")
        print("   Get a free API key at: https://spoonacular.com/food-api")
    else:
        print(f"✓ Spoonacular API key configured")
    
    print("Press Ctrl+C to stop the server\n")
    app.run(debug=True)

