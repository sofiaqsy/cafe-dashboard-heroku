"""
Servicio para la interacción con Google Sheets.
Proporciona funciones para leer y analizar datos de las hojas de café.
"""
import os
import json
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime
import pytz

from server.config import get_config

# Configurar logging con más detalle
logging.basicConfig(
    level=logging.DEBUG,  # Cambiado a DEBUG para ver más información
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

config = get_config()

# Constantes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_NAMES = {
    'compras': 'Compras',
    'ventas': 'Ventas',
    'gastos': 'Gastos',
    'proceso': 'Proceso',
    'almacen': 'Almacen'
}

def get_credentials():
    """Obtiene las credenciales de Google Sheets desde las variables de entorno"""
    try:
        credentials_info = config.get_google_credentials_dict()
        if not credentials_info:
            logger.error("No se encontraron credenciales de Google válidas")
            return None
            
        return service_account.Credentials.from_service_account_info(
            credentials_info, scopes=SCOPES)
    except Exception as e:
        logger.error(f"Error al obtener credenciales: {e}")
        return None

def get_sheets_service():
    """Crear servicio de Google Sheets"""
    credentials = get_credentials()
    if not credentials:
        logger.error("No se pudo obtener credenciales para Google Sheets")
        return None
        
    try:
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Error al crear servicio de Google Sheets: {e}")
        return None

def read_sheet_data(sheet_name):
    """
    Lee datos de una hoja específica de Google Sheets
    
    Args:
        sheet_name (str): Nombre de la hoja a leer ('compras', 'ventas', etc.)
        
    Returns:
        pandas.DataFrame: DataFrame con los datos de la hoja
    """
    service = get_sheets_service()
    if not service:
        logger.error("No se pudo obtener servicio de Google Sheets")
        return pd.DataFrame()
        
    spreadsheet_id = config.SPREADSHEET_ID
    if not spreadsheet_id:
        logger.error("SPREADSHEET_ID no está configurado")
        return pd.DataFrame()
    
    # Obtener el nombre real de la hoja
    real_sheet_name = SHEET_NAMES.get(sheet_name.lower(), sheet_name)
    
    try:
        # Primero leer el rango para determinar cuántas filas hay
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{real_sheet_name}!A:A"
        ).execute()
        
        values = result.get('values', [])
        if not values:
            logger.warning(f"No hay datos en la hoja {real_sheet_name}")
            return pd.DataFrame()
            
        # Ahora leer todas las columnas para esas filas
        num_rows = len(values)
        range_name = f"{real_sheet_name}!A1:Z{num_rows}"
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueRenderOption='UNFORMATTED_VALUE'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            logger.warning(f"No hay datos en {range_name}")
            return pd.DataFrame()
            
        # Convertir a DataFrame
        headers = values[0]
        data = values[1:] if len(values) > 1 else []
        
        # Asegurarse de que todas las filas tengan la misma longitud
        data = [row + [''] * (len(headers) - len(row)) for row in data]
        
        df = pd.DataFrame(data, columns=headers)
        logger.info(f"Leídos {len(df)} registros de {real_sheet_name}")
        return df
        
    except Exception as e:
        logger.error(f"Error al leer datos de {real_sheet_name}: {e}")
        return pd.DataFrame()

def get_compras_data():
    """Obtiene datos de compras"""
    return read_sheet_data('compras')

def get_ventas_data():
    """Obtiene datos de ventas"""
    return read_sheet_data('ventas')

def get_gastos_data():
    """Obtiene datos de gastos"""
    return read_sheet_data('gastos')

def get_proceso_data():
    """Obtiene datos de proceso"""
    return read_sheet_data('proceso')

def get_almacen_data():
    """Obtiene datos de almacen"""
    return read_sheet_data('almacen')

def filter_by_date_range(df, fecha_col='fecha', start_date=None, end_date=None, timezone='America/Lima'):
    """
    Filtra un DataFrame por rango de fechas
    
    Args:
        df (pandas.DataFrame): DataFrame a filtrar
        fecha_col (str): Nombre de la columna de fecha
        start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'
        end_date (str): Fecha de fin en formato 'YYYY-MM-DD'
        timezone (str): Zona horaria para las fechas
        
    Returns:
        pandas.DataFrame: DataFrame filtrado
    """
    if fecha_col not in df.columns:
        logger.warning(f"Columna {fecha_col} no encontrada en el DataFrame")
        return df
    
    # Convertir columna de fecha a datetime si no lo es
    try:
        df[fecha_col] = pd.to_datetime(df[fecha_col], errors='coerce')
    except Exception as e:
        logger.error(f"Error al convertir fechas: {e}")
        return df
    
    # Filtrar por rango de fechas
    if start_date:
        try:
            start_date = pd.to_datetime(start_date)
            tz = pytz.timezone(timezone)
            start_date = start_date.replace(tzinfo=tz)
            df = df[df[fecha_col] >= start_date]
        except Exception as e:
            logger.error(f"Error al filtrar por fecha de inicio: {e}")
    
    if end_date:
        try:
            end_date = pd.to_datetime(end_date)
            tz = pytz.timezone(timezone)
            end_date = end_date.replace(hour=23, minute=59, second=59, tzinfo=tz)
            df = df[df[fecha_col] <= end_date]
        except Exception as e:
            logger.error(f"Error al filtrar por fecha de fin: {e}")
            
    return df

