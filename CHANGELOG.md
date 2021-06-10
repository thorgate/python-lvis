# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2021-06-10

### Added

- Requests timing out in 2 minutes (can be overridden by subclassing the `ElvisClient`), 
  previously, there was no timeout and requests could hang for long time causing resource
  leaks
- This changelog

### Fixed

- ElvisModel was mutating its constructor argument, sometimes causing undesired data changes
- Getting transport orders now works in python 3

## [1.0.1] - 2017-01-05

### Added

- Release to PyPi

### Fixed

- Misc fixes related to automated deploys and quality checks

[1.1.0]: https://github.com/thorgate/python-lvis/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/thorgate/python-lvis/compare/1.0.0-rc3...v1.0.1
