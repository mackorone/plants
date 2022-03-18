#!/usr/bin/env python3

import logging
import os
import subprocess
from typing import Optional, Sequence

from .external import external

logger: logging.Logger = logging.getLogger(__name__)


class Committer:
    @classmethod
    def commit_and_push_if_github_actions(cls) -> None:
        github_actions = cls._get_env("GITHUB_ACTIONS")
        if github_actions != "true":
            logger.info("Not GitHub Actions, skipping")
            return

        run_number = cls._get_env("GITHUB_RUN_NUMBER")
        event_name = cls._get_env("GITHUB_EVENT_NAME")
        cls.commit_and_push(
            commit_message=f"Run {run_number} via {event_name}",
            user_name="github-actions[bot]",
            user_email="github-actions[bot]@users.noreply.github.com",
        )

    @classmethod
    def commit_and_push(
        cls,
        commit_message: str,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> None:
        result = cls._run(["git", "status", "--short"])
        any_changes = bool(result.stdout)
        if not any_changes:
            logger.info("No changes, skipping")
            return

        logger.info("Staging changes")
        cls._run(["git", "add", "--all"])

        logger.info("Committing changes")
        args = ["git"]
        if user_name:
            args += ["-c", f"user.name={user_name}"]
        if user_email:
            args += ["-c", f"user.email={user_email}"]
        args += ["commit", "-m", commit_message]
        cls._run(args)

        logger.info("Pushing changes")
        cls._run(["git", "push"])

    @classmethod
    @external
    def _get_env(cls, name: str) -> Optional[str]:
        return os.environ.get(name)

    @classmethod
    @external
    def _run(cls, args: Sequence[str]) -> "subprocess.CompletedProcess[str]":
        return subprocess.run(args=args, capture_output=True, check=True, text=True)
