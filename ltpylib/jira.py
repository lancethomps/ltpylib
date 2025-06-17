#!/usr/bin/env python
import os
from typing import Tuple

from ltpylib.jira_api import JiraApi

JIRA_URL = os.getenv("JIRA_URL")
JIRA_TOKEN_ENV_VAR = "JIRA_API_TOKEN"
JIRA_TOKEN_USER_ENV_VAR = "JIRA_API_USER"


def create_jira_api(url: str = JIRA_URL, auth: Tuple[str, str] = None) -> JiraApi:
  return JiraApi(
    url=url,
    basic_auth=(auth if auth is not None else get_atlassian_token_auth()),
  )


def get_atlassian_token_auth(env_var_name: str = JIRA_TOKEN_ENV_VAR) -> Tuple[str, str]:
  return os.getenv(JIRA_TOKEN_USER_ENV_VAR), os.getenv(env_var_name)
