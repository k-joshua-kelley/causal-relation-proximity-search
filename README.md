# Causal Relation Proximity Search: A Tool for Extracting Cause-Effect Relationships from PDF Documents

This script extracts observations from PDF documents based on specified causal and topic terms, optionally excluding sentences containing exclusion terms. It outputs both the core sentence containing at 1+ causal terms and 1+ topic terms as well as a short context window (±2 surrounding sentences) to a CSV file for human analysis.

## Features

* Reads text from PDF files.
* Filters for sentences containing 1+ causal term(s) and 1+ topic term(s).
* Supports exclusion of sentences with specified terms.
* Outputs a list of 5-sentence substrings (called observations) from the provided PDFs.
* Displays a progress bar while processing.

## Usage
```
python causal-relation-proximity-search.py path_to_pdfs path_to_causal_terms path_to_topic_terms output_filename [-xc path_to_exclude_causal_terms] [-xt path_to_exclude_topic_terms]
```

## Positional Arguments

| Argument | Description |
|----|----|
| `path_to_pdfs` | Path to the directory containing PDF files to be processed. |
| `path_to_causal_terms` | Path to a TXT file containing causal search terms to include (see Note 1). |
| `path_to_topic_terms` | Path to a TXT file containing topic search terms to include (see Note 1). |
| `output_filename` | Output CSV filename (without the `.csv` extension).

**Note 1:** Input files should contain one term per line. Terms may be plain text or regular expressions (compatible with Python’s `re` library), and may include whitespace.

## Optional Arguments

| Argument | Description |
|----|----|
| `-xc`, `--exclude_causal_terms` | Path to a TXT file containing causal terms to exclude (see Notes 1 & 2).  |
| `-xt`, `--exclude_topic_terms` | Path to a TXT file containing topic terms to exclude (see Notes 1 & 2).  |

**Note 2:** Sentences containing terms from the files specified via `-xc` or `-xt` will be excluded, even if they also contain terms from `path_to_causal_terms` and `path_to_topic_terms`.

## Output

The script generates a `.csv` file with the following columns:

* Filename: Name of the processed PDF file.
* Full Observation: A 5-sentence context window centered around the core sentence.
* Core Sentence: A single sentence contains 1+ causal term(s) and 1+ topic term(s).

## Dependencies

* `PyPDF2`
* `tqdm`

Install with:
```
pip install PyPDF2 tqdm
```

## Additional Notes
* Sentence splitting is done using `. ` as the delimiter.
* The output may contain non-alphanumeric symbols as artifacts from the PDF-to-text conversion performed by `PyPDF2`. This is a known limitation due to inconsistencies in PDF formatting.
* Since this is a simple proximity search (rather than a large language model), the output should be reviewed by a human to ensure relevance and accuracy.

## Licence

This tool is provided as-is for academic and other non-commercial use. Modify freely with attribution.
