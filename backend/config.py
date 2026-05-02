import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY   = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGODB_URI  = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/achadinhos')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:5174').split(',')
