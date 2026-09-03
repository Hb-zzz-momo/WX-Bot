from tools.calculator import calculator
from tools.weather import get_weather
from tools.air_quality import get_air_quality

from tools.amap import (
    get_ip_location,
    find_poi_nearby,
    geocode_location,
)

from tools.exchange_rate import exchange_rate
from tools.express import check_express
from tools.search import web_search
from tools.user_memory import (
    remember_user_memory,
    forget_user_memory,
)

from tools.working_memory import (
    update_working_memory,
)

from tools.github import (
    github_search_repositories,
    github_get_repository,
    github_get_readme,
    github_get_contents,
    github_list_issues,
    github_list_pull_requests,
    github_list_commits,
    github_list_releases,
    github_list_contributors,
    github_get_languages,
    github_search_code,
    github_get_file_content,
)

from tools.working_memory import (
    update_working_memory,
    clear_working_memory,
)

DEFAULT_TOOLS = [
    calculator,
    get_weather,
    get_air_quality,

    get_ip_location,
    find_poi_nearby,
    geocode_location,

    exchange_rate,
    check_express,
    web_search,

    update_working_memory,
    clear_working_memory,

    remember_user_memory,
    forget_user_memory,

    github_search_repositories,
    github_get_repository,
    github_get_readme,
    github_get_contents,
    github_list_issues,
    github_list_pull_requests,
    github_list_commits,
    github_list_releases,
    github_list_contributors,
    github_get_languages,
    github_search_code,
    github_get_file_content,
    
    
]


def get_default_tools():
    return list(DEFAULT_TOOLS)