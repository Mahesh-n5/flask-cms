import os
import urllib.parse

class Config:

    # -----------------------------
    # Flask Secret Key
    # -----------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback_secret")

    # -----------------------------
    # Azure SQL Database
    # -----------------------------
    server = os.environ.get("DB_SERVER")
    database = os.environ.get("DB_NAME")
    username = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")

    driver = "ODBC Driver 18 for SQL Server"

    params = urllib.parse.quote_plus(
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"PORT=1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------
    # Azure Blob Storage
    # -----------------------------
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "postimages")

    # -----------------------------
    # Azure AD Authentication
    # -----------------------------
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    TENANT_ID = os.environ.get("TENANT_ID")

    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    REDIRECT_PATH = "/getAToken"
    SCOPE = ["User.Read"]

    # -----------------------------
    # Azure Website URL
    # -----------------------------
    BASE_URL = os.environ.get("BASE_URL")