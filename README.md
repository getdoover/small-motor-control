# Small Motor Control

<!-- ![Doover Logo](https://doover.com/wp-content/uploads/Doover-Logo-Landscape-Navy-padded-small.png) -->
<img src="https://doover.com/wp-content/uploads/Doover-Logo-Landscape-Navy-padded-small.png" alt="App Icon" style="max-width: 300px;">

**Control small diesel and petrol motors with ignition, starter, and emergency stop functionality.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/getdoover/small-motor-control)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/getdoover/small-motor-control/blob/main/LICENSE)

[Configuration](#configuration) | [Developer](https://github.com/getdoover/small-motor-control/blob/main/DEVELOPMENT.md) | [Need Help?](#need-help)

<br/>

## Overview

Control small diesel and petrol motors with ignition, starter, and emergency stop functionality.

<br/>

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| **Display Name** | Display name for the motor | `Engine` |
| **Ignition In Pin** | Pin to detect ignition state | `4` |
| **Starter Pin** | Pin to control starter relay | `6` |
| **Horn Pin** | Pin to control horn relay | `7` |

<br/>
## Integrations

### Tags

This app exposes the following tags for integration with other apps:

| Tag | Description |
|-----|-------------|
| `state` | Current state (ignition_off, running_user, running_auto, etc.) |
| `run_request_reason` | Reason for current run request from another app |

<br/>
This app works seamlessly with:

- **Platform Interface**: Core Doover platform component


<br/>

## Need Help?

- Email: support@doover.com
- [Community Forum](https://doover.com/community)
- [Full Documentation](https://docs.doover.com)
- [Developer Documentation](https://github.com/getdoover/small-motor-control/blob/main/DEVELOPMENT.md)

<br/>

## Version History

### v1.0.0 (Current)
- Initial release

<br/>

## License

This app is licensed under the [Apache License 2.0](https://github.com/getdoover/small-motor-control/blob/main/LICENSE).
