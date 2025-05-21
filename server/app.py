import os
import logging
from flask import Flask, jsonify, send_from_directory, request
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
    
    # Verificar si la carpeta static existe
    if not os.path.exists(app.static_folder):
        logger.warning(f"La carpeta static '{app.static_folder}' no existe. Se usará un directorio temporal.")
        # Crear el directorio si no existe
        os.makedirs(app.static_folder, exist_ok=True)
        # Crear un archivo index.html básico si no existe
        index_path = os.path.join(app.static_folder, 'index.html')
        if not os.path.exists(index_path):
            with open(index_path, 'w') as f:
                f.write('<html><body><h1>App en construcción</h1><p>La aplicación está en proceso de despliegue.</p></body></html>')
    
    # Ruta para servir la aplicación React
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Servir la aplicación React"""
        logger.info(f"Solicitando ruta: {path}")
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            logger.info(f"Sirviendo archivo: {path}")
            return send_from_directory(app.static_folder, path)
        
        index_path = os.path.join(app.static_folder, 'index.html')
        if os.path.exists(index_path):
            logger.info("Sirviendo index.html")
            return send_from_directory(app.static_folder, 'index.html')
        else:
            logger.error(f"No se pudo encontrar index.html en {app.static_folder}")
            return jsonify({
                'error': 'Aplicación en configuración',
                'message': 'La aplicación está siendo configurada. Por favor, intente de nuevo más tarde.'
            }), 503
    
    # Ruta para verificación de estado
    @app.route('/health')
    def health():
        """Verificar estado de la aplicación"""
        # Añadir información sobre la configuración
        static_folder_exists = os.path.exists(app.static_folder)
        index_exists = os.path.exists(os.path.join(app.static_folder, 'index.html'))
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'default'),
            'debug': app.debug,
            'static_folder': app.static_folder,
            'static_folder_exists': static_folder_exists,
            'index_exists': index_exists,
            'request_path': request.path
        })
    
    return app

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    # Obtener puerto de Heroku o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
