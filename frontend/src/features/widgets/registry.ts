import React from "react";
import { CandlestickChart } from "./components/CandlestickChart";
import { MetricCard } from "./components/MetricCard";
import { DataTable } from "./components/DataTable";
import { WidgetType } from "./constants";
import { WidgetPayload } from "./types";

export const widgetRegistry: Record<string, React.ComponentType<WidgetPayload>> = {
  [WidgetType.CANDLESTICK_CHART]: CandlestickChart as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.METRIC_CARD]: MetricCard as unknown as React.ComponentType<WidgetPayload>,
  [WidgetType.DATA_TABLE]: DataTable as unknown as React.ComponentType<WidgetPayload>,
};
