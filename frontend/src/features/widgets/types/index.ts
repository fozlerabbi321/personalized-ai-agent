export interface OHLCItem {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface CandlestickWidgetPayload {
  widget_type: "candlestick_chart";
  ticker: string;
  title: string;
  current_price: number;
  change: number;
  change_pct: number;
  seven_day_high: number;
  seven_day_low: number;
  data: OHLCItem[];
  metric?: {
    label: string;
    value: string;
    delta: string;
    sentiment?: "positive" | "negative" | "neutral";
  };
}

export interface MetricCardWidgetPayload {
  widget_type: "metric_card";
  label: string;
  value: string;
  delta?: string;
  sentiment?: "positive" | "negative" | "neutral";
  subtitle?: string;
}

export interface DataTableWidgetPayload {
  widget_type: "data_table";
  title?: string;
  columns: string[];
  rows: Array<Record<string, string | number>>;
}

export type WidgetPayload =
  | CandlestickWidgetPayload
  | MetricCardWidgetPayload
  | DataTableWidgetPayload;