def calculate_compras_summary(start_date=None, end_date=None):
    """
    Calcula resumen de compras, separando las que tienen notas de adelantos de las que no
    
    Args:
        start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'
        end_date (str): Fecha de fin en formato 'YYYY-MM-DD'
        
    Returns:
        dict: Resumen de compras con totales separados
    """
    try:
        # Obtener datos de compras
        compras_df = get_compras_data()
        
        # Filtrar por fecha si es necesario
        if start_date or end_date:
            compras_df = filter_by_date_range(compras_df, 'fecha', start_date, end_date)
            
        # Convertir tipos de datos para cálculos
        for col in compras_df.columns:
            if col.lower() in ['cantidad', 'precio', 'total', 'preciototal']:
                compras_df[col] = pd.to_numeric(compras_df[col], errors='coerce').fillna(0)
        
        # Verificar si existe la columna 'notas'
        nota_col = None
        for col_name in compras_df.columns:
            if col_name.lower() in ['notas', 'nota', 'observacion', 'observaciones']:
                nota_col = col_name
                break
        
        total_col = None
        for col_name in compras_df.columns:
            if col_name.lower() in ['total', 'preciototal']:
                total_col = col_name
                break
                
        if nota_col is None or total_col is None:
            logger.warning("No se encontró columna de notas o total en la hoja de compras")
            return {
                'total_compras': float(compras_df[total_col].sum() if total_col else 0),
                'compras_sin_adelantos': float(compras_df[total_col].sum() if total_col else 0),
                'compras_con_adelantos': 0.0
            }
        
        # Separar compras con y sin adelantos - buscar específicamente texto que contenga "Compra con adelanto"
        compras_df['es_adelanto'] = compras_df[nota_col].astype(str).str.contains('Compra con adelanto', case=False, na=False)
        
        # Calcular totales
        compras_con_adelantos = compras_df[compras_df['es_adelanto']][total_col].sum()
        compras_sin_adelantos = compras_df[~compras_df['es_adelanto']][total_col].sum()
        total_compras = compras_con_adelantos + compras_sin_adelantos
        
        # Imprimir para depuración
        logger.info(f"Total compras: {total_compras}")
        logger.info(f"Compras con adelantos: {compras_con_adelantos}")
        logger.info(f"Compras sin adelantos: {compras_sin_adelantos}")
        
        return {
            'total_compras': float(total_compras),
            'compras_sin_adelantos': float(compras_sin_adelantos),
            'compras_con_adelantos': float(compras_con_adelantos)
        }
    except Exception as e:
        logger.error(f"Error al calcular resumen de compras: {e}")
        return {
            'total_compras': 0.0,
            'compras_sin_adelantos': 0.0,
            'compras_con_adelantos': 0.0,
            'error': str(e)
        }

