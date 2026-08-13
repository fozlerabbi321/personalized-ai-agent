// ── Lumen AI Widget Payload Types ─────────────────────────────────────────────

export interface RecommendedBook {
  title: string;
  author: string;
  rating: number;
  pages: number;
  published_year: number;
  genre: string;
  cover_theme?: string;
  tagline: string;
  match_reason: string;
  isbn?: string;
}

export interface BookCardPayload {
  widget_type: "book_card";
  genre: string;
  total_matches: number;
  recommend_note: string;
  books: RecommendedBook[];
}

export interface BookReviewPayload {
  widget_type: "book_review";
  title: string;
  author: string;
  published_year: number;
  genre: string;
  rating: number;
  summary: string;
  themes: string[];
  key_takeaways: string[];
  memorable_quote: string;
  reading_time_hours: number;
  target_audience: string;
}

export interface RecentRead {
  title: string;
  author: string;
  rating: number;
  finished_date: string;
}

export interface ReadingTrackerPayload {
  widget_type: "reading_tracker";
  annual_target: number;
  books_read: number;
  completion_pct: number;
  pages_read: number;
  current_streak_days: number;
  longest_streak_days: number;
  favorite_genre: string;
  status_label: string;
  year: number;
  recent_books: RecentRead[];
}

export type WidgetPayload =
  | BookCardPayload
  | BookReviewPayload
  | ReadingTrackerPayload;
