import { createChart, ColorType, type IChartApi, type ISeriesApi } from 'lightweight-charts';
import { useEffect, useRef } from 'react';

interface ChartPoint {
  time: string;
  value: number;
}

interface LineChartProps {
  data: ChartPoint[];
  height?: number;
  gradientFrom?: string;
  gradientTo?: string;
  markers?: Parameters<ISeriesApi<'Area'>['setMarkers']>[0];
}

export default function LineChart({ data, height = 320, gradientFrom = 'rgba(20,241,149,0.4)', gradientTo = 'rgba(106,93,255,0.1)', markers }: LineChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Area'> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      height,
      width: containerRef.current.clientWidth,
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#A2B6FF',
        fontFamily: 'Inter',
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.04)' },
        horzLines: { color: 'rgba(255,255,255,0.04)' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderVisible: false,
      },
      timeScale: {
        borderVisible: false,
      },
    });

    const series = chart.addAreaSeries({
      lineWidth: 2,
      topColor: gradientFrom,
      bottomColor: gradientTo,
      lineColor: gradientFrom,
    });

    series.setData(data);
    if (markers && markers.length) {
      series.setMarkers(markers);
    }
    seriesRef.current = series;

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);
    chart.timeScale().fitContent();

    chartRef.current = chart;

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, [data, gradientFrom, gradientTo, height, markers]);

  useEffect(() => {
    if (!chartRef.current || !seriesRef.current) return;
    seriesRef.current.setData(data);
    if (markers && markers.length) {
      seriesRef.current.setMarkers(markers);
    } else {
      seriesRef.current.setMarkers([]);
    }
    chartRef.current.timeScale().fitContent();
  }, [data, markers]);

  return <div ref={containerRef} className="w-full" />;
}