def get_detailed_profit_by_process(start_date=None, end_date=None):
    """
    Calcula la ganancia real de forma detallada por cada proceso individual
    
    Args:
        start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'
        end_date (str): Fecha de fin en formato 'YYYY-MM-DD'
        
    Returns:
        dict: Detalles de ganancias por cada proceso
    """
    try:
        # Obtener datos de todas las hojas necesarias
        logger.debug(f"Obteniendo datos para periodo: {start_date} a {end_date}")
        compras_df = get_compras_data()
        proceso_df = get_proceso_data()
        almacen_df = get_almacen_data()
        ventas_df = get_ventas_data()
        
        # Información de diagnóstico: tamaños de los DataFrames
        logger.debug(f"Tamaño de compras_df: {len(compras_df)} filas")
        logger.debug(f"Tamaño de proceso_df: {len(proceso_df)} filas")
        logger.debug(f"Tamaño de almacen_df: {len(almacen_df)} filas")
        logger.debug(f"Tamaño de ventas_df: {len(ventas_df)} filas")
        
        # Mostrar columnas disponibles en cada DataFrame
        logger.debug(f"Columnas de compras_df: {list(compras_df.columns)}")
        logger.debug(f"Columnas de proceso_df: {list(proceso_df.columns)}")
        logger.debug(f"Columnas de almacen_df: {list(almacen_df.columns)}")
        logger.debug(f"Columnas de ventas_df: {list(ventas_df.columns)}")
        
        # Filtrar por fecha si es necesario
        if start_date or end_date:
            logger.debug(f"Filtrando datos por rango de fechas: {start_date} a {end_date}")
            proceso_df = filter_by_date_range(proceso_df, 'fecha', start_date, end_date)
            logger.debug(f"Después del filtrado: {len(proceso_df)} procesos")
            
        # Información de diagnóstico: ¿hay datos después del filtrado?
        if proceso_df.empty:
            logger.warning("No hay datos de proceso para el rango de fechas seleccionado")
            return {
                'procesos': [],
                'resumen': {
                    'total_procesos': 0,
                    'total_costo': 0.0,
                    'total_ingresos': 0.0,
                    'total_ganancia': 0.0
                },
                'debug_info': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'compras_count': len(compras_df),
                    'proceso_count': len(proceso_df),
                    'almacen_count': len(almacen_df),
                    'ventas_count': len(ventas_df)
                }
            }
            
        # Convertir tipos de datos para cálculos
        for df in [compras_df, proceso_df, almacen_df, ventas_df]:
            for col in df.columns:
                if col.lower() in ['cantidad', 'precio', 'total', 'preciototal', 'precio_kg']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Identificar columnas relevantes en cada DataFrame usando una función auxiliar más clara
        def find_column(df, possible_names):
            for name in possible_names:
                for col in df.columns:
                    if name.lower() in col.lower():
                        logger.debug(f"Columna encontrada: {col} para patrón {name}")
                        return col
            logger.warning(f"No se encontró columna que coincida con {possible_names}")
            return None
        
        # Buscar columnas de ID
        proceso_id_col = find_column(proceso_df, ['id', 'codigo', 'proceso_id'])
        compras_id_col = find_column(compras_df, ['id', 'codigo', 'compra_id'])
        compras_total_col = find_column(compras_df, ['total', 'preciototal'])
        proceso_compras_id_col = find_column(proceso_df, ['compras_id', 'id_compra'])
        almacen_id_col = find_column(almacen_df, ['id', 'codigo', 'almacen_id'])
        almacen_proceso_id_col = find_column(almacen_df, ['proceso_id', 'id_proceso'])
        ventas_almacen_id_col = find_column(ventas_df, ['almacen_id', 'id_almacen'])
        ventas_total_col = find_column(ventas_df, ['total', 'precio_total'])
        
        # Verificar columnas identificadas
        required_cols = {
            'proceso_id_col': proceso_id_col,
            'compras_id_col': compras_id_col, 
            'compras_total_col': compras_total_col,
            'proceso_compras_id_col': proceso_compras_id_col,
            'almacen_proceso_id_col': almacen_proceso_id_col,
            'ventas_almacen_id_col': ventas_almacen_id_col,
            'ventas_total_col': ventas_total_col,
            'almacen_id_col': almacen_id_col
        }
        
        missing_cols = [k for k, v in required_cols.items() if v is None]
        if missing_cols:
            logger.warning(f"No se encontraron todas las columnas necesarias: {missing_cols}")
            # Retornar información de depuración
            return {
                'procesos': [],
                'resumen': {
                    'total_procesos': 0,
                    'total_costo': 0.0,
                    'total_ingresos': 0.0,
                    'total_ganancia': 0.0
                },
                'debug_info': {
                    'missing_columns': missing_cols,
                    'available_columns': {
                        'proceso': list(proceso_df.columns),
                        'compras': list(compras_df.columns),
                        'almacen': list(almacen_df.columns),
                        'ventas': list(ventas_df.columns)
                    }
                }
            }
        
        # Resultados detallados por proceso
        detailed_results = []
        
        # Para cada proceso en el rango de fechas
        for index, proceso_row in proceso_df.iterrows():
            logger.debug(f"Procesando proceso #{index}")
            
            if proceso_id_col is None or proceso_id_col not in proceso_df.columns:
                continue
                
            proceso_id = str(proceso_row[proceso_id_col]).strip() if pd.notna(proceso_row[proceso_id_col]) else ''
            if not proceso_id:
                logger.debug(f"Proceso #{index} no tiene ID válido")
                continue
            
            logger.debug(f"Procesando proceso con ID: {proceso_id}")
                
            # Obtener fecha del proceso
            fecha_proceso = proceso_row['fecha'] if 'fecha' in proceso_df.columns and pd.notna(proceso_row['fecha']) else None
            
            # 1. Encontrar la compra asociada al proceso
            compra_id = str(proceso_row[proceso_compras_id_col]).strip() if pd.notna(proceso_row[proceso_compras_id_col]) else ''
            logger.debug(f"Proceso {proceso_id} asociado a compra ID: {compra_id}")
            
            # Datos básicos del proceso
            proceso_info = {
                'proceso_id': proceso_id,
                'fecha_proceso': fecha_proceso.strftime('%Y-%m-%d') if isinstance(fecha_proceso, (datetime, pd.Timestamp)) else None,
                'compra_id': compra_id,
                'tipo_cafe': proceso_row['tipo_cafe'] if 'tipo_cafe' in proceso_df.columns else 'Desconocido',
                'cantidad_entrada': float(proceso_row['cantidad']) if 'cantidad' in proceso_df.columns else 0.0,
                'costo_compra': 0.0,
                'ingresos_ventas': 0.0,
                'ganancia': 0.0,
                'ventas': [],
                'detalles': {}
            }
            
            # 2. Obtener costo de la compra asociada
            if compra_id:
                compra_matches = compras_df[compras_df[compras_id_col].astype(str).str.strip() == compra_id]
                logger.debug(f"Encontradas {len(compra_matches)} compras con ID {compra_id}")
                
                if not compra_matches.empty:
                    compra_row = compra_matches.iloc[0]
                    costo_compra = float(compra_row[compras_total_col]) if compras_total_col in compras_df.columns else 0.0
                    proceso_info['costo_compra'] = costo_compra
                    logger.debug(f"Costo de compra para proceso {proceso_id}: {costo_compra}")
                    
                    # Añadir detalles de la compra
                    proceso_info['detalles']['compra'] = {
                        'fecha': compra_row['fecha'].strftime('%Y-%m-%d') if isinstance(compra_row.get('fecha'), (datetime, pd.Timestamp)) else None,
                        'tipo_cafe': compra_row.get('tipo_cafe', 'Desconocido'),
                        'cantidad': float(compra_row.get('cantidad', 0)),
                        'precio_kg': float(compra_row.get('precio', 0)),
                        'total': costo_compra
                    }
            
            # 3. Encontrar registros de almacén asociados a este proceso
            almacen_asociado = []
            if almacen_proceso_id_col:
                almacen_matches = almacen_df[almacen_df[almacen_proceso_id_col].astype(str).str.strip() == proceso_id]
                logger.debug(f"Encontrados {len(almacen_matches)} registros de almacén para proceso {proceso_id}")
                
                for _, almacen_row in almacen_matches.iterrows():
                    almacen_id = str(almacen_row[almacen_id_col]).strip() if pd.notna(almacen_row.get(almacen_id_col)) else ''
                    almacen_asociado.append({
                        'almacen_id': almacen_id,
                        'fecha': almacen_row['fecha'].strftime('%Y-%m-%d') if isinstance(almacen_row.get('fecha'), (datetime, pd.Timestamp)) else None,
                        'tipo_cafe': almacen_row.get('tipo_cafe', 'Desconocido'),
                        'cantidad': float(almacen_row.get('cantidad', 0))
                    })
            
            proceso_info['detalles']['almacen'] = almacen_asociado
            
            # 4. Encontrar ventas asociadas a los registros de almacén
            for almacen_item in almacen_asociado:
                almacen_id = almacen_item['almacen_id']
                ventas_matches = ventas_df[ventas_df[ventas_almacen_id_col].astype(str).str.strip() == almacen_id]
                logger.debug(f"Encontradas {len(ventas_matches)} ventas para almacén {almacen_id}")
                
                for _, venta_row in ventas_matches.iterrows():
                    venta_total = float(venta_row[ventas_total_col]) if ventas_total_col in ventas_df.columns else 0.0
                    proceso_info['ingresos_ventas'] += venta_total
                    
                    venta_info = {
                        'fecha': venta_row['fecha'].strftime('%Y-%m-%d') if isinstance(venta_row.get('fecha'), (datetime, pd.Timestamp)) else None,
                        'cliente': venta_row.get('cliente', 'Desconocido'),
                        'tipo_cafe': venta_row.get('tipo_cafe', 'Desconocido'),
                        'cantidad': float(venta_row.get('cantidad', 0)),
                        'precio_kg': float(venta_row.get('precio', 0)),
                        'total': venta_total
                    }
                    
                    proceso_info['ventas'].append(venta_info)
            
            # 5. Calcular ganancia para este proceso
            proceso_info['ganancia'] = proceso_info['ingresos_ventas'] - proceso_info['costo_compra']
            logger.debug(f"Ganancia calculada para proceso {proceso_id}: {proceso_info['ganancia']}")
            
            # Añadir al resultado
            detailed_results.append(proceso_info)
        
        # Información de diagnóstico final
        logger.info(f"Total de procesos encontrados: {len(detailed_results)}")
        
        # Calcular totales generales
        total_costo = sum(p['costo_compra'] for p in detailed_results)
        total_ingresos = sum(p['ingresos_ventas'] for p in detailed_results)
        total_ganancia = sum(p['ganancia'] for p in detailed_results)
        
        logger.info(f"Total costos: {total_costo}")
        logger.info(f"Total ingresos: {total_ingresos}")
        logger.info(f"Total ganancia: {total_ganancia}")
        
        # Devolver resultado con información de depuración
        return {
            'procesos': detailed_results,
            'resumen': {
                'total_procesos': len(detailed_results),
                'total_costo': float(total_costo),
                'total_ingresos': float(total_ingresos),
                'total_ganancia': float(total_ganancia)
            },
            'debug_info': {
                'start_date': start_date,
                'end_date': end_date,
                'compras_count': len(compras_df),
                'proceso_count': len(proceso_df),
                'filtered_proceso_count': len(proceso_df) if start_date is None and end_date is None else None,
                'almacen_count': len(almacen_df),
                'ventas_count': len(ventas_df),
                'identified_columns': required_cols
            }
        }
    except Exception as e:
        logger.error(f"Error al calcular ganancia detallada por proceso: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'procesos': [],
            'resumen': {
                'total_procesos': 0,
                'total_costo': 0.0,
                'total_ingresos': 0.0,
                'total_ganancia': 0.0
            },
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def calculate_profit_by_process(start_date=None, end_date=None):
    """
    Calcula la ganancia real basada en el proceso de transformación de café
    
    Args:
        start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'
        end_date (str): Fecha de fin en formato 'YYYY-MM-DD'
        
    Returns:
        dict: Resumen de ganancias por proceso
    """
    try:
        # Obtener datos de todas las hojas necesarias
        compras_df = get_compras_data()
        proceso_df = get_proceso_data()
        almacen_df = get_almacen_data()
        ventas_df = get_ventas_data()
        
        # Filtrar por fecha si es necesario
        if start_date or end_date:
            compras_df = filter_by_date_range(compras_df, 'fecha', start_date, end_date)
            proceso_df = filter_by_date_range(proceso_df, 'fecha', start_date, end_date)
            almacen_df = filter_by_date_range(almacen_df, 'fecha', start_date, end_date)
            ventas_df = filter_by_date_range(ventas_df, 'fecha', start_date, end_date)
            
        # Convertir tipos de datos para cálculos
        for df in [compras_df, proceso_df, almacen_df, ventas_df]:
            for col in df.columns:
                if col.lower() in ['cantidad', 'precio', 'total', 'preciototal', 'precio_kg']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Identificar columnas relevantes en cada DataFrame
        compras_id_col = None
        for col in compras_df.columns:
            if col.lower() in ['id', 'codigo', 'compra_id']:
                compras_id_col = col
                break
                
        compras_total_col = None
        for col in compras_df.columns:
            if col.lower() in ['total', 'preciototal']:
                compras_total_col = col
                break
                
        proceso_compras_id_col = None
        for col in proceso_df.columns:
            if 'compras_' in col.lower() and 'id' in col.lower():
                proceso_compras_id_col = col
                break
                
        almacen_id_col = None
        for col in almacen_df.columns:
            if col.lower() in ['id', 'codigo', 'almacen_id']:
                almacen_id_col = col
                break
                
        ventas_almacen_id_col = None
        for col in ventas_df.columns:
            if 'almacen' in col.lower() and 'id' in col.lower():
                ventas_almacen_id_col = col
                break
                
        ventas_total_col = None
        for col in ventas_df.columns:
            if col.lower() in ['total', 'precio_total']:
                ventas_total_col = col
                break
                
        # Verificar que se encontraron todas las columnas necesarias
        if (compras_id_col is None or compras_total_col is None or 
            proceso_compras_id_col is None or almacen_id_col is None or 
            ventas_almacen_id_col is None or ventas_total_col is None):
            logger.warning("No se encontraron todas las columnas necesarias para calcular ganancias por proceso")
            logger.warning(f"compras_id_col: {compras_id_col}")
            logger.warning(f"compras_total_col: {compras_total_col}")
            logger.warning(f"proceso_compras_id_col: {proceso_compras_id_col}")
            logger.warning(f"almacen_id_col: {almacen_id_col}")
            logger.warning(f"ventas_almacen_id_col: {ventas_almacen_id_col}")
            logger.warning(f"ventas_total_col: {ventas_total_col}")
            return {
                'costo_compras': 0.0,
                'ingresos_ventas': 0.0,
                'ganancia_real': 0.0
            }
        
        # Calcular costo total de compras que han sido procesadas
        costo_compras_procesadas = 0.0
        ingresos_ventas_procesadas = 0.0
        
        # Mapear compras a procesos
        compras_procesadas = {}
        if not proceso_df.empty and proceso_compras_id_col in proceso_df.columns:
            for _, row in proceso_df.iterrows():
                compra_id = row[proceso_compras_id_col]
                if pd.notna(compra_id) and compra_id != '':
                    # Limpiar el ID (a veces viene con espacios o caracteres adicionales)
                    compra_id = str(compra_id).strip()
                    compras_procesadas[compra_id] = True
        
        # Sumar el costo de las compras procesadas
        if not compras_df.empty and compras_id_col in compras_df.columns and compras_total_col in compras_df.columns:
            for _, row in compras_df.iterrows():
                compra_id = str(row[compras_id_col]).strip() if pd.notna(row[compras_id_col]) else ''
                if compra_id in compras_procesadas:
                    costo_compras_procesadas += float(row[compras_total_col])
        
        # Mapear almacén a ventas
        almacen_vendido = {}
        if not ventas_df.empty and ventas_almacen_id_col in ventas_df.columns:
            for _, row in ventas_df.iterrows():
                almacen_id = row[ventas_almacen_id_col]
                if pd.notna(almacen_id) and almacen_id != '':
                    # Limpiar el ID
                    almacen_id = str(almacen_id).strip()
                    if ventas_total_col in ventas_df.columns:
                        almacen_vendido[almacen_id] = float(row[ventas_total_col])
                        ingresos_ventas_procesadas += float(row[ventas_total_col])
        
        # Calcular ganancia real
        ganancia_real = ingresos_ventas_procesadas - costo_compras_procesadas
        
        logger.info(f"Costo total de compras procesadas: {costo_compras_procesadas}")
        logger.info(f"Ingresos por ventas de café procesado: {ingresos_ventas_procesadas}")
        logger.info(f"Ganancia real: {ganancia_real}")
        
        return {
            'costo_compras': float(costo_compras_procesadas),
            'ingresos_ventas': float(ingresos_ventas_procesadas),
            'ganancia_real': float(ganancia_real)
        }
    except Exception as e:
        logger.error(f"Error al calcular ganancia por proceso: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'costo_compras': 0.0,
            'ingresos_ventas': 0.0,
            'ganancia_real': 0.0,
            'error': str(e)
        }

def calculate_daily_summary(start_date=None, end_date=None):
    """
    Calcula un resumen diario de operaciones
    
    Args:
        start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'
        end_date (str): Fecha de fin en formato 'YYYY-MM-DD'
        
    Returns:
        dict: Resumen diario con estadísticas
    """
    try:
        # Obtener datos
        compras_df = get_compras_data()
        ventas_df = get_ventas_data()
        gastos_df = get_gastos_data()
        
        # Obtener también datos del proceso (que contiene compras con adelantos)
        proceso_df = get_proceso_data()
        
        # Filtrar por fecha si es necesario
        if start_date or end_date:
            compras_df = filter_by_date_range(compras_df, 'fecha', start_date, end_date)
            ventas_df = filter_by_date_range(ventas_df, 'fecha', start_date, end_date)
            gastos_df = filter_by_date_range(gastos_df, 'fecha', start_date, end_date)
            proceso_df = filter_by_date_range(proceso_df, 'fecha', start_date, end_date)
            
        # Convertir tipos de datos para cálculos
        for df in [compras_df, ventas_df, gastos_df, proceso_df]:
            for col in df.columns:
                if col.lower() in ['cantidad', 'precio', 'total', 'monto', 'preciototal']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Calcular estadísticas
        kg_comprados = compras_df['cantidad'].sum() if 'cantidad' in compras_df.columns else 0
        kg_vendidos = ventas_df['cantidad'].sum() if 'cantidad' in ventas_df.columns else 0
        ingresos = ventas_df['total'].sum() if 'total' in ventas_df.columns else 0
        
        # Análisis de gastos
        gastos_total = gastos_df['monto'].sum() if 'monto' in gastos_df.columns else 0
        
        # Análisis de métodos de pago (basado en descripción)
        if 'descripcion' in gastos_df.columns:
            gastos_efectivo = gastos_df[gastos_df['descripcion'].astype(str).str.upper().str.contains('EFECTIVO', na=False)]['monto'].sum()
            gastos_transferencia = gastos_df[gastos_df['descripcion'].astype(str).str.upper().str.contains('TRANSFERENCIA', na=False)]['monto'].sum()
        else:
            gastos_efectivo = 0
            gastos_transferencia = 0
            
        # Calcular resumen de compras (con y sin adelantos) usando los datos de proceso
        # En proceso, las compras con adelantos tienen una nota que comienza con "Compra con adelanto"
        nota_col = None
        for col_name in proceso_df.columns:
            if col_name.lower() in ['notas', 'nota', 'observacion', 'observaciones']:
                nota_col = col_name
                break
                
        total_col = None
        for col_name in proceso_df.columns:
            if col_name.lower() in ['total', 'preciototal']:
                total_col = col_name
                break
                
        compras_con_adelantos = 0
        compras_sin_adelantos = 0
                
        if nota_col is not None and total_col is not None:
            proceso_df['es_adelanto'] = proceso_df[nota_col].astype(str).str.contains('Compra con adelanto', case=False, na=False)
            compras_con_adelantos = proceso_df[proceso_df['es_adelanto']][total_col].sum()
            compras_sin_adelantos = proceso_df[~proceso_df['es_adelanto']][total_col].sum()
        else:
            # Si no se encuentran las columnas en proceso, usar la función calculate_compras_summary
            compras_summary = calculate_compras_summary(start_date, end_date)
            compras_con_adelantos = compras_summary['compras_con_adelantos']
            compras_sin_adelantos = compras_summary['compras_sin_adelantos']
        
        # Calcular ganancia real basada en procesos
        profit_summary = calculate_profit_by_process(start_date, end_date)
            
        # Construir resumen
        summary = {
            'periodo': {
                'inicio': start_date or 'Todos los datos',
                'fin': end_date or 'Hasta la fecha actual',
            },
            'inventario': {
                'kg_comprados': float(kg_comprados),
                'kg_vendidos': float(kg_vendidos),
                'kg_disponibles': float(kg_comprados - kg_vendidos)
            },
            'financiero': {
                'ingresos': float(ingresos),
                'gastos': float(gastos_total),
                'ganancia': float(ingresos - gastos_total),
                'ganancia_real': float(profit_summary['ganancia_real'])
            },
            'compras': {
                'total': float(compras_con_adelantos + compras_sin_adelantos),
                'sin_adelantos': float(compras_sin_adelantos),
                'con_adelantos': float(compras_con_adelantos)
            },
            'metodos_pago': {
                'efectivo': float(gastos_efectivo),
                'transferencia': float(gastos_transferencia),
                'otro': float(gastos_total - gastos_efectivo - gastos_transferencia)
            },
            'operaciones': {
                'compras': len(compras_df),
                'ventas': len(ventas_df),
                'gastos': len(gastos_df)
            }
        }
        
        return summary
    except Exception as e:
        logger.error(f"Error al calcular resumen diario: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'error': str(e),
            'periodo': {
                'inicio': start_date or 'Todos los datos',
                'fin': end_date or 'Hasta la fecha actual',
            }
        }

def get_daily_summaries(start_date=None, end_date=None):
    """
    Obtiene resúmenes diarios para un rango de fechas
    
    Args:
        start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'
        end_date (str): Fecha de fin en formato 'YYYY-MM-DD'
        
    Returns:
        list: Lista de resúmenes diarios
    """
    try:
        # Obtener datos
        compras_df = get_compras_data()
        ventas_df = get_ventas_data()
        gastos_df = get_gastos_data()
        proceso_df = get_proceso_data()
        almacen_df = get_almacen_data()
        
        # Convertir columnas de fecha a datetime
        for df in [compras_df, ventas_df, gastos_df, proceso_df, almacen_df]:
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        
        # Filtrar por fecha si es necesario
        if start_date or end_date:
            compras_df = filter_by_date_range(compras_df, 'fecha', start_date, end_date)
            ventas_df = filter_by_date_range(ventas_df, 'fecha', start_date, end_date)
            gastos_df = filter_by_date_range(gastos_df, 'fecha', start_date, end_date)
            proceso_df = filter_by_date_range(proceso_df, 'fecha', start_date, end_date)
            almacen_df = filter_by_date_range(almacen_df, 'fecha', start_date, end_date)
            
        # Convertir tipos de datos para cálculos
        for df in [compras_df, ventas_df, gastos_df, proceso_df, almacen_df]:
            for col in df.columns:
                if col.lower() in ['cantidad', 'precio', 'total', 'monto', 'preciototal']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Obtener todas las fechas únicas
        all_dates = pd.DataFrame()
        for df in [compras_df, ventas_df, gastos_df, proceso_df, almacen_df]:
            if 'fecha' in df.columns and not df.empty:
                all_dates = pd.concat([all_dates, df[['fecha']]])
        
        if all_dates.empty:
            return []
            
        # Extraer solo la fecha (sin hora)
        all_dates['fecha_solo'] = all_dates['fecha'].dt.date
        unique_dates = sorted(all_dates['fecha_solo'].unique())
        
        # Preparar columnas para proceso
        nota_col_proceso = None
        for col_name in proceso_df.columns:
            if col_name.lower() in ['notas', 'nota', 'observacion', 'observaciones']:
                nota_col_proceso = col_name
                break
                
        total_col_proceso = None
        for col_name in proceso_df.columns:
            if col_name.lower() in ['total', 'preciototal']:
                total_col_proceso = col_name
                break
                
        if nota_col_proceso is not None and total_col_proceso is not None:
            proceso_df['es_adelanto'] = proceso_df[nota_col_proceso].astype(str).str.contains('Compra con adelanto', case=False, na=False)
        
        daily_summaries = []
        
        for date in unique_dates:
            str_date = date.strftime('%Y-%m-%d')
            
            # Filtrar por día específico
            day_compras = compras_df[compras_df['fecha'].dt.date == date] if 'fecha' in compras_df.columns else pd.DataFrame()
            day_ventas = ventas_df[ventas_df['fecha'].dt.date == date] if 'fecha' in ventas_df.columns else pd.DataFrame()
            day_gastos = gastos_df[gastos_df['fecha'].dt.date == date] if 'fecha' in gastos_df.columns else pd.DataFrame()
            day_proceso = proceso_df[proceso_df['fecha'].dt.date == date] if 'fecha' in proceso_df.columns else pd.DataFrame()
            day_almacen = almacen_df[almacen_df['fecha'].dt.date == date] if 'fecha' in almacen_df.columns else pd.DataFrame()
            
            # Calcular estadísticas del día
            kg_comprados = day_compras['cantidad'].sum() if 'cantidad' in day_compras.columns else 0
            kg_vendidos = day_ventas['cantidad'].sum() if 'cantidad' in day_ventas.columns else 0
            ingresos = day_ventas['total'].sum() if 'total' in day_ventas.columns else 0
            gastos_total = day_gastos['monto'].sum() if 'monto' in day_gastos.columns else 0
            
            # Análisis de métodos de pago (basado en descripción)
            if 'descripcion' in day_gastos.columns and not day_gastos.empty:
                gastos_efectivo = day_gastos[day_gastos['descripcion'].astype(str).str.upper().str.contains('EFECTIVO', na=False)]['monto'].sum()
                gastos_transferencia = day_gastos[day_gastos['descripcion'].astype(str).str.upper().str.contains('TRANSFERENCIA', na=False)]['monto'].sum()
            else:
                gastos_efectivo = 0
                gastos_transferencia = 0
                
            # Calcular compras con y sin adelantos para el día desde hoja de proceso
            compras_con_adelantos = 0
            compras_sin_adelantos = 0
            
            if nota_col_proceso is not None and total_col_proceso is not None and not day_proceso.empty:
                compras_con_adelantos = day_proceso[day_proceso['es_adelanto']][total_col_proceso].sum()
                compras_sin_adelantos = day_proceso[~day_proceso['es_adelanto']][total_col_proceso].sum()
                
            # Calcular ganancia real basada en procesos para el día
            # Esto es una simplificación, ya que el proceso real puede involucrar días múltiples
            ganancia_real = 0
            
            # Construir resumen del día
            day_summary = {
                'fecha': str_date,
                'inventario': {
                    'kg_comprados': float(kg_comprados),
                    'kg_vendidos': float(kg_vendidos)
                },
                'financiero': {
                    'ingresos': float(ingresos),
                    'gastos': float(gastos_total),
                    'ganancia': float(ingresos - gastos_total),
                    'ganancia_real': float(ganancia_real)
                },
                'compras': {
                    'total': float(compras_con_adelantos + compras_sin_adelantos),
                    'sin_adelantos': float(compras_sin_adelantos),
                    'con_adelantos': float(compras_con_adelantos)
                },
                'metodos_pago': {
                    'efectivo': float(gastos_efectivo),
                    'transferencia': float(gastos_transferencia),
                    'otro': float(gastos_total - gastos_efectivo - gastos_transferencia)
                },
                'operaciones': {
                    'compras': len(day_compras),
                    'ventas': len(day_ventas),
                    'gastos': len(day_gastos)
                }
            }
            
            daily_summaries.append(day_summary)
            
        return daily_summaries
    except Exception as e:
        logger.error(f"Error al obtener resúmenes diarios: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def get_coffee_types_summary():
    """
    Obtiene un resumen de los tipos de café
    
    Returns:
        dict: Resumen de tipos de café con cantidades y estadísticas
    """
    try:
        compras_df = get_compras_data()
        
        if 'tipo_cafe' not in compras_df.columns:
            logger.warning("Columna tipo_cafe no encontrada en compras")
            return {}
            
        # Asegurar que la columna cantidad sea numérica
        compras_df['cantidad'] = pd.to_numeric(compras_df['cantidad'], errors='coerce').fillna(0)
        
        # Agrupar por tipo de café
        tipos_cafe = compras_df.groupby('tipo_cafe').agg({
            'cantidad': 'sum',
            'tipo_cafe': 'count'
        }).rename(columns={'tipo_cafe': 'operaciones'})
        
        # Convertir a diccionario
        result = {}
        for tipo, row in tipos_cafe.iterrows():
            result[tipo] = {
                'kg_total': float(row['cantidad']),
                'operaciones': int(row['operaciones'])
            }
            
        return result
    except Exception as e:
        logger.error(f"Error al obtener resumen de tipos de café: {e}")
        return {}
