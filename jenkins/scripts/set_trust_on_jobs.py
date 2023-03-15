import argparse
import os

import jenkins

USER = os.environ["JENKINS_USER"]
PW = os.environ["JENKINS_PW"]


def add_fork_trust_plugin(xml: str) -> str:
    nobody = '<trust class="org.jenkinsci.plugins.github_branch_source.ForkPullRequestDiscoveryTrait$TrustNobody"/>'
    some_people = (
        '<trust class="org.jenkinsci.plugins.githubScmTraitNotificationContext.'
        'ForkPullRequestDiscoveryTrait$TrustSomePeople" plugin="github-trust-hardcoded-authors@12.0"/>'
    )
    return xml.replace(nobody, some_people)


def test():
    with open("out.xml") as f:
        content = f.read()

    content = add_fork_trust_plugin(content)

    with open("out.xml", "w") as f:
        f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Set the job config XML for octoml- and tvm- jobs in Jenkins"
    )
    parser.parse_args()

    server = jenkins.Jenkins("https://ci.tlcpack.ai", username=USER, password=PW)  # type: ignore[attr-defined]
    jobs = server.get_jobs()

    to_update = []
    for job in jobs:
        name = job["fullname"]
        if name.startswith("tvm-") or name.startswith("octoml-"):
            to_update.append(name)

    for name in to_update:
        print(f"Updating fork trust plugin for {name}", end="")
        config = server.get_job_config(name)
        new_config = add_fork_trust_plugin(config)
        if config != new_config:
            r = server.reconfig_job(name, new_config)

        print("  done")
