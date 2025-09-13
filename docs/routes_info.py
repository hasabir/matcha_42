import yaml
from flask import Blueprint, current_app, render_template
import os

# Create the blueprint with a proper name
docs_bp = Blueprint('docs_bp', __name__)

@docs_bp.route("/info", methods=["GET"])
def api_docs():
    """Endpoint to display API documentation in HTML format"""
    
    # Load the YAML file from the docs directory
    yaml_file_path = os.path.join(current_app.root_path, 'docs', 'routes_info.yml')
    
    try:
        with open(yaml_file_path, 'r') as file:
            routes_data = yaml.safe_load(file)
    except FileNotFoundError:
        return "Routes documentation file not found", 404
    except yaml.YAMLError as e:
        return f"Error parsing YAML file: {e}", 500
    
    # Generate HTML content
    html_content = generate_html_docs(routes_data['routes'])
    
    return html_content

def generate_html_docs(routes):
    """Generate HTML documentation from routes data"""
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Documentation</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }}
            .route {{
                background: #f8f9fa;
                border-left: 4px solid #007bff;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 4px;
            }}
            .endpoint {{
                font-weight: bold;
                color: #007bff;
                font-family: monospace;
                font-size: 1.1em;
            }}
            .methods {{
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.9em;
                margin-left: 10px;
            }}
            .protected {{
                display: inline-block;
                background: #dc3545;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.9em;
                margin-left: 10px;
            }}
            .description {{
                margin-top: 10px;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>API Documentation</h1>
            <p>Total routes: {len(routes)}</p>
    """
    
    for route in routes:
        methods_html = "".join([f'<span class="methods">{method}</span>' for method in route['methods']])
        protected_html = '<span class="protected">🔒 Auth Required</span>' if route['protected'] else '<span style="color: #6c757d;">No Auth</span>'
        
        html += f"""
            <div class="route">
                <div>
                    <span class="endpoint">{route['endpoint']}</span>
                    {methods_html}
                    {protected_html}
                </div>
                <div class="description">
                    {route['description']}
                </div>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html