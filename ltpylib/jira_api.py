#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import re
from typing import Dict, List, Tuple, Union

import jira.resources
from jira import JIRA
from requests import Session

from ltpylib import inputs, strconverters, strings
from ltpylib.collect import EMPTY_LIST, EMPTY_MAP, to_csv
from ltpylib.jira_api_types import Issue, IssueSearchResult, JiraProject, Sprint, SprintReport, SprintState, VelocityReport

OPTION_AGILE_REST_PATH = "agile_rest_path"

JIRA_API_SEARCH: str = "/rest/api/2/search"
JIRA_API_EPICS: str = "/rest/greenhopper/latest/xboard/plan/backlog/epics"
JIRA_API_SPRINT_REPORT: str = "/rest/greenhopper/1.0/rapid/charts/sprintreport"
JIRA_API_VELOCITY_REPORT: str = "/rest/greenhopper/1.0/rapid/charts/velocity.json"

ISSUE_FIELD_SPRINT_FINAL: str = "sprintFinal"
ISSUE_FIELD_SPRINT_RAW: str = "sprintRaw"


class JiraApi(object):

  def __init__(
    self,
    api: JIRA = None,
    url: str = None,
    auth: Tuple[str, str] = None,
    basic_auth: Tuple[str, str] = None,
  ):
    if api is not None:
      self.api: JIRA = api
    elif url is not None and (auth is not None or basic_auth is not None):
      self.api: JIRA = JIRA(
        url,
        auth=auth,
        basic_auth=basic_auth,
        options={
          OPTION_AGILE_REST_PATH: jira.resources.GreenHopperResource.AGILE_BASE_REST_PATH,
        },
      )
    else:
      raise Exception("Must be initialized with 'api: JIRA' instance or both 'url' and 'auth'")

  def get_session(self) -> Session:
    return self.api._session

  def board_id(
    self,
    board_id_or_name: Union[str, int],
  ) -> int:
    if isinstance(board_id_or_name, int) or board_id_or_name.isdigit():
      return int(board_id_or_name)

    boards = self.api.boards(maxResults=0)
    for maybe_board in boards:
      if maybe_board.id == board_id_or_name or maybe_board.name == board_id_or_name:
        return int(maybe_board.id)

    raise Exception("Could not find board=%s, choices below:\n%s" % (board_id_or_name, "\n".join(["%s (%s)" % (board.id, board.name) for board in boards])))

  def epics(
    self,
    board_id: int,
  ) -> dict:
    return self.get_session().get(self.api.client_info() + JIRA_API_EPICS + "?rapidViewId=" + str(board_id)).json()

  def issue(
    self,
    id: str,
    fields: List[str] = None,
    expand: List[str] = None,
    # parse response config
    no_convert: bool = False,
    convert_single_value_arrays: bool = False,
    create_new_result: bool = False,
    skip_fields: List[str] = EMPTY_LIST,
    dict_field_to_inner_field: Dict[str, str] = EMPTY_MAP,
    join_array_fields: List[str] = EMPTY_LIST,
    date_fields: List[str] = EMPTY_LIST
  ) -> Issue:
    return Issue(
      values=JiraApi.parse_api_response_with_names(
        self.api.issue(
          id,
          fields=to_csv(fields),
          expand=JiraApi.expand_with_names(expand),
        ).raw,
        no_convert=no_convert,
        convert_single_value_arrays=convert_single_value_arrays,
        create_new_result=create_new_result,
        skip_fields=skip_fields,
        dict_field_to_inner_field=dict_field_to_inner_field,
        join_array_fields=join_array_fields,
        date_fields=date_fields
      )
    )

  def issue_summaries(
    self,
    issues: List[str],
    markdown: bool = False,
    link: bool = False,
  ) -> List[str]:
    summaries = []

    for issue in issues:
      if issue.count("/") > 0:
        issue_key = issue.split("/")[-1]
      else:
        issue_key = issue

      result = self.issue(issue_key)

      if markdown:
        summary: str = "[%s](%s/browse/%s) `%s`" % (self.url, result.key, result.key, result.summary)
      elif link:
        summary: str = "%s/browse/%s %s" % (self.url, result.key, result.summary)
      else:
        summary: str = "%s %s" % (result.key, result.summary)

      summaries.append(summary)

    return summaries

  def project(
    self,
    project_id_or_name: Union[str, int],
  ) -> JiraProject:
    jira_project: jira.resources.Project = self.api.project(project_id_or_name)
    return JiraProject(values=jira_project.raw)

  def search_issues(
    self,
    jql_or_filter_id: Union[str, int],
    start_at: int = 0,
    max_results: Union[int, bool] = 50,
    validate_query: bool = True,
    fields: List[str] = None,
    expand: List[str] = None,
    json_result: bool = True,
    # parse response config
    no_convert: bool = False,
    convert_single_value_arrays: bool = False,
    create_new_result: bool = False,
    skip_fields: List[str] = EMPTY_LIST,
    dict_field_to_inner_field: Dict[str, str] = EMPTY_MAP,
    join_array_fields: List[str] = EMPTY_LIST,
    date_fields: List[str] = EMPTY_LIST,
  ) -> IssueSearchResult:
    if isinstance(jql_or_filter_id, int) or jql_or_filter_id.isdigit():
      jira_filter: jira.resources.Filter = self.api.filter(jql_or_filter_id)
      jql: str = jira_filter.jql
    else:
      jql: str = jql_or_filter_id

    get_all = isinstance(max_results, bool) and not max_results
    if json_result:
      check_for_more = get_all or max_results > 100
      max_results_param = 100 if check_for_more else max_results
    else:
      check_for_more = False
      max_results_param = max_results

    fields_csv = to_csv(fields)
    expanded_with_names = JiraApi.expand_with_names(expand)
    result = IssueSearchResult(
      values=JiraApi.parse_api_response_with_names(
        self.api.search_issues(
          jql,
          startAt=start_at,
          maxResults=max_results_param,
          validate_query=validate_query,
          fields=fields_csv,
          expand=expanded_with_names,
          json_result=json_result,
        ),
        "issues",
        no_convert=no_convert,
        convert_single_value_arrays=convert_single_value_arrays,
        create_new_result=create_new_result,
        skip_fields=skip_fields,
        dict_field_to_inner_field=dict_field_to_inner_field,
        join_array_fields=join_array_fields,
        date_fields=date_fields
      )
    )

    if check_for_more:
      last_result = result

      while last_result.issues and len(result.issues) < result.total and (get_all or len(result.issues) < max_results):
        more_start_at = last_result.startAt + last_result.maxResults

        last_result = IssueSearchResult(
          values=JiraApi.parse_api_response_with_names(
            self.api.search_issues(
              jql,
              startAt=more_start_at,
              maxResults=max_results_param,
              validate_query=validate_query,
              fields=fields_csv,
              expand=expanded_with_names,
              json_result=json_result,
            ),
            "issues",
            no_convert=no_convert,
            convert_single_value_arrays=convert_single_value_arrays,
            create_new_result=create_new_result,
            skip_fields=skip_fields,
            dict_field_to_inner_field=dict_field_to_inner_field,
            join_array_fields=join_array_fields,
            date_fields=date_fields
          )
        )

        result.issues.extend(last_result.issues)

    return result

  def sprint_id(
    self,
    sprint_id_or_name: Union[str, int],
    board_id: int,
    allow_select_sprint: bool = True,
    find_active_sprint: bool = False,
    find_first_future_sprint: bool = False,
    include_closed_sprints: bool = False,
  ) -> int:
    if not sprint_id_or_name:
      if not allow_select_sprint:
        raise ValueError("sprint_id_or_name is None and allow_select_sprint=False")

      return self.sprint_selection(
        board_id,
        find_active_sprint=find_active_sprint,
        find_first_future_sprint=find_first_future_sprint,
        include_closed_sprints=include_closed_sprints,
      )

    if isinstance(sprint_id_or_name, int) or sprint_id_or_name.isdigit():
      return int(sprint_id_or_name)

    sprints = self.api.sprints(board_id)
    for maybe_sprint in sprints:
      if maybe_sprint.id == sprint_id_or_name or maybe_sprint.name == sprint_id_or_name:
        return int(maybe_sprint.id)

    raise Exception("Could not find sprint=%s, choices below:\n%s" % (sprint_id_or_name, "\n".join(JiraApi.create_sprint_choices(sprints))))

  def sprint_issues(
    self,
    board_id_or_name: Union[str, int],
    sprint_id_or_name: Union[str, int] = None,
    find_active_sprint: bool = False,
    find_first_future_sprint: bool = False,
    include_closed_sprints: bool = False,
    add_filters: List[str] = None,
    include_placeholder: bool = False,
    include_sub_tasks: bool = False,
    unassigned: bool = False,
    unestimated: bool = False,
    fields: List[str] = None,
    max_results: int = 500,
  ) -> IssueSearchResult:
    board_id = self.board_id(board_id_or_name)
    sprint_id = self.sprint_id(
      sprint_id_or_name,
      board_id,
      allow_select_sprint=True,
      find_active_sprint=find_active_sprint,
      find_first_future_sprint=find_first_future_sprint,
      include_closed_sprints=include_closed_sprints,
    )

    add_filters = " ".join(
      JiraApi.create_filters(
        add_filters=add_filters,
        include_placeholder=include_placeholder,
        include_sub_tasks=include_sub_tasks,
        unassigned=unassigned,
        unestimated=unestimated,
      )
    )

    jql = "Sprint = %s %s ORDER BY updated DESC" % (sprint_id, add_filters)

    return self.search_issues(jql, max_results=max_results, fields=fields)

  def sprint_report(
    self,
    board_id: int,
    sprint_id: int,
  ) -> SprintReport:
    url = self.api.client_info() + JIRA_API_SPRINT_REPORT + "?rapidViewId=%s&sprintId=%s" % (board_id, sprint_id)
    return SprintReport(self.get_session().get(url).json())

  def sprint_selection(
    self,
    board_id: int,
    find_active_sprint: bool = False,
    find_first_future_sprint: bool = False,
    include_closed_sprints: bool = False,
    include_closed_sprints_count: int = 2,
  ) -> int:
    sprints = self.sprints(
      board_id,
      include_closed_sprints=include_closed_sprints,
      include_closed_sprints_count=include_closed_sprints_count,
    )
    choices = JiraApi.create_sprint_choices(sprints)

    if find_active_sprint:
      for sprint in sprints:
        if sprint.state == "ACTIVE":
          return int(sprint.id)

      raise Exception("No ACTIVE sprint found in sprints below:\n%s" % "\n".join(choices))
    elif find_first_future_sprint:
      for sprint in sprints:
        if sprint.state == "FUTURE":
          return int(sprint.id)

      raise Exception("No FUTURE sprint found in sprints below:\n%s" % "\n".join(choices))

    choice = inputs.select_prompt(choices)
    return int(strings.substring_before(choice, " ("))

  def sprints(
    self,
    board_id: int,
    include_closed_sprints: bool = True,
    include_closed_sprints_count: int = None,
  ) -> List[Sprint]:
    if self.using_greenhopper():
      state = None
    else:
      sprint_states = ["active", "future"]
      if include_closed_sprints:
        sprint_states.append("closed")
      state = ",".join(sprint_states)

    sprints: List[Sprint] = [Sprint(sprint.raw) for sprint in self.api.sprints(board_id, state=state)]
    if not include_closed_sprints:
      sprints = [sprint for sprint in sprints if sprint.state != SprintState.CLOSED]
    elif include_closed_sprints_count is not None and include_closed_sprints_count > 0:
      closed_sprints: List[Sprint] = [sprint for sprint in sprints if sprint.state == SprintState.CLOSED]
      other_sprints: List[Sprint] = [sprint for sprint in sprints if sprint.state != SprintState.CLOSED]
      closed_sprints = sorted(closed_sprints, key=lambda spr: spr.endDate, reverse=True)[:include_closed_sprints_count]
      sprints = sorted(other_sprints + closed_sprints, key=lambda spr: spr.id)

    return sprints

  def using_greenhopper(self) -> bool:
    return self.api._options[OPTION_AGILE_REST_PATH] == jira.resources.GreenHopperResource.GREENHOPPER_REST_PATH

  def velocity_report(
    self,
    board_id: int,
  ) -> VelocityReport:
    url = self.api.client_info() + JIRA_API_VELOCITY_REPORT + "?rapidViewId=%s" % (board_id)
    return VelocityReport(self.get_session().get(url).json())

  @staticmethod
  def create_filters(
    add_filters: List[str] = None,
    include_placeholder: bool = False,
    include_sub_tasks: bool = False,
    unassigned: bool = False,
    unestimated: bool = False,
  ) -> List[str]:
    filters: List[str] = []
    if add_filters:
      filters.extend(add_filters)

    if not include_placeholder:
      filters.append("AND (labels IS EMPTY OR labels NOT IN (placeholder))")

    if not include_sub_tasks:
      filters.append("AND type NOT IN (Sub-task)")

    if unassigned:
      filters.append("AND assignee IS NULL")

    if unestimated:
      filters.append("AND \"Story Points\" IS NULL")

    return filters

  @staticmethod
  def create_issues_display(issues: List[Issue], fields: List[str]) -> List[str]:
    return sorted([" ".join([getattr(issue, field) for field in fields]) for issue in issues])

  @staticmethod
  def create_sprint_choices(sprints: List[Sprint]) -> List[str]:
    return [('%s (%s): %s' % (sprint.id, sprint.state.name, sprint.name)) for sprint in sprints]

  @staticmethod
  def expand_with_names(expand: List[str]) -> str:
    if expand is None:
      expand = []

    expand.append("names")
    return to_csv(expand)

  @staticmethod
  def parse_api_response_with_names(
    result: dict,
    convert_values_field: str = None,
    names_field: str = "names",
    fields_field: str = "fields",
    no_convert: bool = False,
    convert_single_value_arrays: bool = False,
    create_new_result: bool = False,
    skip_fields: List[str] = EMPTY_LIST,
    dict_field_to_inner_field: Dict[str, str] = EMPTY_MAP,
    join_array_fields: List[str] = EMPTY_LIST,
    date_fields: List[str] = EMPTY_LIST
  ) -> dict:
    if not convert_values_field:
      convert_values: List[Dict] = [result]
    else:
      convert_values_temp: Union[dict, List[dict]] = result.get(convert_values_field)
      if isinstance(convert_values_temp, list):
        convert_values: List[Dict] = convert_values_temp
      else:
        convert_values: List[Dict] = [convert_values_temp]

    names: Dict[str, str] = result.get(names_field)
    array_fields: List[str] = []
    convert_array_fields: List[str] = []

    for convert_value in convert_values:
      if create_new_result:
        updated_value: Dict = {}
      else:
        updated_value: Dict = convert_value

      if create_new_result:
        for entry in convert_value.items():
          if entry[0] != fields_field and not entry[0] in skip_fields:
            updated_value[entry[0]] = entry[1]
      elif skip_fields:
        for field in skip_fields:
          if field != fields_field and field in updated_value:
            updated_value.pop(field)

      if create_new_result:
        issue_fields: Dict = convert_value.get(fields_field, {})
      else:
        issue_fields: Dict = convert_value.pop(fields_field, {})

      for entry in issue_fields.items():
        key: str = entry[0]
        val = entry[1]
        if val is None:
          continue
        elif isinstance(val, list) and not val:
          continue
        elif no_convert:
          updated_value[key] = val
          continue

        orig_key: str = key
        if key.startswith("customfield_") and key in names:
          key = strconverters.to_camel_case(names.get(key))

        if key in skip_fields or orig_key in skip_fields:
          continue
        elif key == "sprint":
          sprints: List[Union[str, dict]] = val
          if isinstance(sprints[0], str):
            val = [re.match(r".*,name=(.*?),.*", sprint).group(1) for sprint in sprints]
          else:
            val = [sprint.get("name") for sprint in sprints]

          if ISSUE_FIELD_SPRINT_RAW not in skip_fields:
            updated_value[ISSUE_FIELD_SPRINT_RAW] = sprints
          if ISSUE_FIELD_SPRINT_FINAL not in skip_fields:
            updated_value[ISSUE_FIELD_SPRINT_FINAL] = val[-1]
        elif key in dict_field_to_inner_field:
          if key not in skip_fields:
            updated_value[key] = val
          inner_field: str = dict_field_to_inner_field.get(key)
          if isinstance(val, dict):
            val = val.get(inner_field)
            key = key + "_" + inner_field
          elif isinstance(val, list):
            val = [elem.get(inner_field) for elem in val]
            key = key + "_" + inner_field

        if isinstance(val, list):
          if key in join_array_fields:
            val = ",".join(val)
          elif convert_single_value_arrays:
            if key not in array_fields:
              array_fields.append(key)
              convert_array_fields.append(key)

            if len(val) > 1:
              if key in convert_array_fields:
                convert_array_fields.remove(key)
        # elif key in date_fields:
        #   val = val.replace("-0400", "").replace("-0500", "").replace("T", " ")

        updated_value[key] = val

    if not no_convert and convert_single_value_arrays and convert_array_fields:
      for field in convert_array_fields:
        for convert_value in convert_values:
          if field in convert_value and convert_value.get(field):
            convert_value[field] = "\n".join(convert_value.get(field))

    return result

  @property
  def url(self):
    return self.api._options["server"]
