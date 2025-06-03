"""
Rutas de la API para el backend.
Define los endpoints para acceder a datos de Google Sheets.
"""
import logging
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

from server.sheets_service import (
    get_compras_data, get_ventas_data, get_gastos_data, get_proceso_data, get_almacen_data,
    calculate_daily_summary, get_daily_summaries, get_coffee_types_summary,
    get_detailed_profit_by_process
)

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
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

@api_bp.route('/proceso-ganancia', methods=['GET'])
def proceso_ganancia():
    """
    Obtener el detalle de ganancias por proceso individual
    
    Query parameters:
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
        debug: Si está presente, devuelve información adicional de depuración
    """
    try:
        # Obtener parámetros de consulta
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        include_debug = request.args.get('debug', 'true').lower() in ('true', '1', 't', 'yes')
        
        logger.info(f"Obteniendo ganancias por proceso: {start_date} a {end_date}")
        
        # Si no se especifica end_date, usar la fecha actual
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Si no se especifica start_date, usar el mes actual
        if not start_date:
            # Primer día del mes actual
            current_month = datetime.now().replace(day=1)
            start_date = current_month.strftime('%Y-%m-%d')
        
        # Obtener datos detallados de ganancia por proceso
        data = get_detailed_profit_by_process(start_date, end_date)
        
        # Si no se solicita información de depuración, eliminarla de la respuesta
        if not include_debug and 'debug_info' in data:
            del data['debug_info']
            
        # Agregar información de la solicitud para depuración
        if include_debug:
            if 'debug_info' not in data:
                data['debug_info'] = {}
            data['debug_info']['request'] = {
                'start_date': start_date,
                'end_date': end_date,
                'url': request.url,
                'args': dict(request.args)
            }
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error al obtener ganancia detallada por proceso: {e}")
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(error_traceback)
        return jsonify({
            'error': str(e),
            'traceback': error_traceback,
            'message': 'Error al obtener ganancia detallada por proceso'
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
