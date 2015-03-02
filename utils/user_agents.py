import random
# List of available user agents to user

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0"

# TODO: Separate mobile agents from regular ones
USER_AGENTS = []
MOBILE_USER_AGENTS = []
def random_agent():
    random.choice(USER_AGENTS)