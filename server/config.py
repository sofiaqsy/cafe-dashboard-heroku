import os
import json
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

# Configuración básica
class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cafe-dashboard-secret-key'
    DEBUG = False
    TESTING = False
    
    # Google Sheets
    SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
    GOOGLE_CREDENTIALS = os.environ.get('GOOGLE_CREDENTIALS')
    
    # Otras configuraciones
    LOG_LEVEL = logging.INFO
    
    # Métodos auxiliares
    @staticmethod
    def get_google_credentials_dict():
        """Convierte las credenciales de Google de string JSON a diccionario"""
        try:
            if Config.GOOGLE_CREDENTIALS:
                return json.loads(Config.GOOGLE_CREDENTIALS)
            return None
        except json.JSONDecodeError:
            logging.error("Error al decodificar las credenciales de Google. Verifique el formato JSON.")
            return None

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    
    # En producción, podemos aumentar la seguridad
    @classmethod
    def init_app(cls, app):
        # Configuraciones adicionales para producción
        # Por ejemplo, configuración de logging, seguridad, etc.
        pass

# Diccionario para seleccionar la configuración según el entorno
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Determinar la configuración a utilizar basada en la variable de entorno
def get_config():
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])
