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
    DB_SERVER = os.environ.get("DB_SERVER")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

    DRIVER = "ODBC Driver 18 for SQL Server"

    # Build connection string safely
    if DB_SERVER and DB_NAME and DB_USER and DB_PASSWORD:
        params = urllib.parse.quote_plus(
            f"DRIVER={DRIVER};"
            f"SERVER={DB_SERVER};"
            f"PORT=1433;"
            f"DATABASE={DB_NAME};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
    else:
        # Fallback (useful for local testing if DB not set)
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------
    # Azure Blob Storage
    # -----------------------------
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "postimages")

    # -----------------------------
    # Azure AD (Microsoft Login)
    # -----------------------------
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    TENANT_ID = os.environ.get("TENANT_ID")

    AUTHORITY = (
        f"https://login.microsoftonline.com/{TENANT_ID}"
        if TENANT_ID else None
    )

    REDIRECT_PATH = "/getAToken"
    SCOPE = ["User.Read"]

    # -----------------------------
    # Base URL (IMPORTANT for Azure)
    # -----------------------------
    BASE_URL = os.environ.get(
        "BASE_URL",
        "http://127.0.0.1:5000"  # default for local
    )

    # -----------------------------
    # Debug Mode (optional)
    # -----------------------------
    DEBUG = os.environ.get("DEBUG", "False") == "True"
