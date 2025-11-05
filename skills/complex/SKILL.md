# Trending Python Digest Skill

**Type:** Complex Skill (Code Execution)
**Version:** 1.0.0
**Status:** ✅ Active

## Description

Generates a curated newsletter digest of trending Python repositories from GitHub.

This skill demonstrates the **complex execution mode** by:
- Orchestrating multiple MCP tool calls
- Filtering and transforming data
- Aggregating results
- Producing formatted output

## Usage

### Command Line

```bash
# Basic usage (min 1000 stars)
python skills/complex/trending-python-digest.py

# Custom star threshold
python skills/complex/trending-python-digest.py --min-stars 500

# Limit number of items
python skills/complex/trending-python-digest.py --max-items 10

# Different output formats
python skills/complex/trending-python-digest.py --output-format json
python skills/complex/trending-python-digest.py --output-format html
```

### Programmatic Usage

```python
import subprocess
import json

result = subprocess.run(
    ['python', 'skills/complex/trending-python-digest.py', '--min-stars', '1000'],
    capture_output=True,
    text=True
)

digest = result.stdout
print(digest)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--min-stars` | int | 1000 | Minimum GitHub stars for repositories |
| `--max-items` | int | 5 | Maximum items in the digest |
| `--output-format` | str | markdown | Output format: markdown, json, or html |

## MCP Tools Used

1. **adk.watch_collect** - Collects trending repositories from GitHub
2. **adk.analyse_watch_report** - Analyzes repository data
3. **adk.curate_digest** - Generates formatted digest

## Output Example

### Markdown Format

```markdown
# 🐍 Trending Python Repositories Digest

*Generated: 2025-01-15*

## Top Repositories

### 1. transformers
**Stars:** 130,000
**Description:** State-of-the-art Machine Learning for PyTorch, TensorFlow, and JAX.

### 2. django
**Stars:** 78,000
**Description:** The Web framework for perfectionists with deadlines.

...
```

### JSON Format

```json
{
  "repositories": [
    {
      "name": "transformers",
      "stars": 130000,
      "language": "Python",
      "description": "State-of-the-art ML"
    }
  ]
}
```

## Execution Flow

```
┌──────────────────────────────────────┐
│  User runs skill                     │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Step 1: Collect repos via MCP      │
│  call_mcp('adk', 'watch_collect')   │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Step 2: Filter Python repos        │
│  (>= min_stars, language=Python)    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Step 3: Analyze top 10             │
│  call_mcp('adk', 'analyse_report')  │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Step 4: Generate digest            │
│  call_mcp('adk', 'curate_digest')   │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Output formatted digest             │
└──────────────────────────────────────┘
```

## Performance

- **Execution Time:** ~10-15 seconds
- **Token Usage:** ~2,000 tokens (vs ~100,000 without filtering)
- **Token Savings:** 98% compared to non-filtered approach

## Reusability

This skill can be:
- Scheduled to run daily/weekly
- Integrated into CI/CD pipelines
- Modified for other languages (JS, Rust, Go, etc.)
- Extended with email notifications

## Extending

To create a similar skill for a different language:

```bash
# Copy the skill
cp skills/complex/trending-python-digest.py skills/complex/trending-rust-digest.py

# Modify the filter
# Change: repo.get("language") == "Python"
# To:     repo.get("language") == "Rust"

# Update documentation
```

## Requirements

- SuperClaude with Hybrid MCP enabled
- ADK MCP server configured
- Python 3.8+

## Related Skills

- `skills/simple/check-github-trending.py` - Simple single-call version
- `skills/complex/multi-language-report.py` - Cross-language analysis (future)

## Version History

- **1.0.0** (2025-01-15) - Initial release
