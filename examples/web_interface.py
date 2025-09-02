"""
Flask Web Interface for Chat Moderation Plugin

A simple web interface to manage and monitor the chat moderation system.
Requires Flask: pip install flask
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import sys
import os
from datetime import datetime

# Add parent directory to path to import moderation modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from moderation_api import ModerationAPI

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production!

# Initialize moderation API
moderation_api = ModerationAPI()


@app.route('/')
def dashboard():
    """Main dashboard"""
    stats = moderation_api.get_stats()
    recent_violations = moderation_api.get_violations(days=7)
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_violations=recent_violations[:10])


@app.route('/api/moderate', methods=['POST'])
def api_moderate_message():
    """API endpoint to moderate a message"""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'message' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = moderation_api.moderate_message(
        user_id=data['user_id'],
        message=data['message'],
        channel_id=data.get('channel_id'),
        user_roles=data.get('user_roles', [])
    )
    
    return jsonify(result)


@app.route('/api/user/<user_id>')
def api_get_user(user_id):
    """API endpoint to get user information"""
    user_status = moderation_api.get_user_status(user_id)
    violations = moderation_api.get_violations(user_id, days=30)
    
    return jsonify({
        'user_status': user_status,
        'violations': violations
    })


@app.route('/api/action', methods=['POST'])
def api_apply_action():
    """API endpoint to apply manual moderation action"""
    data = request.get_json()
    
    required_fields = ['user_id', 'action']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    success = moderation_api.apply_manual_action(
        user_id=data['user_id'],
        action=data['action'],
        duration=data.get('duration', 300),
        reason=data.get('reason', 'Manual action via web interface'),
        moderator_id=data.get('moderator_id')
    )
    
    return jsonify({'success': success})


@app.route('/api/stats')
def api_get_stats():
    """API endpoint to get moderation statistics"""
    return jsonify(moderation_api.get_stats())


@app.route('/api/violations')
def api_get_violations():
    """API endpoint to get violations"""
    user_id = request.args.get('user_id')
    days = int(request.args.get('days', 7))
    
    violations = moderation_api.get_violations(user_id, days)
    return jsonify(violations)


@app.route('/users')
def users_page():
    """Users management page"""
    # Get all users that have been tracked
    all_users = {}
    for user_id, user_data in moderation_api.plugin.users.items():
        all_users[user_id] = {
            'user_id': user_id,
            'is_muted': user_data.is_muted,
            'is_banned': user_data.is_banned,
            'violation_count': user_data.violation_count,
            'mute_until': user_data.mute_until.isoformat() if user_data.mute_until else None,
            'ban_until': user_data.ban_until.isoformat() if user_data.ban_until else None
        }
    
    return render_template('users.html', users=all_users)


@app.route('/config')
def config_page():
    """Configuration management page"""
    config = moderation_api.plugin.config
    return render_template('config.html', config=config)


@app.route('/config/update', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        # Get form data and convert to config updates
        config_updates = {}
        
        # Handle checkbox values for enabled/disabled settings
        for key in request.form:
            value = request.form[key]
            
            # Convert string values to appropriate types
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                value = float(value)
            
            # Build nested config structure
            keys = key.split('.')
            current = config_updates
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            current[keys[-1]] = value
        
        success = moderation_api.update_config(config_updates)
        
        if success:
            flash('Configuration updated successfully!', 'success')
        else:
            flash('Failed to update configuration.', 'error')
            
    except Exception as e:
        flash(f'Error updating configuration: {str(e)}', 'error')
    
    return redirect(url_for('config_page'))


@app.route('/test')
def test_page():
    """Test moderation page"""
    return render_template('test.html')


@app.route('/test/message', methods=['POST'])
def test_message():
    """Test message moderation"""
    user_id = request.form.get('user_id', 'test_user')
    message = request.form.get('message', '')
    
    if message:
        result = moderation_api.moderate_message(user_id, message)
        return render_template('test.html', 
                             test_result=result, 
                             test_message=message, 
                             test_user_id=user_id)
    
    return redirect(url_for('test_page'))


# Template files (would normally be in templates/ directory)
templates = {
    'base.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Chat Moderation{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav { background: #333; color: white; padding: 10px; margin: -20px -20px 20px -20px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
        .violation-item { background: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #ffc107; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #0056b3; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 4px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/users">Users</a>
            <a href="/config">Configuration</a>
            <a href="/test">Test</a>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'error' }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>
''',

    'dashboard.html': '''
{% extends "base.html" %}

{% block title %}Dashboard - Chat Moderation{% endblock %}

{% block content %}
<h1>Moderation Dashboard</h1>

<div class="stats">
    <div class="stat-card">
        <h3>Total Violations</h3>
        <h2>{{ stats.total_violations }}</h2>
    </div>
    <div class="stat-card">
        <h3>Active Mutes</h3>
        <h2>{{ stats.active_mutes }}</h2>
    </div>
    <div class="stat-card">
        <h3>Active Bans</h3>
        <h2>{{ stats.active_bans }}</h2>
    </div>
    <div class="stat-card">
        <h3>Users Tracked</h3>
        <h2>{{ stats.total_users_tracked }}</h2>
    </div>
</div>

{% if stats.violation_types %}
<h2>Violation Types</h2>
<table>
    <thead>
        <tr>
            <th>Type</th>
            <th>Count</th>
        </tr>
    </thead>
    <tbody>
        {% for vtype, count in stats.violation_types.items() %}
        <tr>
            <td>{{ vtype.title() }}</td>
            <td>{{ count }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endif %}

<h2>Recent Violations (Last 7 Days)</h2>
{% if recent_violations %}
    {% for violation in recent_violations %}
    <div class="violation-item">
        <strong>{{ violation.user_id }}</strong> - {{ violation.violation_type }} 
        <small>({{ violation.timestamp }})</small><br>
        <em>{{ violation.message[:100] }}{% if violation.message|length > 100 %}...{% endif %}</em>
    </div>
    {% endfor %}
{% else %}
    <p>No recent violations found.</p>
{% endif %}
{% endblock %}
''',

    'test.html': '''
{% extends "base.html" %}

{% block title %}Test Moderation - Chat Moderation{% endblock %}

{% block content %}
<h1>Test Message Moderation</h1>

<form method="POST" action="/test/message">
    <div class="form-group">
        <label for="user_id">User ID:</label>
        <input type="text" id="user_id" name="user_id" value="{{ test_user_id or 'test_user' }}" required>
    </div>
    
    <div class="form-group">
        <label for="message">Message to Test:</label>
        <textarea id="message" name="message" rows="3" placeholder="Enter a message to test..." required>{{ test_message or '' }}</textarea>
    </div>
    
    <button type="submit" class="btn">Test Message</button>
</form>

{% if test_result %}
<h2>Moderation Result</h2>
<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <p><strong>Allowed:</strong> {{ test_result.allowed }}</p>
    <p><strong>Violations:</strong> {{ test_result.violations | join(', ') if test_result.violations else 'None' }}</p>
    <p><strong>Actions Taken:</strong> {{ test_result.actions_taken | join(', ') if test_result.actions_taken else 'None' }}</p>
    
    {% if test_result.user_status %}
    <h3>User Status</h3>
    <p><strong>Is Muted:</strong> {{ test_result.user_status.is_muted }}</p>
    <p><strong>Is Banned:</strong> {{ test_result.user_status.is_banned }}</p>
    <p><strong>Violation Count:</strong> {{ test_result.user_status.violation_count }}</p>
    {% endif %}
</div>
{% endif %}

<h2>Sample Test Messages</h2>
<ul>
    <li>Clean message: "Hello everyone, how are you today?"</li>
    <li>Profanity: "This is a damn test message"</li>
    <li>Caps abuse: "THIS IS ALL CAPS AND VERY ANNOYING"</li>
    <li>Spam: "buy now buy now buy now buy now"</li>
</ul>
{% endblock %}
'''
}


def create_template_files():
    """Create template files if they don't exist"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    for filename, content in templates.items():
        filepath = os.path.join(template_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(content)


if __name__ == '__main__':
    create_template_files()
    
    print("Starting Chat Moderation Web Interface...")
    print("Open your browser to http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)