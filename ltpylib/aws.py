#!/usr/bin/env python
import base64
import json
from typing import Dict, Optional, Tuple

from boto3.session import Session
from botocore.exceptions import ClientError

AWS_SESSIONS_BY_REGION_PROFILE: Dict[Tuple[Optional[str], Optional[str]], Session] = {}


def create_aws_session(
  region_name: str = None,
  profile_name: str = None,
) -> Session:
  return Session(region_name=region_name, profile_name=profile_name)


def get_or_create_aws_session(
  region_name: str = None,
  profile_name: str = None,
) -> Session:
  key = (region_name, profile_name)
  if key in AWS_SESSIONS_BY_REGION_PROFILE:
    return AWS_SESSIONS_BY_REGION_PROFILE[key]

  session = create_aws_session(region_name=region_name, profile_name=profile_name)
  AWS_SESSIONS_BY_REGION_PROFILE[key] = session
  return session


def set_default_aws_session(region_name: str = None, profile_name: str = None) -> Session:
  session = get_or_create_aws_session(region_name=region_name, profile_name=profile_name)
  AWS_SESSIONS_BY_REGION_PROFILE[(None, None)] = session
  return session


def get_secret_json(secret_name: str, session: Session = None) -> dict:
  if session is None:
    session = get_or_create_aws_session()

  client = session.client(service_name="secretsmanager")

  try:
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
  except ClientError as e:
    if e.response["Error"]["Code"] == "DecryptionFailureException":
      # Secrets Manager can"t decrypt the protected secret text using the provided KMS key.
      # Deal with the exception here, and/or rethrow at your discretion.
      raise e
    elif e.response["Error"]["Code"] == "InternalServiceErrorException":
      # An error occurred on the server side.
      # Deal with the exception here, and/or rethrow at your discretion.
      raise e
    elif e.response["Error"]["Code"] == "InvalidParameterException":
      # You provided an invalid value for a parameter.
      # Deal with the exception here, and/or rethrow at your discretion.
      raise e
    elif e.response["Error"]["Code"] == "InvalidRequestException":
      # You provided a parameter value that is not valid for the current state of the resource.
      # Deal with the exception here, and/or rethrow at your discretion.
      raise e
    elif e.response["Error"]["Code"] == "ResourceNotFoundException":
      # We can"t find the resource that you asked for.
      # Deal with the exception here, and/or rethrow at your discretion.
      raise e
  else:
    # Decrypts secret using the associated KMS key.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if "SecretString" in get_secret_value_response:
      secret = get_secret_value_response["SecretString"]
    else:
      secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    return json.loads(secret)
