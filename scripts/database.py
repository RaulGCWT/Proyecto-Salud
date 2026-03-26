import boto3
import os
from decimal import Decimal

# Helper para manejar Decimals de DynamoDB en las respuestas JSON de Flask
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# Configuración DynamoDB desde variables de entorno
db_url = os.environ.get("DYNAMODB_URL", "http://dynamodb-local:8000")
dynamodb = boto3.resource(
    'dynamodb', 
    endpoint_url=db_url, 
    region_name='us-east-1', 
    aws_access_key_id='local', 
    aws_secret_access_key='local'
)

# Definición de tablas
table_rules = dynamodb.Table('MonitoringRules')
table_events = dynamodb.Table('DeviceEvents')
table_devices = dynamodb.Table('Devices')
table_invites = dynamodb.Table('FamilyInvites')
table_family_users = dynamodb.Table('FamilyUsers')
table_residents = dynamodb.Table('Residents')
table_staff_members = dynamodb.Table('StaffMembers')

def init_db():
    """Crea las tablas si no existen al arrancar"""
    for t_name in ['MonitoringRules', 'DeviceEvents', 'Devices', 'FamilyInvites', 'FamilyUsers', 'Residents', 'StaffMembers']:
        try:
            dynamodb.create_table(
                TableName=t_name,
                KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            print(f"✅ Tabla {t_name} creada.")
        except Exception:
            # La tabla ya existe
            pass
