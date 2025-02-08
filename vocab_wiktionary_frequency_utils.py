from bs4 import BeautifulSoup
from cachier import cachier
import requests
import random
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import pyplot as plt

from vocab_llm_utils import (
    GREEK_WIKTIONARY_FREQUENCY_LIST_URL,
    quick_search_for_wordform,
    metadata_for_lemma_full,
    get_language_name,
)


def wiktionary_cleanup(html: str):
    """
    Throw away unimportant parts of the HTML.

    This was useful for getting the frequency list from Wiktionary.
    """

    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Remove footer and head
    for tag in soup.find_all(["footer", "head"]):
        tag.decompose()

    # Remove all title (i.e. tooltip) attributes
    for tag in soup.find_all(attrs={"title": True}):
        del tag["title"]

    # Return the cleaned HTML
    html_cleaned = str(soup)
    return html_cleaned


def extract_word_url_count_from_wiktionary_frequency_list(
    html: str, include_missing_links: bool = True
) -> list[dict]:
    """
    <div class="derivedterms ul-column-count" data-column-count="5">
    <ul>
        <li><a href="/wiki/%CE%BE%CE%AD%CF%81%CE%B5%CE%B9%CF%82#Greek">ξέρεις</a> 258455</li>
        ...
    </ul>
    </div>

    ->

    [
        {"word": "ξέρεις", "count": 258455, "url": "/wiki/%CE%BE%CE%AD%CF%81%CE%B5%CE%B9%CF%82#Greek"},
        ...
    ]
    """
    soup = BeautifulSoup(html, "html.parser")
    words_d = []
    # Find the div with class="derivedterms"
    derived_terms_div = soup.find("div", class_="derivedterms")
    assert derived_terms_div is not None, "Derived terms div not found"
    for li in derived_terms_div.find_all("li"):  # type: ignore
        a = li.find("a")
        if not include_missing_links and a is None:
            continue
        word = a.text.strip()
        count = int(li.text.split()[1])
        url = a["href"]
        word_d = {"word": word, "count": count, "url": url}
        words_d.append(word_d)
    return words_d


def get_greek_wiktionary_frequency_list(
    url: str = GREEK_WIKTIONARY_FREQUENCY_LIST_URL,
):
    response = requests.get(url)
    response.raise_for_status()

    html = response.text
    # html = wiktionary_cleanup(html)
    words_d = extract_word_url_count_from_wiktionary_frequency_list(html)

    # out, extra = generate_gpt_from_template(
    #     "get_greek_wiktionary_frequency_list",
    #     {"html": html},
    #     True,
    #     max_tokens=8192,
    #     verbose=0,
    # )
    # return out
    # return html, None
    return words_d, None


@cachier()
def get_greek_wiktionary_frequency_list_cached(
    url: str = GREEK_WIKTIONARY_FREQUENCY_LIST_URL,
):
    out, extra = get_greek_wiktionary_frequency_list(url)
    return out


def get_ai_data_for_word(
    word: str, count: int, target_language_code: str, verbose: int = 1
) -> dict:
    """
    Get AI analysis data for a single word.

    Args:
        word: The word to analyze
        count: The frequency count from Wiktionary
        target_language_code: ISO language code (e.g. "el" for Greek)
        verbose: Verbosity level

    Returns:
        Dictionary containing:
            - word: original word
            - count: wiktionary frequency count
            - wordform_data: AI data for the wordform
            - lemma_data: AI data for the lemma (if found)
            - error: error message if any
    """
    result = {
        "word": word,
        "count": count,
        "wordform_data": None,
        "lemma_data": None,
        "error": None,
    }

    try:
        # Get AI data for wordform
        wordform_data, _ = quick_search_for_wordform(
            word, target_language_code, verbose=verbose
        )
        result["wordform_data"] = wordform_data

        # If we found a lemma, get its full metadata
        if "lemma" in wordform_data:
            lemma = wordform_data["lemma"]
            target_language_name = get_language_name(target_language_code)
            lemma_data, _ = metadata_for_lemma_full(
                lemma=lemma, target_language_name=target_language_name, verbose=verbose
            )
            result["lemma_data"] = lemma_data

    except Exception as e:
        result["error"] = str(e)
        if verbose >= 1:
            print(f"Error processing {word}: {e}")

    return result


def analyze_word_sample(
    words_data: list[dict],
    sample_size: int,
    target_language_code: str,
    random_seed: int | None = None,
    verbose: int = 1,
) -> list[dict]:
    """
    Analyze a random sample of words using the AI.

    Args:
        words_data: List of word dictionaries from Wiktionary
        sample_size: Number of words to sample
        target_language_code: ISO language code
        random_seed: Optional random seed for reproducibility
        verbose: Verbosity level

    Returns:
        List of result dictionaries containing AI analysis data
    """
    if random_seed is not None:
        random.seed(random_seed)

    # Sample words
    sampled_words = random.sample(words_data, sample_size)

    # Analyze each word
    results = []
    for word_data in sampled_words:
        word = word_data["word"]
        count = word_data["count"]

        if verbose >= 1:
            print(f"\nProcessing word: {word} (count: {count})")

        result = get_ai_data_for_word(
            word, count, target_language_code, verbose=verbose
        )
        results.append(result)

    return results


def plot_frequency_vs_commonality(
    results: list[dict],
    figsize: tuple[int, int] = (12, 8),
    verbose: int = 1,
) -> tuple[plt.Figure, plt.Axes]:  # type: ignore
    """
    Create a scatter plot comparing Wiktionary frequency counts with AI commonality estimates.

    Args:
        results: List of result dictionaries from analyze_word_sample()
        figsize: Figure size as (width, height)
        verbose: Verbosity level

    Returns:
        tuple of (figure, axes)
    """
    # Extract plottable data points
    plot_data = [
        {
            "word": r["word"],
            "count": r["count"],
            "commonality": r["lemma_data"].get("commonality"),
        }
        for r in results
        if r["lemma_data"] is not None and "commonality" in r["lemma_data"]
    ]

    if not plot_data:
        if verbose >= 1:
            print("\nNo commonality data found in results")
        return plt.subplots(figsize=figsize)

    # Extract data for plotting
    counts = [d["count"] for d in plot_data]
    commonalities = [d["commonality"] for d in plot_data]

    # Create scatter plot
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(counts, commonalities, alpha=0.5)
    ax.set_xscale("log")
    ax.set_xlabel("Wiktionary Frequency Count (log scale)")
    ax.set_ylabel("AI Estimated Commonality (0-1)")
    ax.set_title("Wiktionary Frequency vs AI Commonality Estimate")

    # Add trend line if we have enough points
    if len(counts) > 1:
        z = np.polyfit(np.log10(counts), commonalities, 1)
        p = np.poly1d(z)
        ax.plot(sorted(counts), p(np.log10(sorted(counts))), "r--", alpha=0.8)

        # Add correlation coefficient
        correlation = np.corrcoef(np.log10(counts), commonalities)[0, 1]
        ax.text(
            0.05, 0.95, f"Correlation (log): {correlation:.3f}", transform=ax.transAxes
        )

    ax.grid(True)

    if verbose >= 1:
        print("\nSample comparisons:")
        for d in sorted(plot_data, key=lambda x: x["count"], reverse=True):
            print(
                f"Word: {d['word']:<10} Count: {d['count']:<8} AI Commonality: {d['commonality']:.2f}"
            )

    return fig, ax
