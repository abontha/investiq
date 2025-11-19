import { memo, useEffect, useRef } from 'react';

function TradingViewWidget() {
  const container = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!container.current) return;
    container.current.innerHTML = '';
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = `{
        "symbols": [
          { "proName": "FOREXCOM:SPXUSD", "title": "S&P 500 Index" },
          { "proName": "FOREXCOM:NSXUSD", "title": "US 100 Cash CFD" },
          { "proName": "FX_IDC:EURUSD", "title": "EUR to USD" },
          { "proName": "BITSTAMP:BTCUSD", "title": "Bitcoin" },
          { "proName": "BITSTAMP:ETHUSD", "title": "Ethereum" }
        ],
        "colorTheme": "dark",
        "locale": "en",
        "largeChartUrl": "",
        "isTransparent": false,
        "showSymbolLogo": true,
        "displayMode": "adaptive"
      }`;
    container.current.appendChild(script);
  }, []);

  return (
    <div className="tradingview-widget-container w-full" ref={container}>
      <div className="tradingview-widget-container__widget" />
      <div className="tradingview-widget-copyright text-[10px] text-white/40 mt-1">
        <a href="https://www.tradingview.com/markets/" rel="noopener noreferrer" target="_blank" className="text-cyan-400">
          Ticker tape
        </a>{' '}
        <span className="text-white/30">by TradingView</span>
      </div>
    </div>
  );
}

export default memo(TradingViewWidget);
