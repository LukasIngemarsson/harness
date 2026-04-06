import { useState } from "react";
import type { TaskStep } from "../types";
import { TaskStatus } from "../types";
import { cn } from "../utils/cn";

type Props = {
  goal: string;
  steps: TaskStep[];
};

function statusIcon(status: string): string {
  switch (status) {
    case TaskStatus.Completed:
      return "\u2713";
    case TaskStatus.InProgress:
      return "\u25CB";
    case TaskStatus.Failed:
      return "\u2717";
    case TaskStatus.Skipped:
      return "\u2013";
    default:
      return "\u00B7";
  }
}

function statusColor(status: string): string {
  switch (status) {
    case TaskStatus.Completed:
      return "text-green-400";
    case TaskStatus.InProgress:
      return "text-blue-400";
    case TaskStatus.Failed:
      return "text-red-400";
    case TaskStatus.Skipped:
      return "text-gray-500";
    default:
      return "text-gray-600";
  }
}

export function TaskProgress({ goal, steps }: Props) {
  const [collapsed, setCollapsed] = useState(false);
  const completed = steps.filter(
    (s) => s.status === TaskStatus.Completed,
  ).length;

  return (
    <div
      className={cn("rounded border border-gray-700 bg-gray-800/50 text-sm")}
    >
      <button
        type="button"
        onClick={() => setCollapsed((c) => !c)}
        className={cn(
          "flex w-full items-center justify-between px-3 py-2",
          "text-left hover:bg-gray-700/30",
        )}
      >
        <span className="font-medium text-gray-300">{goal}</span>
        <span className="text-xs text-gray-500">
          {completed}/{steps.length}
          <span className="ml-2">{collapsed ? "\u25B6" : "\u25BC"}</span>
        </span>
      </button>
      {!collapsed && (
        <div className="flex flex-col gap-1 px-3 pb-2">
          {steps.map((step, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className={cn("w-4 text-center", statusColor(step.status))}>
                {statusIcon(step.status)}
              </span>
              <span
                className={cn(
                  step.status === TaskStatus.Completed &&
                    "text-gray-500 line-through",
                  step.status === TaskStatus.Pending && "text-gray-400",
                  step.status === TaskStatus.InProgress && "text-gray-200",
                  step.status === TaskStatus.Failed && "text-red-400",
                )}
              >
                {step.description}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
