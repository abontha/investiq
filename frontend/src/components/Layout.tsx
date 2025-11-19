import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LineChart, Info, Sparkles, TrendingUp } from 'lucide-react';
import type { ReactNode } from 'react';
import TradingViewWidget from './TradingViewWidget';

const navItems = [
  { label: 'Predictions', path: '/predictions', icon: TrendingUp },
  { label: 'Backtesting', path: '/backtesting', icon: LineChart },
  { label: 'About', path: '/about', icon: Info },
];

interface LayoutProps {
  children?: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-night text-white flex">
      <aside className="w-64 hidden lg:flex flex-col border-r border-white/5 bg-[#04060c]/80 backdrop-blur-xl">
        <div className="px-8 py-10 flex items-center gap-3">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-glow">
            <Sparkles className="text-night" size={28} />
          </div>
          <div>
            <p className="uppercase tracking-[0.3em] text-xs text-white/70">InvestIQ</p>
            <p className="text-lg font-semibold text-white">Alpha Studio</p>
          </div>
        </div>
        <nav className="flex-1 px-4 space-y-2">
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive: navActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 relative overflow-hidden ${
                    (navActive || isActive)
                      ? 'text-white bg-white/10 shadow-[0_10px_30px_rgba(20,241,149,0.15)]'
                      : 'text-white/60 hover:text-white hover:bg-white/5'
                  }`
                }
              >
                <item.icon size={20} />
                <span className="font-medium">{item.label}</span>
                {(location.pathname === item.path || (item.path !== '/about' && location.pathname.startsWith(item.path))) && (
                  <motion.span
                    layoutId="nav-indicator"
                    className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-emerald-400 to-cyan-500"
                  />
                )}
              </NavLink>
            );
          })}
        </nav>
        <div className="px-6 py-8">
          <div className="glass-panel p-4">
            <p className="text-xs text-white/60 uppercase tracking-[0.3em]">Alpha Build</p>
            <p className="text-sm text-white mt-2">
              Experimental FinRL studio for premium predictive insights. For educational purposes only.
            </p>
          </div>
        </div>
      </aside>
      <div className="flex-1 flex flex-col">
        <header className="lg:hidden px-5 py-4 border-b border-white/5 bg-[#050814]/80 backdrop-blur-xl flex items-center justify-between">
          <div>
            <p className="uppercase tracking-[0.4em] text-[10px] text-white/60">InvestIQ</p>
            <p className="font-semibold">FinRL Studio</p>
          </div>
        </header>
        <main className="flex-1 px-4 sm:px-6 lg:px-10 py-6 lg:py-10 space-y-6">
          <div className="glass-panel p-3 overflow-hidden">
            <TradingViewWidget />
          </div>
          {children ?? <Outlet />}
        </main>
      </div>
    </div>
  );
}

export default Layout;
