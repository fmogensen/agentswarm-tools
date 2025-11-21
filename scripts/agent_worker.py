#!/usr/bin/env python3
"""
Agent Worker - Development Team Member

Each worker receives tool assignments from the orchestrator and develops them
using AI-powered code generation.
"""

import os
import sys
import asyncio
import logging
import json
import argparse
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import redis.asyncio as redis
except ImportError:
    import redis
    redis.asyncio = redis

# Import generators
from code_generator import ToolCodeGenerator
from test_generator import ToolTestGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentWorker:
    """Development team worker that builds tools using AI."""

    def __init__(self, team_id: str, team_name: str):
        self.team_id = team_id
        self.team_name = team_name
        self.redis_client = None
        self.current_assignment = None
        self.autonomous_mode = os.getenv('AUTONOMOUS_MODE', 'true').lower() == 'true'

        # Initialize AI generators
        try:
            self.code_generator = ToolCodeGenerator()
            self.test_generator = ToolTestGenerator()
            logger.info(f"✅ {team_id}: AI generators initialized")
        except Exception as e:
            logger.error(f"❌ {team_id}: Failed to initialize generators: {e}")
            raise

    async def connect(self):
        """Connect to Redis."""
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        self.redis_client = await redis.from_url(redis_url, decode_responses=True)
        logger.info(f"🤖 {self.team_id} ({self.team_name}) connected to Redis")

    async def get_assignment(self) -> Optional[Dict[str, Any]]:
        """Get next tool assignment from queue."""
        try:
            # Pop from team-specific queue
            queue_key = f"queue:{self.team_id}"
            assignment_json = await self.redis_client.lpop(queue_key)

            if assignment_json:
                assignment = json.loads(assignment_json)
                logger.info(f"📋 {self.team_id} received: {assignment.get('tool_name')}")
                return assignment

            # If team queue empty, try general queue
            general_assignment = await self.redis_client.lpop("queue:pending")
            if general_assignment:
                assignment = json.loads(general_assignment)
                logger.info(f"📋 {self.team_id} received from general queue: {assignment.get('tool_name')}")
                return assignment

            return None

        except Exception as e:
            logger.error(f"Error getting assignment: {e}")
            return None

    async def develop_tool(self, assignment: Dict[str, Any]) -> bool:
        """
        Develop the assigned tool using AI code generation.

        Steps:
        1. Load tool specification
        2. Generate code with Claude
        3. Generate tests
        4. Write files
        5. Format with black
        6. Type check with mypy
        7. Report completion
        """
        tool_name = assignment.get('tool_name')
        category = assignment.get('category', 'unknown')

        logger.info(f"🔨 {self.team_id} developing: {tool_name}")

        try:
            # Step 1: Load tool specification
            await self._update_status(tool_name, "loading_spec", 10)
            spec = self._load_spec(tool_name)

            if not spec:
                raise ValueError(f"No specification found for {tool_name}")

            # Step 2: Generate code
            await self._update_status(tool_name, "generating_code", 30)
            logger.info(f"  🤖 Generating code for {tool_name}...")
            tool_code = self.code_generator.generate_tool_code(spec)

            # Step 3: Generate tests
            await self._update_status(tool_name, "generating_tests", 50)
            logger.info(f"  🧪 Generating tests for {tool_name}...")
            test_code = self.test_generator.generate_test_code(spec, tool_code)

            # Step 4: Write files
            await self._update_status(tool_name, "writing_files", 70)
            logger.info(f"  📝 Writing files for {tool_name}...")
            self._write_tool_files(tool_name, category, tool_code, test_code)

            # Step 5: Format with black
            await self._update_status(tool_name, "formatting", 80)
            logger.info(f"  ✨ Formatting {tool_name}...")
            self._format_code(tool_name, category)

            # Step 6: Type check (optional, may fail initially)
            await self._update_status(tool_name, "type_checking", 90)
            logger.info(f"  🔍 Type checking {tool_name}...")
            # Type checking is done by continuous_tester

            # Step 7: Mark complete
            await self._update_status(tool_name, "completed", 100)
            await self.redis_client.hset(
                f"tool:{tool_name}",
                mapping={
                    "status": "completed",
                    "assigned_to": self.team_id,
                    "started_at": assignment.get("assigned_at", datetime.now().isoformat()),
                    "completed_at": datetime.now().isoformat(),
                    "category": category
                }
            )

            # Publish completion event
            await self.redis_client.publish(
                "events:tool_completed",
                json.dumps({
                    "tool_name": tool_name,
                    "team_id": self.team_id,
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                })
            )

            logger.info(f"✅ {self.team_id} completed: {tool_name}")
            return True

        except Exception as e:
            logger.error(f"❌ {self.team_id} failed on {tool_name}: {e}")

            # Mark as failed
            await self.redis_client.hset(
                f"tool:{tool_name}",
                mapping={
                    "status": "failed",
                    "error": str(e),
                    "failed_at": datetime.now().isoformat(),
                    "team_id": self.team_id
                }
            )

            return False

    def _load_spec(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Load tool specification from file."""
        spec_path = Path(f"data/tool_specs/{tool_name}.json")
        if spec_path.exists():
            with open(spec_path) as f:
                return json.load(f)
        return None

    def _write_tool_files(
        self,
        tool_name: str,
        category: str,
        tool_code: str,
        test_code: str
    ):
        """Write tool files to disk."""
        # Create directory
        tool_dir = Path(f"tools/{category}/{tool_name}")
        tool_dir.mkdir(parents=True, exist_ok=True)

        # Write __init__.py
        class_name = "".join(word.capitalize() for word in tool_name.split("_"))
        init_content = f'''"""
{tool_name} - {category} tool
"""

from .{tool_name} import {class_name}

__all__ = ["{class_name}"]
'''
        (tool_dir / "__init__.py").write_text(init_content)

        # Write tool implementation
        (tool_dir / f"{tool_name}.py").write_text(tool_code)

        # Write tests
        (tool_dir / f"test_{tool_name}.py").write_text(test_code)

        logger.info(f"  ✅ Files written to {tool_dir}")

    def _format_code(self, tool_name: str, category: str):
        """Format code with black."""
        tool_dir = Path(f"tools/{category}/{tool_name}")

        try:
            subprocess.run(
                ["black", str(tool_dir)],
                capture_output=True,
                check=True,
                timeout=30
            )
            logger.info(f"  ✅ Code formatted")
        except subprocess.CalledProcessError as e:
            logger.warning(f"  ⚠️  Black formatting had issues: {e}")
        except FileNotFoundError:
            logger.warning(f"  ⚠️  Black not found, skipping formatting")

    async def _update_status(self, tool_name: str, phase: str, progress: int):
        """Update tool status in Redis."""
        status_key = f"work:{tool_name}:status"
        status_data = {
            "phase": phase,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        }
        await self.redis_client.set(status_key, json.dumps(status_data))

    async def run(self):
        """Main worker loop."""
        await self.connect()

        logger.info(f"🚀 {self.team_id} ({self.team_name}) started")
        logger.info(f"   Autonomous mode: {self.autonomous_mode}")
        logger.info(f"   AI-powered development enabled")

        check_interval = int(os.getenv('CHECK_INTERVAL', '60'))

        while True:
            try:
                # Get assignment
                assignment = await self.get_assignment()

                if assignment:
                    # Develop the tool
                    success = await self.develop_tool(assignment)

                    if success:
                        # Increment completed counter
                        await self.redis_client.incr("metrics:completed_by_workers")
                    else:
                        # Increment failed counter
                        await self.redis_client.incr("metrics:failed_attempts")

                        # Re-queue if auto-fix enabled
                        if os.getenv('AUTO_FIX', 'true').lower() == 'true':
                            retry_count = assignment.get('retry_count', 0)
                            max_retries = int(os.getenv('RETRY_ATTEMPTS', '5'))

                            if retry_count < max_retries:
                                assignment['retry_count'] = retry_count + 1
                                await self.redis_client.rpush(
                                    "queue:pending",
                                    json.dumps(assignment)
                                )
                                logger.info(f"🔄 Re-queued {assignment['tool_name']} (attempt {retry_count + 1}/{max_retries})")
                else:
                    # No work available - wait
                    logger.debug(f"💤 {self.team_id} waiting for work...")
                    await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(30)

    async def cleanup(self):
        """Cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='AgentSwarm Development Worker')
    parser.add_argument('--team', required=True, help='Team ID (e.g., team1)')
    args = parser.parse_args()

    # Get team info from environment
    team_id = os.getenv('TEAM_ID', args.team)
    team_name = os.getenv('TEAM_NAME', 'unknown')

    # Create and run worker
    worker = AgentWorker(team_id, team_name)

    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info(f"🛑 {team_id} shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await worker.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
