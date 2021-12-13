# TVM Upstream CI

This repo holds the configuration as code for the CI of the upstream TVM project hosted on [github](https://github.com/apache/tvm). Specifically, this repository currently handles configuration of a private Jenkins instance, as well as a dedicated set of worker nodes--this Jenkins instance is located at [https://jenkins.tvm.octoml.ai](https://jenkins.tvm.octoml.ai)


# Components

## Docker

The 'jenkins' docker image contains the build tooling for the docker image that runs the head node. There are also containers for a datadog-agent for CI visibilty and another for a Jenkins agent (for the documentation stage of the TVM pipeline)

## Glossary of terms
| Term | Meaning | Notes |
--- | --- | ---
| Head (node) | This is the primary Jenkins server/process, it schedules jobs | |
| Worker (node) | These servers run as Jenkins clients and run test jobs according to configuration ||
| JJB | Jenkins Job Builder, a tool for setting jenkins jobs up through git-managed config files ||

## DNS Details

* OctoML DNS is hosted in Cloudflare.
* tvm.octoml.ai NS records in Cloudflare point to AWS/Route53 DNS records
* Route53 is used to create the `jenkins.tvm.octoml.ai` record and to validate that we own the domain for AWS certificate manager
