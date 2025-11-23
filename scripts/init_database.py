#!/usr/bin/env python3
"""
Database Initialization Script

Initializes PostgreSQL database schema for analytics and metrics.
Creates tables and sets up initial data.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

try:
    import asyncpg
except ImportError:
    # If asyncpg not available, provide graceful fallback
    asyncpg = None

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Database initialization handler."""

    def __init__(self):
        self.connection = None
        self.db_url = os.getenv(
            "DATABASE_URL", "postgresql://agentswarm:agentswarm@postgres:5432/agentswarm"
        )

    async def connect(self):
        """Connect to PostgreSQL database."""
        if not asyncpg:
            logger.warning("⚠️ asyncpg not installed - skipping database initialization")
            return False

        try:
            # Parse connection string
            # postgresql://user:pass@host:port/dbname
            self.connection = await asyncpg.connect(self.db_url)
            logger.info("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False

    async def create_analytics_table(self):
        """Create analytics events table."""
        query = """
        CREATE TABLE IF NOT EXISTS analytics_events (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            tool_name VARCHAR(100) NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            duration_ms FLOAT,
            success BOOLEAN DEFAULT TRUE,
            error_code VARCHAR(50),
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_analytics_tool_name ON analytics_events(tool_name);
        CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics_events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics_events(event_type);
        """

        try:
            await self.connection.execute(query)
            logger.info("✅ Created analytics_events table")
        except Exception as e:
            logger.error(f"❌ Failed to create analytics_events table: {e}")

    async def create_tool_metrics_table(self):
        """Create tool metrics table."""
        query = """
        CREATE TABLE IF NOT EXISTS tool_metrics (
            id SERIAL PRIMARY KEY,
            tool_name VARCHAR(100) NOT NULL UNIQUE,
            category VARCHAR(50) NOT NULL,
            total_calls INTEGER DEFAULT 0,
            success_calls INTEGER DEFAULT 0,
            error_calls INTEGER DEFAULT 0,
            avg_duration_ms FLOAT DEFAULT 0,
            last_called TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_tool_metrics_category ON tool_metrics(category);
        CREATE INDEX IF NOT EXISTS idx_tool_metrics_last_called ON tool_metrics(last_called);
        """

        try:
            await self.connection.execute(query)
            logger.info("✅ Created tool_metrics table")
        except Exception as e:
            logger.error(f"❌ Failed to create tool_metrics table: {e}")

    async def create_development_log_table(self):
        """Create development activity log table."""
        query = """
        CREATE TABLE IF NOT EXISTS development_log (
            id SERIAL PRIMARY KEY,
            tool_name VARCHAR(100) NOT NULL,
            action VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            agent_id VARCHAR(50),
            details JSONB,
            timestamp TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_dev_log_tool_name ON development_log(tool_name);
        CREATE INDEX IF NOT EXISTS idx_dev_log_timestamp ON development_log(timestamp);
        CREATE INDEX IF NOT EXISTS idx_dev_log_status ON development_log(status);
        """

        try:
            await self.connection.execute(query)
            logger.info("✅ Created development_log table")
        except Exception as e:
            logger.error(f"❌ Failed to create development_log table: {e}")

    async def create_test_results_table(self):
        """Create test results table."""
        query = """
        CREATE TABLE IF NOT EXISTS test_results (
            id SERIAL PRIMARY KEY,
            tool_name VARCHAR(100) NOT NULL,
            test_run_id VARCHAR(100) NOT NULL,
            tests_passed INTEGER DEFAULT 0,
            tests_failed INTEGER DEFAULT 0,
            coverage_percent FLOAT DEFAULT 0,
            duration_seconds FLOAT DEFAULT 0,
            passed BOOLEAN DEFAULT FALSE,
            errors JSONB,
            timestamp TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_test_results_tool_name ON test_results(tool_name);
        CREATE INDEX IF NOT EXISTS idx_test_results_timestamp ON test_results(timestamp);
        """

        try:
            await self.connection.execute(query)
            logger.info("✅ Created test_results table")
        except Exception as e:
            logger.error(f"❌ Failed to create test_results table: {e}")

    async def insert_initial_data(self):
        """Insert initial seed data."""
        query = """
        INSERT INTO development_log (tool_name, action, status, details)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT DO NOTHING;
        """

        try:
            await self.connection.execute(
                query,
                "system",
                "initialization",
                "completed",
                '{"message": "Database initialized successfully"}',
            )
            logger.info("✅ Inserted initial data")
        except Exception as e:
            logger.error(f"❌ Failed to insert initial data: {e}")

    async def verify_tables(self):
        """Verify all tables exist."""
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
        """

        try:
            rows = await self.connection.fetch(query)
            tables = [row["table_name"] for row in rows]

            logger.info(f"📊 Tables in database: {', '.join(tables)}")

            required_tables = [
                "analytics_events",
                "tool_metrics",
                "development_log",
                "test_results",
            ]

            for table in required_tables:
                if table in tables:
                    logger.info(f"  ✅ {table}")
                else:
                    logger.warning(f"  ⚠️ {table} - MISSING")

        except Exception as e:
            logger.error(f"❌ Failed to verify tables: {e}")

    async def initialize(self):
        """Run complete database initialization."""
        logger.info("🚀 Starting database initialization...")

        connected = await self.connect()

        if not connected:
            logger.warning("⚠️ Skipping database initialization - connection failed")
            return False

        # Create all tables
        await self.create_analytics_table()
        await self.create_tool_metrics_table()
        await self.create_development_log_table()
        await self.create_test_results_table()

        # Insert initial data
        await self.insert_initial_data()

        # Verify
        await self.verify_tables()

        logger.info("✅ Database initialization complete!")
        return True

    async def cleanup(self):
        """Cleanup database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("🔌 Database connection closed")


async def main():
    """Main entry point."""
    initializer = DatabaseInitializer()

    try:
        success = await initializer.initialize()

        if success:
            print("\n✅ Database initialized successfully!")
        else:
            print("\n⚠️ Database initialization skipped or failed")
            print("This is not critical - the system can run without PostgreSQL")

    except KeyboardInterrupt:
        logger.info("🛑 Database initialization cancelled")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        await initializer.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
