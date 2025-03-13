export interface ArticleChunkResponse {
  id: number;
  article_id: number;
  chunk_text: string;
  token_size: number;
}

export interface ArticleChunkSearchResult {
  chunk: ArticleChunkResponse;
  distance: number;
}

export interface PaginatedArticleChunkSearchResults {
  items: ArticleChunkSearchResult[];
  total: number;
  page: number;
  page_size: number;
}
