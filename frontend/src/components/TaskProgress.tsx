import type { TaskStep } from "../types";
import { cn } from "../utils/cn";

type Props = {
  goal: string;
  steps: TaskStep[];
};

function statusIcon(status: string): string {
  switch (status) {
    case "completed":
      return "\u2713";
    case "in_progress":
      return "\u25CB";
    case "failed":
      return "\u2717";
    case "skipped":
      return "\u2013";
    default:
      return "\u00B7";
  }
}

function statusColor(status: string): string {
  switch (status) {
    case "completed":
      return "text-green-400";
    case "in_progress":
      return "text-blue-400";
    case "failed":
      return "text-red-400";
    case "skipped":
      return "text-gray-500";
    default:
      return "text-gray-600";
  }
}

export function TaskProgress({ goal, steps }: Props) {
  const completed = steps.filter((s) => s.status === "completed").length;

  return (
    <div
      className={cn(
        "my-2 rounded p-3",
        "border border-gray-700 bg-gray-800/50",
        "text-sm",
      )}
    >
      <div className="mb-2 flex items-center justify-between">
        <span className="font-medium text-gray-300">{goal}</span>
        <span className="text-xs text-gray-500">
          {completed}/{steps.length}
        </span>
      </div>
      <div className="flex flex-col gap-1">
        {steps.map((step, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className={cn("w-4 text-center", statusColor(step.status))}>
              {statusIcon(step.status)}
            </span>
            <span
              className={cn(
                step.status === "completed" && "text-gray-500 line-through",
                step.status === "pending" && "text-gray-400",
                step.status === "in_progress" && "text-gray-200",
                step.status === "failed" && "text-red-400",
              )}
            >
              {step.description}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
