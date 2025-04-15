# Welcome to Jumpstarter

```{eval-rst}
.. image:: https://img.shields.io/badge/GitHub-Repository-blue?logo=github
   :target: https://github.com/jumpstarter-dev/jumpstarter
   :alt: GitHub Repository

.. image:: https://img.shields.io/badge/PyPI-Packages-blue?logo=pypi
   :target: https://pypi.org/project/jumpstarter/
   :alt: Python Packages

.. image:: https://img.shields.io/matrix/jumpstarter%3Amatrix.org?color=blue
   :target: https://matrix.to/#/#jumpstarter:matrix.org
   :alt: Matrix Chat

.. image:: https://img.shields.io/badge/Etherpad-Notes-blue?logo=etherpad
   :target: https://etherpad.jumpstarter.dev/pad-lister
   :alt: Etherpad Notes

.. image:: https://img.shields.io/badge/Weekly%20Meeting-Google%20Meet-blue?logo=google-meet
   :target: https://meet.google.com/gzd-hhbd-hpu
   :alt: Weekly Meeting
```

Jumpstarter is a free and open source testing tool that bridges the gap between
development workflows and deployment environments. It enables you to test your
software stack consistently across both real hardware and virtual environments
using cloud native principles. By decoupling your target devices (physical or
virtual) from test runners, development machines, and CI/CD pipelines,
Jumpstarter allows you to use the same automation scripts everywhere - like a
*Makefile* for device automation.

```{include} ../../README.md
:start-after: "## Highlights"
:end-before: "##"
```

Now that you understand what makes Jumpstarter powerful, let's explore how to
get started with the tool. The following learning paths will guide you through
the documentation based on your specific needs and experience level.

## Learning Paths

### Getting Started

If you are new to Jumpstarter, start here to understand the core concepts and
set up your environment:
- [What is Jumpstarter?](introduction/index.md) - An overview of Jumpstarter's
  key concepts and components
- [Installation Guide](installation/index.md) - Step-by-step instructions to
  install Jumpstarter
- [Setting Up Your First Local
  Exporter](getting-started/setup-local-exporter.md) - Guide to connect your
  first device for testing

### Using Jumpstarter for Testing

For testers and developers looking to automate device testing with Jumpstarter:
- [Setting Up Client & Exporter](getting-started/setup-exporter-client.md) - How
  to configure your testing environment
- [Command Line Interface](cli/index.md) - Detailed guide on using the CLI for
  automation
- [Example
  Projects](https://github.com/jumpstarter-dev/jumpstarter/tree/main/examples) -
  Real-world examples of testing with Jumpstarter

### Extending Jumpstarter

Developers and contributors interested in extending Jumpstarter's capabilities:
- [Architecture Overview](introduction/index.md#core-components) - High-level
  overview of Jumpstarter's internal architecture
- [Driver Development](introduction/drivers.md) - Guide to developing custom
  drivers for new hardware
- [API Reference](api-reference/index.md) - Comprehensive reference for
  Jumpstarter's APIs
- [Contributing Guide](contributing.md) - Guidelines and best practices for
  contributing to the project

### Enterprise & Team Use

For organizations looking to deploy Jumpstarter at scale:
- [Distributed Mode Setup](installation/service/index.md) - Guide to deploying
  the Kubernetes-based controller
- [Solution Architecture](solution-architecture.md) - Reference architectures
  for complex environments
- [Managing Lab Resources](introduction/service.md) - Best practices for
  coordinating access to shared hardware

```{toctree}
:maxdepth: 3
:hidden:

introduction/index.md
installation/index.md
getting-started/index.md
cli/index.md
config/index.md
solution-architecture.md
contributing.md
glossary.md
api-reference/index.md
```