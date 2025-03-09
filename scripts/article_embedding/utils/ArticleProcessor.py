import re               # For regular expression operations (pattern matching and substitutions)
import html             # For converting HTML entities (e.g. &quot;) to their corresponding characters
import tiktoken         # For encoding text into tokens (useful for token counting)
import nltk             # For natural language processing, including sentence tokenization

# Assume nltk.download('punkt') has been run if necessary to ensure sentence tokenization works

class ArticleProcessor:
    """
    A class to process and chunk article text based on token limits and balanced punctuation.
    
    This class provides methods to:
      - Clean and normalize raw article text.
      - Split text into sentences.
      - Count tokens in text using the tiktoken encoder.
      - Build text chunks from sentences, ensuring that punctuation (quotes, parentheses, square brackets) 
        is balanced and that each chunk's token count is within specified limits.
    """
    
    def __init__(self, lower_bound=50, upper_bound=200):
        """
        Initializes the ArticleProcessor with a tiktoken encoder and token limits.
        
        Args:
            lower_bound (int, optional): Minimum number of tokens allowed in a chunk. Defaults to 50.
            upper_bound (int, optional): Maximum number of tokens allowed in a chunk. Defaults to 200.
        """
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
    
    def clean_article_text(self, text: str) -> str:
        """
        Cleans and normalizes the provided article text by performing the following operations:
          - Collapses multiple whitespace characters into a single space.
          - Removes leading and trailing whitespace.
          - Unescapes HTML entities (e.g., &quot; becomes ").
          - Replaces curly quotes (both double and single) with standard straight quotes.
          - Removes URLs from the text.
          - Collapses multiple newline characters into a single newline.
        
        Args:
            text (str): The raw article text to be cleaned.
        
        Returns:
            str: The cleaned and normalized text.
        """
        junk_text_pattern = re.compile(r"STORY CONTINUES.*?privacy policy \.", re.DOTALL | re.IGNORECASE)
        text = re.sub(junk_text_pattern, "", text).strip()

        # Replace multiple whitespace characters with a single space and strip extra spaces.
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Convert HTML entities (like &quot;) into their normal character equivalents.
        text = html.unescape(text)
        
        # Replace curly double quotes with standard double quotes.
        text = text.replace("“", '"').replace("”", '"')
        
        # Replace curly single quotes/apostrophes with standard single quotes.
        text = text.replace("‘", "'").replace("’", "'")
        
        # Define a regular expression to match URLs (http://, https://, or starting with www.).
        url_pattern = r"(https?://\S+|www\.\S+)"
        # Remove all URLs from the text.
        text = re.sub(url_pattern, "", text)
        
        # Collapse multiple newline characters into a single newline.
        text = re.sub(r"\n+", "\n", text)
        
        # Again collapse any remaining multiple whitespace characters into a single space.
        text = re.sub(r"\s+", " ", text)
        
        # Final removal of any leading or trailing whitespace.
        text = text.strip()
        
        return text

    def split_into_sentences(self, text: str):
        """
        Splits a block of text into a list of sentences using NLTK's sentence tokenizer.
        
        Args:
            text (str): The text that needs to be split into sentences.
        
        Returns:
            list: A list of sentence strings extracted from the text.
        """
        sentences = nltk.sent_tokenize(text)
        return sentences

    def token_count(self, text: str) -> int:
        """
        Counts the number of tokens in the given text using the tiktoken encoder.
        This is useful to ensure that text chunks conform to a token limit.
        
        Args:
            text (str): The text to count tokens for.
        
        Returns:
            int: The number of tokens in the text.
        """
        return len(self.encoder.encode(text))
    
    def _is_balanced(self, text: str) -> bool:
        """
        Checks if the text has balanced punctuation for:
          - Double quotes (ensuring an even number of quotes),
          - Parentheses (matching '(' with ')'),
          - Square brackets (matching '[' with ']').
        
        Args:
            text (str): The text to be checked.
        
        Returns:
            bool: True if the punctuation markers are balanced, False otherwise.
        """
        return (text.count('"') % 2 == 0) and \
               (text.count("(") == text.count(")")) and \
               (text.count("[") == text.count("]"))
    
    def _split_text_into_token_chunks(self, text: str, lower=None, upper=None):
        """
        Splits a long text into subchunks whose token counts are within the [lower, upper] range.
        If the final subchunk is too short (i.e., fewer tokens than the lower limit), it merges it with the previous subchunk.
        
        Args:
            text (str): The text to split.
            lower (int, optional): The minimum number of tokens required in a chunk. Defaults to self.lower_bound.
            upper (int, optional): The maximum number of tokens allowed in a chunk. Defaults to self.upper_bound.
        
        Returns:
            list: A list of text subchunks meeting the token constraints.
        """
        # Use provided lower and upper bounds or default to class settings.
        if lower is None:
            lower = self.lower_bound
        if upper is None:
            upper = self.upper_bound
        
        tokens = self.encoder.encode(text)
        # If the total token count is within the upper limit, return the text as a single chunk.
        if len(tokens) <= upper:
            return [text]
        
        subchunks = []
        start = 0
        # Process tokens in slices to ensure each slice is within the upper limit.
        while start < len(tokens):
            end = start + upper
            # If not at the end and the remaining tokens are fewer than the lower limit,
            # then take all remaining tokens to form a chunk.
            if end < len(tokens) and len(tokens) - end < lower:
                end = len(tokens)
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)
            subchunks.append(chunk_text.strip())
            start = end
        
        # Merge the last subchunk with the previous one if it doesn't meet the lower token threshold.
        if len(subchunks) > 1 and self.token_count(subchunks[-1]) < lower:
            subchunks[-2] = subchunks[-2] + " " + subchunks[-1]
            subchunks.pop()
        return subchunks

    def sentence_to_chunks(self, sentences: list):
        """
        Constructs chunks of text from a list of sentences ensuring:
          1. Chunks continue to accumulate sentences if punctuation such as quotes, parentheses, or square brackets are not balanced.
          2. Each finalized chunk has a token count within the desired range (between self.lower_bound and self.upper_bound).
          3. The final sentence is included even if the punctuation is unbalanced.
        
        Args:
            sentences (list): A list of sentences to be combined into chunks.
        
        Returns:
            list: A list of text chunks, each meeting the specified token count and punctuation balance requirements.
        """
        chunks = []      # List to store the finalized chunks.
        curr_chunk = ""  # Variable to accumulate sentences into a candidate chunk.
        
        # Iterate over each sentence in the provided list.
        for sentence in sentences:
            sentence = sentence.strip()  # Remove any extra spaces from the sentence.
            # Create a candidate chunk by appending the sentence to the current chunk.
            candidate = (curr_chunk + " " + sentence).strip() if curr_chunk else sentence
            candidate_tokens = self.token_count(candidate)  # Count tokens in the candidate chunk.
            candidate_balanced = self._is_balanced(candidate)  # Check if punctuation in the candidate is balanced.
            
            # If the candidate chunk exceeds the maximum token limit:
            if candidate_tokens > self.upper_bound:
                # If the existing current chunk is valid (i.e., has at least lower_bound tokens and is balanced),
                # then finalize it as a chunk.
                if curr_chunk and (self.token_count(curr_chunk) >= self.lower_bound and self._is_balanced(curr_chunk)):
                    chunks.append(curr_chunk.strip())
                    curr_chunk = sentence  # Start a new chunk with the current sentence.
                    continue
                else:
                    # The candidate (or the sentence alone) is too long, so split the sentence into smaller subchunks.
                    subchunks = self._split_text_into_token_chunks(sentence, lower=self.lower_bound, upper=self.upper_bound)
                    for sub in subchunks:
                        chunks.append(sub)
                    curr_chunk = ""  # Reset the current chunk after processing the sentence.
                    continue
            
            # If the candidate is balanced and its token count falls within the desired range, finalize it.
            if candidate_balanced and self.lower_bound <= candidate_tokens <= self.upper_bound:
                chunks.append(candidate.strip())
                curr_chunk = ""  # Reset the current chunk for new accumulation.
            else:
                # Otherwise, continue appending the sentence to the current chunk.
                curr_chunk = candidate
        
        # Ensure any remaining text in curr_chunk is added as a chunk.
        if curr_chunk:
            if self.token_count(curr_chunk) > self.upper_bound:
                subchunks = self._split_text_into_token_chunks(curr_chunk, lower=self.lower_bound, upper=self.upper_bound)
                chunks.extend(subchunks)
            else:
                chunks.append(curr_chunk.strip())
                
        return chunks
