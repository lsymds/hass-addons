# UK Bin Collection Data Add-on

A Home Assistant add-on that integrates with UK council websites to fetch and display bin collection schedules. This
add-on leverages the [UK Bin Collection Data](https://github.com/robbrad/UKBinCollectionData) library to create sensors
for next collections and individual bin types, making it easy to track when different bins need to be put out.

## Overview

This add-on:
- Creates sensors for next collection and individual bin types
- Updates collection data automatically on a configurable schedule
- Supports a wide range of UK councils
- Runs Selenium within the add-on for councils that make scraping difficult.

## Documentation

For detailed information about installation, configuration, and usage, please see the [add-on documentation](DOCS.md).

## License

GNU GPL v3
