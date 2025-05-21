"""
Rutas de la API para el backend.
Define los endpoints para acceder a datos de Google Sheets.
"""
import logging
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

from server.sheets_service import (
    get_compras_data, get_ventas_data, get_gastos_data, get_proceso_data, get_almacen_data,
    calculate_daily_summary, get_daily_summaries, get_coffee_types_summary
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint para las rutas de la API
api_bp = Blueprint('api', __name__)

@api_bp.route('/status', methods=['GET'])
def status():
    """Verificar estado de la API"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat()
    })

@api_bp.route('/summary', methods=['GET'])
def summary():
    """
    Obtener un resumen general de los datos.
    
    Query parameters:
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    """
    try:
        # Obtener parámetros de consulta
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Si no se especifica end_date, usar la fecha actual
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Si no se especifica start_date, usar el mes actual
        if not start_date:
            # Primer día del mes actual
            current_month = datetime.now().replace(day=1)
            start_date = current_month.strftime('%Y-%m-%d')
        
        # Calcular resumen
        data = calculate_daily_summary(start_date, end_date)
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error al obtener resumen: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error al obtener resumen'
        }), 500

@api_bp.route('/daily', methods=['GET'])
def daily_data():
    """
    Obtener datos diarios para un rango de fechas.
    
    Query parameters:
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
    """
    try:
        # Obtener parámetros de consulta
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Si no se especifica end_date, usar la fecha actual
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Si no se especifica start_date, usar una semana antes
        if not start_date:
            # Una semana atrás desde end_date
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            start_date_obj = end_date_obj - timedelta(days=7)
            start_date = start_date_obj.strftime('%Y-%m-%d')
        
        # Obtener datos diarios
        data = get_daily_summaries(start_date, end_date)
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error al obtener datos diarios: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error al obtener datos diarios'
        }), 500

@api_bp.route('/coffee-types', methods=['GET'])
def coffee_types():
    """Obtener resumen de tipos de café"""
    try:
        data = get_coffee_types_summary()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error al obtener tipos de café: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error al obtener tipos de café'
        }), 500

@api_bp.route('/raw/compras', methods=['GET'])
def raw_compras():
    """Obtener datos de compras"""
    try:
        df = get_compras_data()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        logger.error(f"Error al obtener datos de compras: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error al obtener datos de compras'
        }), 500

@api_bp.route('/raw/ventas', methods=['GET'])
def raw_ventas():
    """Obtener datos de ventas"""
    try:
        df = get_ventas_data()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        logger.error(f"Error al obtener datos de ventas: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error al obtener datos de ventas'
        }), 500

@api_bp.route('/raw/gastos', methods=['GET'])
def raw_gastos():
    """Obtener datos de gastos"""
    try:
        df = get_gastos_data()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        logger.error(f"Error al obtener datos de gastos: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error al obtener datos de gastos'
        }), 500

@api_bp.route('/raw/proceso', methods=['GET'])
def raw_proceso():
    """Obtener datos de proceso"""
    try:
        df = get_proceso_data()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        logger.error(f"Error al obtener datos de proceso: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error al obtener datos de proceso'
        }), 500

@api_bp.route('/raw/almacen', methods=['GET'])
def raw_almacen():
    """Obtener datos de almacén"""
    try:
        df = get_almacen_data()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        logger.error(f"Error al obtener datos de almacén: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Error al obtener datos de almacén'
        }), 500
