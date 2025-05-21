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

# Configurar logging
logging.basicConfig(level=logging.INFO)
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
        
        # Filtrar por fecha si es necesario
        if start_date or end_date:
            compras_df = filter_by_date_range(compras_df, 'fecha', start_date, end_date)
            ventas_df = filter_by_date_range(ventas_df, 'fecha', start_date, end_date)
            gastos_df = filter_by_date_range(gastos_df, 'fecha', start_date, end_date)
            
        # Convertir tipos de datos para cálculos
        for df in [compras_df, ventas_df, gastos_df]:
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
                'ganancia': float(ingresos - gastos_total)
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
        
        # Convertir columnas de fecha a datetime
        for df in [compras_df, ventas_df, gastos_df]:
            if 'fecha' in df.columns:
                df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        
        # Filtrar por fecha si es necesario
        if start_date or end_date:
            compras_df = filter_by_date_range(compras_df, 'fecha', start_date, end_date)
            ventas_df = filter_by_date_range(ventas_df, 'fecha', start_date, end_date)
            gastos_df = filter_by_date_range(gastos_df, 'fecha', start_date, end_date)
            
        # Convertir tipos de datos para cálculos
        for df in [compras_df, ventas_df, gastos_df]:
            for col in df.columns:
                if col.lower() in ['cantidad', 'precio', 'total', 'monto', 'preciototal']:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Obtener todas las fechas únicas
        all_dates = pd.DataFrame()
        for df in [compras_df, ventas_df, gastos_df]:
            if 'fecha' in df.columns and not df.empty:
                all_dates = pd.concat([all_dates, df[['fecha']]])
        
        if all_dates.empty:
            return []
            
        # Extraer solo la fecha (sin hora)
        all_dates['fecha_solo'] = all_dates['fecha'].dt.date
        unique_dates = sorted(all_dates['fecha_solo'].unique())
        
        daily_summaries = []
        
        for date in unique_dates:
            str_date = date.strftime('%Y-%m-%d')
            
            # Filtrar por día específico
            day_compras = compras_df[compras_df['fecha'].dt.date == date] if 'fecha' in compras_df.columns else pd.DataFrame()
            day_ventas = ventas_df[ventas_df['fecha'].dt.date == date] if 'fecha' in ventas_df.columns else pd.DataFrame()
            day_gastos = gastos_df[gastos_df['fecha'].dt.date == date] if 'fecha' in gastos_df.columns else pd.DataFrame()
            
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
                    'ganancia': float(ingresos - gastos_total)
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
