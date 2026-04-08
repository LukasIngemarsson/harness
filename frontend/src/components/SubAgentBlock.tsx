import { useEffect, useRef, useState } from "react";
import { cn } from "../utils/cn";
import { ToolBlock } from "./ToolBlock";
import type { ToolCall } from "../types";

type Props = {
  role: string;
  task: string;
  tokens: string;
  toolCalls: ToolCall[];
  done: boolean;
};

export function SubAgentBlock({ role, task, tokens, toolCalls, done }: Props) {
  const [collapsed, setCollapsed] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!collapsed && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [tokens, toolCalls, collapsed]);

  return (
    <div
      className={cn(
        "my-2 rounded p-3",
        "border border-gray-700 bg-gray-800/30",
        "text-sm",
      )}
    >
      <div
        className="flex cursor-pointer items-center justify-between"
        onClick={() => setCollapsed(!collapsed)}
      >
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-purple-400 uppercase">
            Sub-Agent
          </span>
          <span className="text-xs text-gray-500">{role}</span>
          {collapsed && (
            <span className="text-xs text-gray-600">
              — {task.slice(0, 60)}
              {task.length > 60 ? "..." : ""}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!done && collapsed && (
            <span className="animate-pulse text-xs text-gray-500">
              working...
            </span>
          )}
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
      {!collapsed && (
        <div ref={scrollRef} className="mt-2 max-h-64 overflow-y-auto">
          <div className="mb-2 text-xs text-gray-400">{task}</div>
          {toolCalls.map((call, i) => (
            <ToolBlock key={i} call={call} compact />
          ))}
          {tokens && (
            <div className="mt-2 whitespace-pre-wrap text-gray-300">
              {tokens}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
