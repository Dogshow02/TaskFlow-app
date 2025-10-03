from flask import Blueprint, send_from_directory, current_app
import os

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/taskflow', defaults={'path': ''})
@frontend_bp.route('/taskflow/<path:path>')
def serve_taskflow(path):
    """Servir a aplicação TaskFlow"""
    static_folder = current_app.static_folder
    taskflow_folder = os.path.join(static_folder, 'taskflow')
    
    if path != "" and os.path.exists(os.path.join(taskflow_folder, path)):
        return send_from_directory(taskflow_folder, path)
    else:
        return send_from_directory(taskflow_folder, 'index.html')

@frontend_bp.route('/css/<path:filename>')
def serve_css(filename):
    """Servir arquivos CSS"""
    return send_from_directory(os.path.join(current_app.static_folder, 'css'), filename)

@frontend_bp.route('/js/<path:filename>')
def serve_js(filename):
    """Servir arquivos JavaScript"""
    return send_from_directory(os.path.join(current_app.static_folder, 'js'), filename)

@frontend_bp.route('/img/<path:filename>')
def serve_img(filename):
    """Servir imagens"""
    return send_from_directory(os.path.join(current_app.static_folder, 'img'), filename)
