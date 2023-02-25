#!/usr/bin/env python3

import logging
from typing import Optional, Tuple

from .environment import Environment
from .subprocess_utils import SubprocessUtils

logger: logging.Logger = logging.getLogger(__name__)


class Committer:
    @classmethod
    def commit_and_push_if_github_actions(cls) -> None:
        if not Environment.is_github_actions():
            logger.info("Not GitHub Actions, skipping")
            return

        run_number = Environment.get_env("GITHUB_RUN_NUMBER")
        event_name = Environment.get_env("GITHUB_EVENT_NAME")
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
        stdout = cls._run(("git", "status", "--short"))
        any_changes = bool(stdout)
        if not any_changes:
            logger.info("No changes, skipping")
            return

        logger.info("Staging changes")
        cls._run(("git", "add", "--all"))

        logger.info("Committing changes")
        args = ["git"]
        if user_name:
            args += ["-c", f"user.name={user_name}"]
        if user_email:
            args += ["-c", f"user.email={user_email}"]
        args += ["commit", "-m", commit_message]
        cls._run(tuple(args))

        logger.info("Pushing changes")
        cls._run(("git", "push"))

    @classmethod
    def _run(cls, args: Tuple[str, ...]) -> str:
        result = SubprocessUtils.run(args, raise_if_nonzero=True)
        return result.stdout
