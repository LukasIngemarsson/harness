import { useState } from "react";
import { cn } from "../utils/cn";

type Props = {
  header: React.ReactNode;
  headerRight?: React.ReactNode;
  children: React.ReactNode;
  defaultCollapsed?: boolean;
  className?: string;
};

export function Collapsible({
  header,
  headerRight,
  children,
  defaultCollapsed = false,
  className,
}: Props) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed);

  return (
    <div className={className}>
      <div
        className="flex cursor-pointer items-center justify-between"
        onClick={() => setCollapsed((c) => !c)}
      >
        <div className="flex items-center gap-2">{header}</div>
        <div className="flex items-center gap-2">
          {headerRight}
          <svg
            viewBox="0 0 16 16"
            className={cn(
              "h-3.5 w-3.5 text-gray-500 transition-transform",
              collapsed ? "-rotate-90" : "rotate-0",
            )}
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M4 6l4 4 4-4" />
          </svg>
        </div>
      </div>
      {!collapsed && children}
    </div>
  );
}
