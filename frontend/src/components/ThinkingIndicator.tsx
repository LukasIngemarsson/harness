import { useEffect, useState } from "react";

type Props = {
  startTime: number;
};

export function ThinkingIndicator({ startTime }: Props) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 100);
    return () => clearInterval(interval);
  }, [startTime]);

  return (
    <div className="mx-auto flex w-full max-w-3xl items-center gap-2 text-xs text-gray-500">
      <span className="animate-pulse">●</span>
      <span>{elapsed}s</span>
    </div>
  );
}
