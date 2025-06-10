# UK Bin Collection Data Add-on

This Home Assistant add-on integrates with your local council's website to fetch and display your bin collection
schedule. It creates sensors for your next collection and individual bin types, making it easy to track when different
bins need to be put out.

The add-on is powered by the [UK Bin Collection Data](https://github.com/robbrad/UKBinCollectionData) library, which
supports a wide range of UK councils. This underlying library does 99% of the heavy lifting but does only ships an
integration by default.

## Features

- Creates sensors for next collection and individual bin types
- Updates collection data automatically on a configurable schedule
- Supports a wide range of UK councils
- Provides human-readable dates and "days until" information
- Includes bin colors where provided by the council

## Configuration

```yaml
schedule: "0 */12 * * *"  # Cron schedule for updates (default: every 12 hours)
council: "YourCouncilName" # Your council ID from the supported councils list
postcode: "AB12 3CD"      # Your property's postcode
house_number: "42"        # Your house number or property name (if required)
uprn: ""                  # Your property's UPRN (if required)
council_override_url: ""  # Override the default council URL (if required)
```

### Option: `schedule`

The cron schedule for checking bin collection data. The default is every 12 hours (`0 */12 * * *`). You can use any valid cron expression to customize when the add-on checks for updates.

### Option: `council`

**Required:** The ID of your local council. This must match exactly with the council ID from the supported councils list. Visit the [UK Bin Collection Data Wiki](https://github.com/robbrad/UKBinCollectionData/wiki) to find your council's ID and specific requirements.

### Option: `postcode`

**Required:** Your property's postcode. Format may vary by council - check the wiki for specific requirements.

### Option: `house_number`

**Optional:** Your house number or property name. Required by some councils - check the wiki to see if your council needs this.

### Option: `uprn`

**Optional:** Your property's Unique Property Reference Number (UPRN). Required by some councils - check the wiki to see if your council needs this.

### Option: `council_override_url`

**Optional:** Override the default council URL. Required by some councils - check the wiki to see if your council needs this.

## Sensors

The add-on creates the following sensors:

- `sensor.bin_collection_next_collection`: Shows the next bin collection details
- `sensor.bin_collection_bin_[type]`: Individual sensors for each bin type (e.g., `sensor.bin_collection_bin_recycling`, `sensor.bin_collection_bin_garden_waste`)

Each sensor includes:
- State: Number of days until collection
- Attributes:
  - Type: The bin type
  - Color: The bin color (if provided by council)
  - Next collection date
  - Human-readable next collection date

## Supported Councils

For a complete list of supported councils and their specific requirements, please visit:
- [Supported Councils List](https://github.com/robbrad/UKBinCollectionData/wiki)
- [Council-specific Requirements](https://github.com/robbrad/UKBinCollectionData/wiki)

If your council isn't supported, you can request support or contribute by visiting the [UK Bin Collection Data repository](https://github.com/robbrad/UKBinCollectionData).

## Troubleshooting

1. Verify your council ID matches exactly with the supported councils list
2. Check if your council requires additional information (UPRN, URL override)
3. Ensure your postcode and house number format matches your council's requirements
4. Check the add-on logs for detailed error messages

## Support

- For add-on specific issues, please open an issue in our repository
- For council-specific issues or requests, please visit the [UK Bin Collection Data repository](https://github.com/robbrad/UKBinCollectionData)
