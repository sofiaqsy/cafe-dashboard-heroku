import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Crear y configurar la aplicación Flask"""
    # Crear aplicación Flask
    app = Flask(__name__, static_folder='../client/build', static_url_path='')
    CORS(app)  # Habilitar CORS para todas las rutas
    
    # Cargar configuración
    from server.config import get_config
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Configurar logging
    logging.basicConfig(level=app.config.get('LOG_LEVEL', logging.INFO))
    
    # Registrar rutas
    from server.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Ruta para servir la aplicación React
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Servir la aplicación React"""
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    # Ruta para verificación de estado
    @app.route('/health')
    def health():
        """Verificar estado de la aplicación"""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    return app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    # Obtener puerto de Heroku o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
