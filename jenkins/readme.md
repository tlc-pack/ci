## Components

### Docker

The 'jenkins' docker image contains the build tooling for the docker image that runs the head node. There is also a container for a Jenkins agent (for the documentation stage of the TVM pipeline)

### Glossary of terms
| Term | Meaning | Notes |
--- | --- | ---
| Head (node) | This is the primary Jenkins server/process, it schedules jobs | |
| Worker (node) | These servers run as Jenkins clients and run test jobs according to configuration ||
| JJB | Jenkins Job Builder, a tool for setting jenkins jobs up through git-managed config files ||
