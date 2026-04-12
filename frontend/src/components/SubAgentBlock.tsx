import { useEffect, useRef } from "react";
import { cn } from "../utils/cn";
import { Collapsible } from "./Collapsible";
import { TaskProgress } from "./TaskProgress";
import { ToolBlock } from "./ToolBlock";
import type { TaskMessage, ToolCall } from "../types";

type Props = {
  role: string;
  task: string;
  tokens: string;
  toolCalls: ToolCall[];
  tasks: TaskMessage[];
  done: boolean;
};

export function SubAgentBlock({
  role,
  task,
  tokens,
  toolCalls,
  tasks,
  done,
}: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [tokens, toolCalls]);

  return (
    <Collapsible
      className={cn(
        "my-2 rounded py-3 pl-3",
        "border border-gray-700 bg-gray-800/30",
        "text-sm",
      )}
      header={
        <>
          <span className="text-xs font-semibold text-purple-400 uppercase">
            Sub-Agent
          </span>
          <span className="text-xs text-gray-500">{role}</span>
        </>
      }
      headerRight={
        !done ? (
          <span className="animate-pulse text-xs text-gray-500">
            working...
          </span>
        ) : undefined
      }
    >
      <div ref={scrollRef} className="mt-2 max-h-64 overflow-y-auto">
        <div className="mb-2 text-xs text-gray-400">{task}</div>
        {tasks.map((t) => (
          <div key={t.taskId} className="mb-2">
            <TaskProgress goal={t.goal} steps={t.steps} />
          </div>
        ))}
        {toolCalls.map((call, i) => (
          <ToolBlock key={i} call={call} compact />
        ))}
        {tokens && (
          <div className="mt-2 whitespace-pre-wrap text-gray-300">{tokens}</div>
        )}
      </div>
    </Collapsible>
  );
}
