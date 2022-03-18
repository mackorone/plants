#!/usr/bin/env python3

import logging
import os
import subprocess
from typing import Optional, Sequence

from .external import external

logger: logging.Logger = logging.getLogger(__name__)


class Committer:
    NAME = "github-actions[bot]"
    EMAIL = "github-actions[bot]@users.noreply.github.com"

    @classmethod
    def commit_and_push_if_github_actions(cls) -> None:
        github_actions = cls._get_env("GITHUB_ACTIONS")
        if github_actions != "true":
            logger.info("Not GitHub Actions, skipping")
            return

        result = cls._run(["git", "status", "-s"])
        any_changes = bool(result.stdout)
        if not any_changes:
            logger.info("No changes, skipping")
            return

        logger.info("Staging changes")
        cls._run(["git", "add", "-A"])

        logger.info("Committing changes")
        run_number = cls._get_env("GITHUB_RUN_NUMBER")
        event_name = cls._get_env("GITHUB_EVENT_NAME")
        cls._run(
            [
                "git",
                "-c",
                f"user.name={cls.NAME}",
                "-c",
                f"user.email={cls.EMAIL}",
                "commit",
                "-m",
                f"Run {run_number} via {event_name}",
            ]
        )

        logger.info("Pushing changes")
        cls._run(["git", "push"])

    @classmethod
    @external
    def _get_env(cls, name: str) -> Optional[str]:
        return os.environ.get(name)

    @classmethod
    @external
    def _run(cls, args: Sequence[str]) -> subprocess.CompletedProcess:
        return subprocess.run(args=args, capture_output=True, check=True, text=True)
