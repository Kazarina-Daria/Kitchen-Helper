# Kitchen Helper

A Flask web application that helps you find recipes based on ingredients you have available, powered by the [Spoonacular Food API](https://spoonacular.com/food-api).

## Features

- **Search Recipes by Ingredients**: Enter ingredients you have and find recipes you can make
- **Recipe Details**: View detailed recipe information including ingredients and instructions
- **Dynamic Recipe Display**: Real-time recipe suggestions based on your available ingredients

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Spoonacular API Key

1. Sign up for a free API key at [https://spoonacular.com/food-api](https://spoonacular.com/food-api)
2. Set your API key as an environment variable:

   **Windows (PowerShell):**
   ```powershell
   $env:SPOONACULAR_API_KEY="your_api_key_here"
   ```

   **Windows (Command Prompt):**
   ```cmd
   set SPOONACULAR_API_KEY=your_api_key_here
   ```

   **Linux/Mac:**
   ```bash
   export SPOONACULAR_API_KEY=your_api_key_here
   ```

   **Alternatively**, you can modify `app.py` and set the API key directly (not recommended for production):
   ```python
   SPOONACULAR_API_KEY = 'your_api_key_here'
   ```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Home Page (`/`)**: Enter ingredients (comma-separated) in the left sidebar and click "Search Recipes"
2. **Recipe Results**: View recipes you can make with your ingredients
3. **Recipe Details**: Click on any recipe to see full details, ingredients, and instructions
4. **Contact Page (`/contact`)**: Submit a contact form (data is printed to console)

## API Endpoints

### Backend Routes

- `GET /` - Home page with recipe search
- `POST /` - Search recipes by ingredients (form submission)
- `GET /about` - About page
- `GET /contact` - Contact form page
- `POST /contact` - Submit contact form
- `GET /recipe/<recipe_id>` - View detailed recipe information
- `POST /api/search` - JSON API endpoint for searching recipes

### Spoonacular API Integration

The application uses the [Spoonacular "Search Recipes by Ingredients" endpoint](https://spoonacular.com/food-api/docs#Search-Recipes-by-Ingredients):

- **Endpoint**: `GET https://api.spoonacular.com/recipes/findByIngredients`
- **Function**: `search_recipes_by_ingredients()` in `app.py`
- **Parameters**: 
  - `ingredients`: List of ingredient names
  - `number`: Maximum recipes to return (default: 10)
  - `ranking`: 1 to maximize used ingredients, 2 to minimize missing ingredients
  - `ignorePantry`: Whether to ignore pantry items (default: True)

## Project Structure

```
Kitchen-Helper/
├── app.py                 # Main Flask application with API integration
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── index.html        # Home page with recipe search
│   ├── about.html        # About page
│   ├── contact.html      # Contact form page
│   ├── recipe_detail.html # Recipe detail page
│   └── error.html        # Error page
└── static/               # Static files (CSS, images)
    └── styles.css       # Stylesheet
```

## Code Modification Guide

### Adding New API Endpoints

To add new Spoonacular API endpoints, create functions in `app.py`:

```python
def your_new_function(params):
    url = f"{SPOONACULAR_BASE_URL}/your-endpoint"
    params = {'apiKey': SPOONACULAR_API_KEY, ...}
    response = requests.get(url, params=params)
    return response.json()
```

### Modifying Recipe Search

Edit the `search_recipes_by_ingredients()` function in `app.py` to change:
- Number of results returned
- Ranking algorithm
- Pantry item filtering

### Adding New Routes

Add new routes in `app.py`:

```python
@app.route('/your-route')
def your_function():
    # Your logic here
    return render_template('your_template.html')
```

## API Rate Limits

The free Spoonacular API plan includes:
- **Daily quota**: Check your dashboard for your plan's quota
- **Rate limit**: 60 requests per minute (free plan)
- Each request costs 1 point + 0.01 points per result

See [Spoonacular Rate Limiting Documentation](https://spoonacular.com/food-api/docs#Rate-Limiting-&-Quotas) for details.

## License

This project uses the Spoonacular Food API. Please review their [Terms & Conditions](https://spoonacular.com/food-api/terms) when using the API.