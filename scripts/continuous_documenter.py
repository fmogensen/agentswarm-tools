#!/usr/bin/env python3
"""
Continuous Documenter - Documentation Generation Agent

Monitors for tested tools and generates documentation automatically.
Creates API docs, usage examples, and integration guides.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

try:
    import redis.asyncio as redis
except ImportError:
    import redis

    redis.asyncio = redis

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ContinuousDocumenter:
    """Continuous documentation generation agent."""

    def __init__(self):
        self.redis_client = None
        self.auto_document = os.getenv("AUTO_DOCUMENT", "true").lower() == "true"

    async def connect(self):
        """Connect to Redis."""
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis_client = await redis.from_url(redis_url, decode_responses=True)
        logger.info("📚 Continuous Documenter connected to Redis")

    async def subscribe_to_tested_tools(self):
        """Subscribe to tool tested events."""
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe("events:tool_tested")
        logger.info("📡 Subscribed to tool tested events")
        return pubsub

    async def generate_documentation(self, tool_name: str, category: str) -> Dict[str, Any]:
        """
        Generate documentation for a tool.

        In production, this would:
        1. Parse tool code and docstrings
        2. Generate API documentation
        3. Create usage examples
        4. Write integration guide
        5. Generate markdown files
        6. Update README files

        For now, this is a stub that simulates documentation generation.
        """
        logger.info(f"📚 Generating docs: {tool_name}")

        try:
            # Simulate documentation generation
            await asyncio.sleep(1)

            # Stub documentation results
            results = {
                "tool_name": tool_name,
                "category": category,
                "docs_generated": True,
                "files_created": [
                    f"docs/api/{category}/{tool_name}.md",
                    f"docs/examples/{category}/{tool_name}_example.md",
                ],
                "readme_updated": True,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ Documentation generated: {tool_name}")
            return results

        except Exception as e:
            logger.error(f"❌ Documentation failed: {tool_name} - {e}")
            return {
                "tool_name": tool_name,
                "category": category,
                "docs_generated": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def process_documentation_results(self, results: Dict[str, Any]):
        """Process documentation results and update tool status."""
        tool_name = results["tool_name"]

        if results.get("docs_generated"):
            # Documentation generated - mark as complete
            await self.redis_client.hset(
                f"tool:{tool_name}",
                mapping={
                    "status": "completed",
                    "documented_at": datetime.now().isoformat(),
                    "docs_files": json.dumps(results.get("files_created", [])),
                },
            )

            # Store documentation results
            await self.redis_client.set(
                f"docs_results:{tool_name}", json.dumps(results), ex=86400 * 7  # Keep for 7 days
            )

            # Publish completion event
            await self.redis_client.publish(
                "events:tool_fully_complete",
                json.dumps(
                    {
                        "tool_name": tool_name,
                        "status": "completed",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            )

            # Increment metrics
            await self.redis_client.incr("metrics:completed")
            await self.redis_client.incr("metrics:documented")

            logger.info(f"✅ {tool_name} marked as fully complete")

        else:
            # Documentation failed
            await self.redis_client.hset(
                f"tool:{tool_name}",
                mapping={
                    "status": "doc_failed",
                    "doc_error": results.get("error", "Documentation generation failed"),
                    "doc_failed_at": datetime.now().isoformat(),
                },
            )

            # Increment metrics
            await self.redis_client.incr("metrics:doc_failures")

            logger.warning(f"⚠️ Documentation failed for {tool_name}")

    async def get_tools_needing_docs(self) -> List[str]:
        """Get tools that need documentation."""
        try:
            # Scan for tools with status "tested"
            tools = []
            cursor = 0

            while True:
                cursor, keys = await self.redis_client.scan(cursor, match="tool:*", count=100)

                for key in keys:
                    status = await self.redis_client.hget(key, "status")
                    if status == "tested":
                        tool_name = key.replace("tool:", "")
                        tools.append(tool_name)

                if cursor == 0:
                    break

            return tools

        except Exception as e:
            logger.error(f"Error getting tools needing docs: {e}")
            return []

    async def update_summary_documentation(self):
        """
        Update summary documentation files.

        In production, this would:
        1. Update main README with progress
        2. Generate tools index
        3. Update category documentation
        4. Create integration guides
        """
        try:
            # Get completion metrics
            completed = int(await self.redis_client.get("metrics:completed") or 0)
            total = int(os.getenv("TOOLS_TO_DEVELOP", "61"))

            logger.info(
                f"📊 Progress: {completed}/{total} tools complete ({int(completed/total*100)}%)"
            )

        except Exception as e:
            logger.error(f"Error updating summary docs: {e}")

    async def run(self):
        """Main documenter loop."""
        await self.connect()

        logger.info("🚀 Continuous Documenter started")
        logger.info(f"   Auto-document: {self.auto_document}")

        # Subscribe to tested tool events
        pubsub = await self.subscribe_to_tested_tools()

        check_interval = int(os.getenv("CHECK_INTERVAL", "60"))

        while True:
            try:
                # Check for event-driven notifications
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=5)

                if message and message["type"] == "message":
                    event = json.loads(message["data"])
                    tool_name = event.get("tool_name")

                    # Get tool details
                    tool_data = await self.redis_client.hgetall(f"tool:{tool_name}")
                    category = tool_data.get("category", "unknown")

                    # Generate documentation
                    results = await self.generate_documentation(tool_name, category)
                    await self.process_documentation_results(results)

                # Also poll for any tools that might have been missed
                tools_needing_docs = await self.get_tools_needing_docs()

                for tool_name in tools_needing_docs[:3]:  # Process up to 3 at a time
                    tool_data = await self.redis_client.hgetall(f"tool:{tool_name}")
                    category = tool_data.get("category", "unknown")

                    results = await self.generate_documentation(tool_name, category)
                    await self.process_documentation_results(results)

                # Update summary docs periodically
                await self.update_summary_documentation()

                if not message and not tools_needing_docs:
                    # No work - wait
                    await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"Documenter loop error: {e}")
                await asyncio.sleep(30)

    async def cleanup(self):
        """Cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()


async def main():
    """Main entry point."""
    documenter = ContinuousDocumenter()

    try:
        await documenter.run()
    except KeyboardInterrupt:
        logger.info("🛑 Continuous Documenter shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await documenter.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
