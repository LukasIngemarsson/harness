import type { ChatMessage } from "../types";
import { ToolBlock } from "./ToolBlock";

type Props = {
  message: ChatMessage;
};

export function MessageBubble({ message }: Props) {
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
