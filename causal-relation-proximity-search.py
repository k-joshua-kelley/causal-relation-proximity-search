import os
import re
import PyPDF2
import csv
import argparse
from tqdm import tqdm


def pdf2text(filepath):
    """
    Extracts text from all pages of a PDF file and returns a single cleaned-up string.

    Args:
        filepath (str): Path to the PDF file.

    Returns:
        str: Cleaned text extracted from the PDF.
    """
    with open(filepath, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        contents = ''
        for i in range(len(pdf_reader.pages)):
            # Remove excessive whitespace and strip leading/trailing spaces
            contents += re.sub(r'\s+', ' ', pdf_reader.pages[i].extract_text()).strip()
        return contents


def read_terms(file_path):
    """
    Reads a list of terms from a file, one term per line.

    Args:
        file_path (str): Path to the term file.

    Returns:
        list of str: List of terms.
    """
    return open(file_path, 'r').read().splitlines()


def filter_sentences(sentences, terms, case_sensitive=True):
    """
    Filters sentences that contain at least one of the provided terms.

    Args:
        sentences (list of str): Sentences to filter.
        terms (list of str): List of regex terms to match.
        case_sensitive (bool): Whether the match should be case-sensitive.

    Returns:
        list of str: Sentences that match the terms.
    """
    if case_sensitive:
        return [sentence for sentence in sentences if any(re.search(term, sentence) for term in terms)]
    else:
        return [sentence for sentence in sentences if any(re.search(term, sentence, re.IGNORECASE) for term in terms)]


def exclude_sentences(sentences, terms, case_sensitive=True):
    """
    Excludes sentences that contain any of the provided terms.

    Args:
        sentences (list of str): Sentences to filter.
        terms (list of str): List of regex terms to match for exclusion.
        case_sensitive (bool): Whether the match should be case-sensitive.

    Returns:
        list of str: Sentences that do not match the exclusion terms.
    """
    if case_sensitive:
        return [sentence for sentence in sentences if not any(re.search(term, sentence) for term in terms)]
    else:
        return [sentence for sentence in sentences if
                not any(re.search(term, sentence, re.IGNORECASE) for term in terms)]


def process_text(text, causal_terms, topic_terms, xt_terms=None, xc_terms=None):
    """
    Extracts context windows around core sentences that contain both topic and causal terms.

    Args:
        text (str): The full text to search within.
        causal_terms (list of str): Causal keywords to identify relevant sentences.
        topic_terms (list of str): Topic keywords to identify relevant sentences.
        xt_terms (list of str, optional): Topic exclusion terms.
        xc_terms (list of str, optional): Causal exclusion terms.

    Returns:
        tuple:
            - full_obs (list of str): Contextual windows around each relevant sentence.
            - core_sentences (list of str): Sentences that met both topic and causal conditions.
    """
    # Split into individual sentences and add a period for formatting
    all_sentences = [sentence.strip() + '.' for sentence in text.split('. ') if sentence]

    # Apply inclusion and exclusion filters
    core_sentences = all_sentences
    core_sentences = filter_sentences(core_sentences, topic_terms, case_sensitive=False)
    core_sentences = filter_sentences(core_sentences, causal_terms, case_sensitive=True)
    if xt_terms is not None:
        core_sentences = exclude_sentences(core_sentences, xt_terms, case_sensitive=False)
    if xc_terms is not None:
        core_sentences = exclude_sentences(core_sentences, xc_terms, case_sensitive=True)

    full_obs = []
    idx = -1  # Tracks last index used, to avoid finding duplicate sentence positions
    for sentence in core_sentences:
        idx = all_sentences.index(sentence, idx + 1)  # Find index of current sentence

        # Extract surrounding window (2 before, 2 after)
        start_idx_to_use = max(0, idx - 2)
        end_idx_to_use = min(len(all_sentences), idx + 3)

        surrounding_sentences = all_sentences[start_idx_to_use:end_idx_to_use]
        full_obs.append(" ".join(surrounding_sentences).strip())

    return full_obs, core_sentences


def get_args():
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_pdfs', type=str, help='Path to directory containing PDF documents to process.')
    parser.add_argument('path_to_causal_terms', type=str, help='Path to file containing causal search terms.')
    parser.add_argument('path_to_topic_terms', type=str, help='Path to file containing topic search terms.')
    parser.add_argument('output_filename', type=str,
                        help='Filename for output data, excluding extension.  Output will be written as a .csv file.')
    parser.add_argument('-xc', '--exclude_causal_terms', type=str,
                        help='Path to file containing causal terms to exclude; i.e., sentences containing these terms will be excluded from the dataset.')
    parser.add_argument('-xt', '--exclude_topic_terms', type=str,
                        help='Path to file containing topic terms to exclude; i.e., sentences containing these terms will be excluded from the dataset.')
    return parser.parse_args()


if __name__ == '__main__':
    # Parse CLI arguments
    args = get_args()
    directory = args.path_to_pdfs
    causal_terms = read_terms(args.path_to_causal_terms)
    topic_terms = read_terms(args.path_to_topic_terms)
    output_csv = args.output_filename + '.csv'
    xt_terms = read_terms(args.exclude_topic_terms) if args.exclude_topic_terms else None
    xc_terms = read_terms(args.exclude_causal_terms) if args.exclude_causal_terms else None

    file_list = os.listdir(directory)
    progress_bar = tqdm(total=len(file_list), desc="Processing")

    # Write results to CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Full Observation", "Core Sentence"])

        for filename in file_list:
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and (
                    filename.endswith('.pdf') or filename.endswith('.PDF')):  # Ensure only PDF files are processed
                # Extract relevant sentences and their surrounding context
                full_obs_list, core_sentence_list = process_text(pdf2text(file_path), causal_terms, topic_terms,
                                                                 xt_terms=xt_terms, xc_terms=xc_terms)
                # Write each observation and core sentence to CSV
                for full_obs, core_sentence in zip(full_obs_list, core_sentence_list):
                    writer.writerow([filename, full_obs, core_sentence])
            else:
                print(f'{filename} was not processed either because (1) file does not exist or (2) file is not a PDF.')
            progress_bar.update(1)
