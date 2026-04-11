import type { TaskStep } from "../types";
import { TaskStatus } from "../types";
import { cn } from "../utils/cn";
import { Collapsible } from "./Collapsible";

type Props = {
  goal: string;
  steps: TaskStep[];
  status?: string;
};

const STATUS_DISPLAY: Record<string, { icon: string; color: string }> = {
  [TaskStatus.Completed]: { icon: "\u2713", color: "text-green-400" },
  [TaskStatus.InProgress]: { icon: "\u25CB", color: "text-blue-400" },
  [TaskStatus.Failed]: { icon: "\u2717", color: "text-red-400" },
  [TaskStatus.Skipped]: { icon: "\u2013", color: "text-gray-500" },
  [TaskStatus.Pending]: { icon: "\u00B7", color: "text-gray-600" },
};

const DEFAULT_STATUS = { icon: "\u00B7", color: "text-gray-600" };

export function TaskProgress({ goal, steps, status }: Props) {
  const completed = steps.filter(
    (s) => s.status === TaskStatus.Completed,
  ).length;
  const active = status && status !== TaskStatus.Completed;

  return (
    <Collapsible
      className={cn(
        "rounded border border-gray-700 bg-gray-800/50 text-sm",
        active && "sticky top-0 z-10 bg-gray-800",
      )}
      header={
        <span className="px-3 py-2 font-medium text-gray-300">{goal}</span>
      }
      headerRight={
        <span className="px-3 py-2 text-xs text-gray-500">
          {completed}/{steps.length}
        </span>
      }
    >
      <div className="flex flex-col gap-1 px-3 pb-2">
        {steps.map((step, i) => {
          const { icon, color } = STATUS_DISPLAY[step.status] ?? DEFAULT_STATUS;
          return (
            <div key={i} className="flex items-center gap-2">
              <span className={cn("w-4 text-center", color)}>{icon}</span>
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
          );
        })}
      </div>
    </Collapsible>
  );
}
