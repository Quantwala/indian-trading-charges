# Contributing

Thank you for helping improve Indian trading-cost estimates.

## Development

Use Python 3.9 or newer. From this repository:

```bash
python -m venv .venv
# Activate the virtual environment for your platform.
python -m pip install -e ".[dev]"
python -m pytest -q
```

For a rate change, cite the official exchange, government or broker source, state its effective date, and add a worked-example test. Keep calculation rounding explicit. Do not include account credentials, contract notes with personal details, or private trading data.

Open an issue before a major API change. Small corrections and tests can go directly into a pull request. Maintainers also synchronize rates with the Quantwala app and its parity tests.

## Community

Be respectful and constructive. Discuss code and evidence; avoid personal attacks, harassment and promotional spam. This project provides research estimates and does not give buy/sell recommendations.
