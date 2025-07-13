#!/usr/bin/env python3
"""
BibTeX Google Scholar Checker
Automatically checks the existence of papers in a .bibtex file using Google Scholar.
"""

import bibtexparser
import requests
from bs4 import BeautifulSoup
import time
import re
import argparse
import sys
from urllib.parse import quote_plus
import random

class GoogleScholarChecker:
    def __init__(self, delay_range=(2, 5)):
        """
        Initialize the checker with configurable delay to avoid rate limiting.
        
        Args:
            delay_range: Tuple of (min_delay, max_delay) in seconds between requests
        """
        self.delay_range = delay_range
        self.session = requests.Session()
        # Set a realistic user agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def clean_text(self, text):
        """Clean text for better search matching."""
        if not text:
            return ""
        # Remove special characters and normalize whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join(text.split())
        return text.strip()
    
    def build_search_query(self, entry):
        """
        Build a Google Scholar search query from a BibTeX entry.
        
        Args:
            entry: BibTeX entry dictionary
            
        Returns:
            str: Search query string
        """
        query_parts = []
        
        # Add title (most important)
        if 'title' in entry:
            title = self.clean_text(entry['title'])
            query_parts.append(f'"{title}"')
        
        # Add first author
        if 'author' in entry:
            authors = entry['author'].split(' and ')
            if authors:
                first_author = authors[0].strip()
                # Extract last name
                name_parts = first_author.split(',')
                if len(name_parts) > 1:
                    last_name = name_parts[0].strip()
                else:
                    name_parts = first_author.split()
                    last_name = name_parts[-1] if name_parts else ""
                
                if last_name:
                    query_parts.append(f'author:"{last_name}"')
        
        # Add year if available
        if 'year' in entry:
            query_parts.append(entry['year'])
        
        return ' '.join(query_parts)
    
    def search_google_scholar(self, query):
        """
        Search Google Scholar for a given query.
        
        Args:
            query: Search query string
            
        Returns:
            tuple: (success: bool, num_results: int, error_msg: str)
        """
        try:
            url = f"https://scholar.google.com/scholar?q={quote_plus(query)}"
            
            # Add random delay to avoid rate limiting
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 429:
                return False, 0, "Rate limited by Google Scholar"
            elif response.status_code != 200:
                return False, 0, f"HTTP {response.status_code}"
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if we got results
            result_divs = soup.find_all('div', {'class': 'gs_r gs_or gs_scl'}) or \
                         soup.find_all('div', {'class': 'gs_ri'})
            
            # Check for "no results" message
            no_results = soup.find('div', string=re.compile(r'did not match any articles', re.I))
            
            if no_results or len(result_divs) == 0:
                return True, 0, ""
            
            return True, len(result_divs), ""
            
        except requests.RequestException as e:
            return False, 0, f"Network error: {str(e)}"
        except Exception as e:
            return False, 0, f"Error: {str(e)}"
    
    def check_bibtex_file(self, bibtex_file_path, output_file=None):
        """
        Check all entries in a BibTeX file against Google Scholar.
        
        Args:
            bibtex_file_path: Path to the BibTeX file
            output_file: Optional path to save results
            
        Returns:
            list: List of dictionaries containing check results
        """
        print(f"Loading BibTeX file: {bibtex_file_path}")
        
        try:
            with open(bibtex_file_path, 'r', encoding='utf-8') as bibtex_file:
                bib_database = bibtexparser.load(bibtex_file)
        except Exception as e:
            print(f"Error loading BibTeX file: {e}")
            return []
        
        entries = bib_database.entries
        print(f"Found {len(entries)} entries to check")
        
        results = []
        
        for i, entry in enumerate(entries, 1):
            entry_id = entry.get('ID', f'entry_{i}')
            title = entry.get('title', 'No title')
            
            print(f"\n[{i}/{len(entries)}] Checking: {entry_id}")
            print(f"Title: {title}")
            
            # Build search query
            query = self.build_search_query(entry)
            print(f"Query: {query}")
            
            # Search Google Scholar
            success, num_results, error_msg = self.search_google_scholar(query)
            
            result = {
                'entry_id': entry_id,
                'title': title,
                'query': query,
                'found': success and num_results > 0,
                'num_results': num_results if success else 0,
                'error': error_msg,
                'success': success
            }
            
            results.append(result)
            
            if success:
                status = "✓ FOUND" if num_results > 0 else "✗ NOT FOUND"
                print(f"Status: {status} ({num_results} results)")
            else:
                print(f"Status: ERROR - {error_msg}")
        
        # Save results if output file specified
        if output_file:
            self.save_results(results, output_file)
        
        return results
    
    def save_results(self, results, output_file):
        """Save results to a file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("BibTeX Google Scholar Check Results\n")
                f.write("=" * 50 + "\n\n")
                
                found_count = sum(1 for r in results if r['found'])
                total_count = len(results)
                
                f.write(f"Summary: {found_count}/{total_count} entries found\n\n")
                
                for result in results:
                    f.write(f"Entry ID: {result['entry_id']}\n")
                    f.write(f"Title: {result['title']}\n")
                    f.write(f"Query: {result['query']}\n")
                    
                    if result['success']:
                        status = "FOUND" if result['found'] else "NOT FOUND"
                        f.write(f"Status: {status} ({result['num_results']} results)\n")
                    else:
                        f.write(f"Status: ERROR - {result['error']}\n")
                    
                    f.write("-" * 30 + "\n\n")
            
            print(f"\nResults saved to: {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def print_summary(self, results):
        """Print a summary of the check results."""
        total = len(results)
        found = sum(1 for r in results if r['found'])
        errors = sum(1 for r in results if not r['success'])
        
        print(f"\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Total entries checked: {total}")
        print(f"Found in Google Scholar: {found}")
        print(f"Not found: {total - found - errors}")
        print(f"Errors: {errors}")
        print(f"Success rate: {found/total*100:.1f}%" if total > 0 else "N/A")
        
        if errors > 0:
            print(f"\nEntries with errors:")
            for result in results:
                if not result['success']:
                    print(f"  - {result['entry_id']}: {result['error']}")

def main():
    parser = argparse.ArgumentParser(description='Check BibTeX entries against Google Scholar')
    parser.add_argument('bibtex_file', help='Path to the BibTeX file')
    parser.add_argument('-o', '--output', help='Output file to save results')
    parser.add_argument('--min-delay', type=float, default=2.0, 
                       help='Minimum delay between requests (seconds)')
    parser.add_argument('--max-delay', type=float, default=5.0,
                       help='Maximum delay between requests (seconds)')
    
    args = parser.parse_args()
    
    if not args.bibtex_file:
        print("Error: Please provide a BibTeX file path")
        sys.exit(1)
    
    # Create checker instance
    checker = GoogleScholarChecker(delay_range=(args.min_delay, args.max_delay))
    
    print("BibTeX Google Scholar Checker")
    print("=" * 50)
    print("This tool will check each entry in your BibTeX file against Google Scholar.")
    print("Please be patient as we need to add delays to avoid rate limiting.")
    print(f"Using delay range: {args.min_delay}-{args.max_delay} seconds between requests\n")
    
    # Check the BibTeX file
    results = checker.check_bibtex_file(args.bibtex_file, args.output)
    
    # Print summary
    checker.print_summary(results)

if __name__ == "__main__":
    main()
