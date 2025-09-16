from flask import g
from playhouse.pool import PooledPostgresqlExtDatabase
import logging
from datetime import datetime
from config import DB_POOL_CONFIG
from utils.env_config import DATABASE_URL, is_vercel, is_local_to_prod
import os
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

# Initialize with None - will be configured in init_db()
database = None


class MonitoredPooledPostgresqlExtDatabase(PooledPostgresqlExtDatabase):
    """PostgresqlDatabase with connection monitoring and JSON support."""

    def __init__(self, *args, **kwargs):
        """Initialize with timeout attribute."""
        super().__init__(*args, **kwargs)
        self._timeout = kwargs.get("timeout", 30)  # Default to 30 seconds

    def _connect(self, *args, **kwargs):
        """Monitor connection creation."""
        start_time = datetime.now()
        try:
            conn = super()._connect(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            # logger.info(
            #     "Database connection established in %.3f seconds. "
            #     "Pool status: %d connections",
            #     duration,
            #     len(self._connections),
            # )
            return conn
        except Exception as e:
            logger.error("Database connection failed: %s", str(e))
            raise

    def _close(self, conn, close_conn=False):
        """Monitor connection closure."""
        try:
            super()._close(conn, close_conn)
            # logger.info(
            #     "Database connection closed. Pool status: %d connections",
            #     len(self._connections),
            # )
        except Exception as e:
            logger.error("Error closing database connection: %s", str(e))
            raise


def parse_database_url(url: str) -> dict:
    """Parse DATABASE_URL into connection parameters.

    Args:
        url: Database URL string

    Returns:
        dict: Connection parameters
    """
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")  # Remove leading slash

    config = {
        "database": path,
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname,
        "port": parsed.port,
    }

    # Require SSL for production and local-to-prod connections
    if is_vercel() or is_local_to_prod():
        config["sslmode"] = "require"

    return config


def get_db_config():
    """Get database configuration from DATABASE_URL.

    Configuration is loaded from environment variables via env_config.py.
    """
    # Parse the database URL into connection parameters
    db_url = DATABASE_URL.get_secret_value()
    # Start from base pool config, allow env overrides in dev/test
    pool_cfg = dict(DB_POOL_CONFIG)
    try:
        env_max = os.getenv("DB_POOL_MAX_CONNECTIONS")
        if env_max:
            pool_cfg["max_connections"] = int(env_max)
        env_stale = os.getenv("DB_POOL_STALE_TIMEOUT")
        if env_stale:
            pool_cfg["stale_timeout"] = int(env_stale)
        env_timeout = os.getenv("DB_POOL_TIMEOUT")
        if env_timeout:
            pool_cfg["timeout"] = int(env_timeout)
    except Exception:
        # Ignore bad overrides to avoid crashing app
        pass

    config = {**parse_database_url(db_url), **pool_cfg}

    logger.info(
        "Configuring Postgres connection to %s@%s:%s/%s",
        config["user"],
        config["host"],
        config["port"],
        config["database"],
    )

    return MonitoredPooledPostgresqlExtDatabase(**config)


def get_db():
    """Get database connection."""
    global database

    if database is None:
        database = get_db_config()

    if not hasattr(g, "db"):
        g.db = database
        if isinstance(database, PooledPostgresqlExtDatabase):
            logger.debug(
                "Database connection acquired. Pool status: %d connections",
                len(database._connections),
            )
    return g.db


def close_db(e=None):
    """Close database connection"""
    db = getattr(g, "db", None)
    if db is not None and not db.is_closed():
        db.close()
        if isinstance(db, PooledPostgresqlExtDatabase):
            logger.debug(
                "Database connection released. Pool status: %d connections",
                len(db._connections),
            )


def init_db(app=None, test_db=None):
    """Initialize database connection.

    Args:
        app: Optional Flask app to register database hooks with
        test_db: Optional test database to use instead of the default
    """
    global database

    if test_db:
        # Use provided test database (for testing)
        database = test_db
    else:
        # Use environment-appropriate database
        database = get_db_config()

    # Bind all models to the database
    from db_models import get_models

    for model in get_models():
        model._meta.database = database

    if app:
        app.before_request(before_request)
        app.teardown_request(teardown_request)


def before_request():
    """Ensure database connection before each request."""
    global database

    if database is None:
        database = get_db_config()

    if not hasattr(g, "db"):
        g.db = database
        if isinstance(database, PooledPostgresqlExtDatabase):
            logger.debug(
                "Database connection acquired. Pool status: %d connections",
                len(database._connections),
            )
    return None


def teardown_request(exception):
    """Close database connection after each request"""
    db = getattr(g, "db", None)
    if db is not None and not db.is_closed():
        db.close()
    return None


def init_tables():
    """Create all tables"""
    global database
    from db_models import get_models

    if database is None:
        database = get_db_config()

    # Bind all models to the database
    for model in get_models():
        model._meta.database = database

    if not database.is_closed():
        database.connect()

    try:
        database.create_tables(get_models())
    finally:
        if not database.is_closed():
            database.close()
