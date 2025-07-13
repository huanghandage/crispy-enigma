# BibTeX Google Scholar Checker

A Python tool to automatically check whether the papers listed in a `.bib` BibTeX file can be found on Google Scholar.

---

## Features

- Check all BibTeX entries against Google Scholar
- Search by title, author, and year
- Summary report of found / not found entries
- Optional save-to-file report
- Configurable delay to avoid rate limiting
- Realistic user-agent to reduce blocking risks

---

## Quick Start Guide

### Installation

Install dependencies:

```

pip install bibtexparser beautifulsoup4 requests

```

Or using a `requirements.txt` file:

```

pip install -r requirements.txt

```

### Basic Usage

Run on a BibTeX file:

```

python bibtex\_scholar\_checker.py my\_papers.bib

```

Save results to an output file:

```

python bibtex\_scholar\_checker.py my\_papers.bib -o results.txt

```

---

## Detailed Usage Examples

Check with default delay settings:

```

python bibtex\_scholar\_checker.py my\_papers.bib

```

Check with custom delay settings (to avoid rate limits):

```

python bibtex\_scholar\_checker.py my\_papers.bib --min-delay 3 --max-delay 8

```

Sample console output:

```

\[1/10] Checking: paper\_1
Title: Efficient Quantum Algorithms
Query: "Efficient Quantum Algorithms" author:"Grover" 1996
Status: ✓ FOUND (5 results)

Summary:
Total entries checked: 10
Found in Google Scholar: 9
Not found: 1
Errors: 0
Success rate: 90.0%

```

---

## Configuration Options

| Option            | Description                               | Default  |
|-------------------|-----------------------------------------|----------|
| `-o`, `--output` | Output file to save results             | None     |
| `--min-delay`    | Minimum delay between requests (sec)    | 2.0      |
| `--max-delay`    | Maximum delay between requests (sec)    | 5.0      |

---

## Technical Explanation

This tool works as follows:

1. **Input Parsing**: Reads the provided `.bib` BibTeX file using `bibtexparser`.
2. **Query Construction**: For each entry, it builds a search query using:
   - Cleaned title (quoted),
   - First author's last name,
   - Publication year (if available).
3. **Request Handling**: Makes an HTTP GET request to Google Scholar using a session with a realistic browser user-agent.
4. **Delay Management**: Waits for a random interval between requests (within specified delay range) to avoid triggering Google Scholar’s rate limits.
5. **Result Parsing**: Uses BeautifulSoup to parse the returned HTML and checks for search result blocks or “no results” messages.
6. **Reporting**: Collects results for all entries, summarizes findings, and optionally writes them to an output file.

---

## Requirements and Dependencies

- Python >= 3.7

### Python Dependencies

- `bibtexparser`
- `beautifulsoup4`
- `requests`

To install dependencies, run:

```

pip install -r requirements.txt

```

---

