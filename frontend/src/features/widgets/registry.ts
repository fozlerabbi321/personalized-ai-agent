import React from "react";
import { CandlestickChart } from "./components/CandlestickChart";
import { MetricCard } from "./components/MetricCard";
import { DataTable } from "./components/DataTable";

export const widgetRegistry: Record<string, React.ComponentType<any>> = {
  candlestick_chart: CandlestickChart,
  metric_card: MetricCard,
  data_table: DataTable,
};
