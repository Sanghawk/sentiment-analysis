export interface Article {
  display_datetime: string;
  last_modified_datetime: string;
  publish_datetime: string;
  create_datetime: string;
  content_vertical: string;
  og_description: string;
  content_type: string;
  page_url: string;
  og_title: string;
  content_title: string;
  og_site_name: string;
  tags: string;
  authors: string;
  content_tier: string;
  article_s3_url: string;
  id: number;
}

export interface ArticleContentResponse {
  text: string;
}

export interface ArticleSimilarity {
  article: Article;
  distance: number;
}

export interface ArticleSimilaritySearchResult {
  items: ArticleSimilarity[];
  total: number;
  page: number;
  page_size: number;
}
