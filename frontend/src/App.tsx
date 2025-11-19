import { AnimatePresence, motion } from 'framer-motion';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import Layout from './components/Layout';
import PredictionsPage from './pages/PredictionsPage';
import BacktestingPage from './pages/BacktestingPage';
import AboutPage from './pages/AboutPage';

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route
          path="/predictions"
          element={
            <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit" transition={{ duration: 0.5 }}>
              <PredictionsPage />
            </motion.div>
          }
        />
        <Route
          path="/backtesting"
          element={
            <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit" transition={{ duration: 0.5 }}>
              <BacktestingPage />
            </motion.div>
          }
        />
        <Route
          path="/about"
          element={
            <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit" transition={{ duration: 0.5 }}>
              <AboutPage />
            </motion.div>
          }
        />
        <Route path="/" element={<Navigate to="/predictions" replace />} />
        <Route path="*" element={<Navigate to="/predictions" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <Layout>
      <AnimatedRoutes />
    </Layout>
  );
}
