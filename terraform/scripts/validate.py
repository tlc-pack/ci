import sys
import os
from github import Github

def check_is_verified(token, repository):
  client = Github(login_or_token=token)
  repo = client.get_repo(repository)
  latest_commit = repo.get_commit("HEAD")
  return latest_commit.commit.raw_data["verification"]["verified"]
  
if __name__ == '__main__' :
  with open('DEPLOYERS.md') as file:
    deployers = [i.strip() for i in file]

  token = os.environ['GITHUB_TOKEN']
  working_repository = os.environ['PR_REPO_FULL_NAME']

  is_verified = check_is_verified(token, working_repository)
  is_fork = not os.environ['GITHUB_REPOSITORY'] == working_repository
  is_deployer = os.environ['EMAIL'] in deployers

  valid_workflow = is_verified and ((is_fork and is_deployer and (os.environ['GITHUB_EVENT_NAME'] == 'pull_request_target')) or (not is_fork and (os.environ['GITHUB_EVENT_NAME'] == 'pull_request')))
  print(valid_workflow)
