import { useState } from "react";
import { cn } from "../utils/cn";
import { ChevronIcon } from "./Icons";

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
        className="flex cursor-pointer items-center justify-between pr-3"
        onClick={() => setCollapsed((c) => !c)}
      >
        <div className="flex items-center gap-2">{header}</div>
        <div className="flex items-center gap-2">
          {headerRight}
          <ChevronIcon
            className={cn(
              "text-gray-500 transition-transform",
              collapsed ? "-rotate-90" : "rotate-0",
            )}
          />
        </div>
      </div>
      {!collapsed && children}
    </div>
  );
}
