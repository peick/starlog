# Change Log

## 1.1.1 - unreleased

- Fixed a deadlock while shutting down the StatusHandler

## 1.1.0 - 2019-04-02

- Added LookbackHandler
- Added filtering / handling of specific loggers to multiprocess handlers
- Fixed `inc` function used in the StatusHandler

## 1.0.0 - 2019-03-21

- Available log handlers:
  - MultiprocessHandler
  - StatusHandler
  - ZmqHandler
