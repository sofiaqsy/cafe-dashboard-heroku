# Café Dashboard

Dashboard web para reportes financieros e inventario del sistema de gestión de café.

## 📊 Características

- **Visualización de datos financieros**: Gráficos interactivos de ventas, compras y ganancias
- **Control de inventario**: Seguimiento visual del stock de café por tipo y fase
- **Análisis de métodos de pago**: Distribución de transacciones (efectivo vs transferencia)
- **Reportes personalizados**: Filtros por fecha, tipo de café y categoría
- **Exportación de datos**: Descarga de reportes en formatos Excel y PDF

## 🔧 Tecnologías

- **Frontend**: React, Recharts, Tailwind CSS
- **Backend**: Python con Flask
- **Datos**: Integración directa con Google Sheets
- **Despliegue**: Configurado para Heroku

## 📋 Estructura del Proyecto

```
cafe-dashboard-heroku/
├── README.md                 # Documentación principal
├── requirements.txt          # Dependencias de Python
├── runtime.txt               # Versión de Python para Heroku
├── Procfile                  # Configuración para Heroku
├── .gitignore                # Archivos ignorados por git
├── client/                   # Frontend React
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
└── server/                   # Backend Python
    ├── app.py                # Aplicación Flask
    ├── config.py             # Configuración de la aplicación
    ├── sheets_service.py     # Servicio de conexión con Google Sheets
    ├── utils/                # Utilidades varias 
    └── routes/               # Rutas de la API
```

## 🚀 Instalación y Ejecución

### Requisitos Previos

- Python 3.9+
- Node.js 16+
- Acceso a Google Sheets API

### Configuración del Backend

1. Crea un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Configura las credenciales de Google:

Crea un archivo `.env` en la raíz del proyecto con:

```
GOOGLE_CREDENTIALS={"tu_json_de_credenciales_aquí"}
SPREADSHEET_ID=tu_id_de_hoja_de_cálculo
```

### Configuración del Frontend

1. Navega a la carpeta client:

```bash
cd client
```

2. Instala las dependencias:

```bash
npm install
```

3. Crea un archivo `.env` para las variables de entorno:

```
REACT_APP_API_URL=http://localhost:5000
```

### Ejecución en Desarrollo

1. Inicia el backend:

```bash
flask run
```

2. Inicia el frontend (en otra terminal):

```bash
cd client
npm start
```

## 📦 Despliegue en Heroku

### Preparación

1. Asegúrate de tener Heroku CLI instalado y estar autenticado

2. Crea una nueva aplicación en Heroku:

```bash
heroku create cafe-dashboard
```

3. Configura las variables de entorno en Heroku:

```bash
heroku config:set GOOGLE_CREDENTIALS='{"tu_json_de_credenciales_aquí"}' --app cafe-dashboard
heroku config:set SPREADSHEET_ID=tu_id_de_hoja_de_cálculo --app cafe-dashboard
```

### Despliegue

Puedes desplegar directamente desde el repositorio GitHub conectando la aplicación Heroku, o mediante:

```bash
git push heroku main
```

## 🔄 Integración con el Bot de Telegram

Este dashboard lee los mismos datos que utiliza el [bot de Telegram para gestión de café](https://github.com/sofiaqsy/cafe-bot-telegram), ambos pueden funcionar de forma independiente, pero se complementan entre sí:

- El **bot de Telegram** maneja las operaciones diarias de registro de compras, ventas, etc.
- El **dashboard web** proporciona visualizaciones y análisis detallados para toma de decisiones

No se requiere configuración adicional para la integración, ya que ambos utilizan las mismas hojas de Google Sheets como fuente de datos.

## 📃 Licencia

Este proyecto está licenciado bajo MIT License - ver el archivo [LICENSE](LICENSE) para más detalles.
