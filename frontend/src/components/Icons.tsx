import { cn } from "../utils/cn";

type IconProps = {
  className?: string;
};

export function ChevronIcon({ className }: IconProps) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={cn("h-3.5 w-3.5", className)}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M4 6l4 4 4-4" />
    </svg>
  );
}

export function LockIcon({ className }: IconProps) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={cn("h-3.5 w-3.5", className)}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3.5" y="8" width="9" height="6.5" rx="1.5" />
      <path d="M5.5 8V5.5a2.5 2.5 0 0 1 5 0V8" />
    </svg>
  );
}

export function UnlockIcon({ className }: IconProps) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={cn("h-3.5 w-3.5", className)}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="3.5" y="8" width="9" height="6.5" rx="1.5" />
      <path d="M5.5 8V5.5a2.5 2.5 0 0 1 5 0" />
    </svg>
  );
}

export function TokenStackIcon({ className }: IconProps) {
  return (
    <svg
      viewBox="0 0 16 16"
      className={cn("h-3.5 w-3.5", className)}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
    >
      <ellipse cx="8" cy="11" rx="5" ry="2" />
      <ellipse cx="8" cy="8" rx="5" ry="2" />
      <ellipse cx="8" cy="5" rx="5" ry="2" />
      <line x1="3" y1="5" x2="3" y2="11" />
      <line x1="13" y1="5" x2="13" y2="11" />
    </svg>
  );
}

export function WarningIcon({ className }: IconProps) {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="currentColor"
      className={cn("h-4 w-4", className)}
    >
      <path
        fillRule="evenodd"
        d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 6a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 6zm0 9a1 1 0 100-2 1 1 0 000 2z"
        clipRule="evenodd"
      />
    </svg>
  );
}
