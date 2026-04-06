import type { ChatMessage, Task } from "../types";
import { TaskProgress } from "./TaskProgress";
import { ToolBlock } from "./ToolBlock";

type Props = {
  message: ChatMessage;
  tasks: Record<string, Task>;
};

export function MessageBubble({ message, tasks }: Props) {
  if (message.role === "user") {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <div className="mb-1 text-xs font-semibold text-blue-400 uppercase">
          User
        </div>
        <div className="whitespace-pre-wrap">{message.content}</div>
      </div>
    );
  }

  if (message.role === "system") {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <div className="text-xs text-gray-500 italic">{message.content}</div>
      </div>
    );
  }

  if (message.role === "task") {
    const task = tasks[message.taskId];
    if (!task) return null;
    return (
      <div className="mx-auto w-full max-w-3xl">
        <TaskProgress goal={task.goal} steps={task.steps} />
      </div>
    );
  }

  if (message.role === "tool") {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <div className="mb-1 text-xs font-semibold text-gray-500 uppercase">
          Tools
        </div>
        {message.calls.map((call, i) => (
          <ToolBlock key={i} call={call} />
        ))}
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-3xl">
      <div className="mb-1 text-xs font-semibold text-green-400 uppercase">
        Assistant
      </div>
      <div className="whitespace-pre-wrap">{message.content}</div>
    </div>
  );
}
