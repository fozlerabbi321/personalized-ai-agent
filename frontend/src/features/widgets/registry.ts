import React from "react";
import { BookCard } from "./components/BookCard";
import { BookReview } from "./components/BookReview";
import { ReadingTracker } from "./components/ReadingTracker";
import { WidgetType } from "./constants";
import { WidgetPayload } from "./types";

export const widgetRegistry: Record<string, React.ComponentType<WidgetPayload>> = {
  [WidgetType.BOOK_CARD]: BookCard as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.BOOK_REVIEW]: BookReview as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.READING_TRACKER]: ReadingTracker as unknown as React.ComponentType<WidgetPayload>,
};
