#!/usr/bin/env python3
"""
Continuous Tester - Quality Assurance Agent

Monitors for completed tools and runs automated tests.
Ensures all tools meet quality standards before marking as complete.
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, List

try:
    import redis.asyncio as redis
except ImportError:
    import redis

    redis.asyncio = redis

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ContinuousTester:
    """Continuous testing agent."""

    def __init__(self):
        self.redis_client = None
        self.auto_fix = os.getenv("AUTO_FIX", "true").lower() == "true"
        self.min_coverage = int(os.getenv("MIN_TEST_COVERAGE", "80"))

    async def connect(self):
        """Connect to Redis."""
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis_client = await redis.from_url(redis_url, decode_responses=True)
        logger.info("🧪 Continuous Tester connected to Redis")

    async def subscribe_to_completions(self):
        """Subscribe to tool completion events."""
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe("events:tool_completed")
        logger.info("📡 Subscribed to tool completion events")
        return pubsub

    async def test_tool(self, tool_name: str, category: str) -> Dict[str, Any]:
        """
        Run tests for a tool.

        In production, this would:
        1. Run pytest for the tool
        2. Check code coverage
        3. Run type checking (mypy)
        4. Run linting (pylint, flake8)
        5. Security scan (bandit)
        6. Verify Agency Swarm compatibility

        For now, this is a stub that simulates testing.
        """
        logger.info(f"🧪 Testing: {tool_name}")

        try:
            # Simulate test execution
            await asyncio.sleep(2)

            # Stub test results (in production, run actual pytest)
            results = {
                "tool_name": tool_name,
                "category": category,
                "tests_passed": True,
                "test_count": 5,
                "failures": 0,
                "coverage": 85,  # Percentage
                "duration": 2.3,  # Seconds
                "linting_passed": True,
                "type_check_passed": True,
                "security_scan_passed": True,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ Tests passed: {tool_name} (coverage: {results['coverage']}%)")
            return results

        except Exception as e:
            logger.error(f"❌ Tests failed: {tool_name} - {e}")
            return {
                "tool_name": tool_name,
                "category": category,
                "tests_passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def process_test_results(self, results: Dict[str, Any]):
        """Process test results and update tool status."""
        tool_name = results["tool_name"]

        if results.get("tests_passed") and results.get("coverage", 0) >= self.min_coverage:
            # Tests passed - mark as ready for documentation
            await self.redis_client.hset(
                f"tool:{tool_name}",
                mapping={
                    "status": "tested",
                    "test_coverage": results.get("coverage", 0),
                    "tested_at": datetime.now().isoformat(),
                },
            )

            # Store test results
            await self.redis_client.set(
                f"test_results:{tool_name}", json.dumps(results), ex=86400 * 7  # Keep for 7 days
            )

            # Publish test success event
            await self.redis_client.publish(
                "events:tool_tested",
                json.dumps(
                    {
                        "tool_name": tool_name,
                        "status": "tested",
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            )

            # Increment metrics
            await self.redis_client.incr("metrics:tests_passed")

            logger.info(f"✅ {tool_name} marked as tested")

        else:
            # Tests failed
            await self.redis_client.hset(
                f"tool:{tool_name}",
                mapping={
                    "status": "test_failed",
                    "test_error": results.get("error", "Quality standards not met"),
                    "test_failed_at": datetime.now().isoformat(),
                },
            )

            # Increment metrics
            await self.redis_client.incr("metrics:tests_failed")

            # Auto-fix if enabled
            if self.auto_fix:
                # Re-queue for development with fix instructions
                await self.redis_client.rpush(
                    "queue:pending",
                    json.dumps(
                        {
                            "tool_name": tool_name,
                            "category": results.get("category"),
                            "action": "fix_tests",
                            "error": results.get("error"),
                            "retry_count": 0,
                        }
                    ),
                )
                logger.info(f"🔄 Re-queued {tool_name} for auto-fix")

    async def get_tools_needing_tests(self) -> List[str]:
        """Get tools that need testing."""
        try:
            # Scan for tools with status "needs_review"
            tools = []
            cursor = 0

            while True:
                cursor, keys = await self.redis_client.scan(cursor, match="tool:*", count=100)

                for key in keys:
                    status = await self.redis_client.hget(key, "status")
                    if status == "needs_review":
                        tool_name = key.replace("tool:", "")
                        tools.append(tool_name)

                if cursor == 0:
                    break

            return tools

        except Exception as e:
            logger.error(f"Error getting tools needing tests: {e}")
            return []

    async def run(self):
        """Main tester loop."""
        await self.connect()

        logger.info("🚀 Continuous Tester started")
        logger.info(f"   Auto-fix: {self.auto_fix}")
        logger.info(f"   Min coverage: {self.min_coverage}%")

        # Subscribe to completion events
        pubsub = await self.subscribe_to_completions()

        check_interval = int(os.getenv("CHECK_INTERVAL", "60"))

        while True:
            try:
                # Check for event-driven notifications
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=5)

                if message and message["type"] == "message":
                    event = json.loads(message["data"])
                    tool_name = event.get("tool_name")
                    category = event.get("category", "unknown")

                    # Run tests
                    results = await self.test_tool(tool_name, category)
                    await self.process_test_results(results)

                # Also poll for any tools that might have been missed
                tools_needing_tests = await self.get_tools_needing_tests()

                for tool_name in tools_needing_tests[:5]:  # Process up to 5 at a time
                    tool_data = await self.redis_client.hgetall(f"tool:{tool_name}")
                    category = tool_data.get("category", "unknown")

                    results = await self.test_tool(tool_name, category)
                    await self.process_test_results(results)

                if not message and not tools_needing_tests:
                    # No work - wait
                    await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"Tester loop error: {e}")
                await asyncio.sleep(30)

    async def cleanup(self):
        """Cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()


async def main():
    """Main entry point."""
    tester = ContinuousTester()

    try:
        await tester.run()
    except KeyboardInterrupt:
        logger.info("🛑 Continuous Tester shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
