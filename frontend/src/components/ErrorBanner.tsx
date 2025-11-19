interface ErrorBannerProps {
  message: string;
}

export default function ErrorBanner({ message }: ErrorBannerProps) {
  return (
    <div className="border border-red-500/30 bg-red-500/10 text-red-200 rounded-2xl px-4 py-3">
      {message}
    </div>
  );
}
