# Logging Configuration

This file controls all logging behavior for the KYC/AML Document Classifier application.

## Quick Settings

### Change Log Level
Edit `logging.level` in `logging_config.json`:
- `DEBUG` - Most verbose, all details
- `INFO` - Normal operations (recommended for production)
- `WARNING` - Only warnings and errors
- `ERROR` - Only errors
- `CRITICAL` - Only critical failures

Example:
```json
{
  "logging": {
    "level": "INFO"
  }
}
```

### Disable Console Logging
Set `logging.console.enabled` to `false`:
```json
{
  "logging": {
    "console": {
      "enabled": false
    }
  }
}
```

### Disable File Logging
Set `logging.file.enabled` to `false`:
```json
{
  "logging": {
    "file": {
      "enabled": false
    }
  }
}
```

## Configuration Reference

### Log Levels
- **DEBUG**: File operations, endpoint access details
- **INFO**: Application flow, predictions, requests (default)
- **WARNING**: Unexpected situations that don't stop execution
- **ERROR**: Failures that prevent specific operations
- **CRITICAL**: Severe errors that may stop the application

### Log Rotation
- **when**: `midnight` - Rotates at midnight every day
- **interval**: `1` - Rotate every 1 day
- **backup_count**: `30` - Keep 30 days of logs, auto-delete older files
- **encoding**: `utf-8` - Support for all characters

### Log File Naming
- Pattern: `application_{date}.log`
- Example: `application_2025_12_11.log`
- Rotated files: `application_2025_12_11.log.2025_12_10`

## Examples

### Development Environment (Verbose Logging)
```json
{
  "logging": {
    "level": "DEBUG",
    "console": {
      "enabled": true,
      "level": "DEBUG"
    },
    "file": {
      "enabled": true,
      "level": "DEBUG"
    }
  }
}
```

### Production Environment (Clean Console)
```json
{
  "logging": {
    "level": "INFO",
    "console": {
      "enabled": true,
      "level": "WARNING"
    },
    "file": {
      "enabled": true,
      "level": "INFO"
    }
  }
}
```

### Debugging Issues (Maximum Detail)
```json
{
  "logging": {
    "level": "DEBUG",
    "console": {
      "enabled": true,
      "level": "DEBUG"
    },
    "file": {
      "enabled": true,
      "level": "DEBUG"
    },
    "rotation": {
      "backup_count": 7
    }
  }
}
```

### Minimal Logging (Performance Critical)
```json
{
  "logging": {
    "level": "ERROR",
    "console": {
      "enabled": false
    },
    "file": {
      "enabled": true,
      "level": "ERROR"
    }
  }
}
```

## Log Cleanup

Old log files are automatically deleted after 30 days (configurable via `backup_count`).

To change retention period:
```json
{
  "logging": {
    "rotation": {
      "backup_count": 7  // Keep only 7 days
    }
  }
}
```

## Log Format

Default format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Example output:
```
2025-12-11 10:30:15 - __main__ - INFO - Prediction successful - File: aadhar.jpg, Class: aadhar, Confidence: 0.9823
```

### Available Format Variables
- `%(asctime)s` - Timestamp
- `%(name)s` - Logger name
- `%(levelname)s` - Log level (INFO, ERROR, etc.)
- `%(message)s` - Log message
- `%(filename)s` - Source file name
- `%(funcName)s` - Function name
- `%(lineno)d` - Line number

### Custom Format Example
```json
{
  "logging": {
    "format": "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"
  }
}
```

## Troubleshooting

### Logs not appearing
1. Check `logging.file.enabled` is `true`
2. Verify `logs/` directory exists and is writable
3. Ensure log level isn't too restrictive (try `DEBUG`)

### Too many log files
1. Reduce `rotation.backup_count`
2. Or manually delete old logs from `logs/` directory

### Console output too verbose
1. Set `logging.console.level` to `WARNING` or `ERROR`
2. Or disable with `logging.console.enabled: false`

### Need different levels for file vs console
File and console can have independent log levels:
```json
{
  "logging": {
    "console": {
      "level": "WARNING"  // Only warnings in console
    },
    "file": {
      "level": "DEBUG"    // Everything in file
    }
  }
}
```

## Best Practices

1. **Production**: Use `INFO` level, keep 30 days of logs
2. **Development**: Use `DEBUG` level, 7 days is enough
3. **Troubleshooting**: Temporarily enable `DEBUG`, then revert
4. **Performance**: If logging impacts performance, reduce to `WARNING`
5. **Storage**: Monitor disk space if keeping many days of logs

## Applying Changes

After modifying `logging_config.json`, restart the application:
```bash
# Stop the server (Ctrl+C)
# Start again
uvicorn api.main:app --reload
```

Changes take effect immediately on restart.
