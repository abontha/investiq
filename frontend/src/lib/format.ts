const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
});

export const formatCurrency = (value: number) => currencyFormatter.format(value);

export const formatPercent = (value: number, digits = 2) => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(digits)}%`;
};

export const formatDate = (iso: string) => {
  const date = new Date(iso);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
};

export const toChartDate = (iso: string) => {
  return iso.split('T')[0];
};
