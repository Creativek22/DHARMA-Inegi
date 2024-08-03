import pandas as pd

def load_data(filepath):
    """Carga los datos del JSON."""
    return pd.read_json(filepath)

def filter_data(df, column, value):
    """Filtra los datos según la columna y el valor especificado."""
    return df[df[column] == value]

def summarize_data(df):
    """Genera un resumen de los datos."""
    summary = {
        'total_empresas': df.shape[0],
        'actividad_principal': df['Código de la clase de actividad SCIAN'].value_counts().idxmax(),
        'promedio_empleados': df['Descripcion estrato personal ocupado'].value_counts().idxmax() # Ajustado a un cálculo de resumen más general
    }
    return summary
