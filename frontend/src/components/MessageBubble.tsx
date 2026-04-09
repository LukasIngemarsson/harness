import Markdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "../types";
import { MessageRole } from "../types";
import { SubAgentBlock } from "./SubAgentBlock";
import { ToolBlock } from "./ToolBlock";

type Props = {
  message: ChatMessage;
  onConfirm?: (approved: boolean) => void;
};

export function MessageBubble({ message, onConfirm }: Props) {
  if (message.role === MessageRole.User) {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <div className="mb-1 text-xs font-semibold text-blue-400 uppercase">
          User
        </div>
        <div className="whitespace-pre-wrap">{message.content}</div>
      </div>
    );
  }

  if (message.role === MessageRole.System) {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <div className="text-xs text-gray-500 italic">{message.content}</div>
      </div>
    );
  }

  if (message.role === MessageRole.SubAgent) {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <SubAgentBlock
          role={message.agentRole}
          task={message.task}
          tokens={message.tokens}
          toolCalls={message.toolCalls}
          done={message.done}
        />
      </div>
    );
  }

  if (message.role === MessageRole.Tool) {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <div className="mb-1 text-xs font-semibold text-gray-500 uppercase">
          Tools
        </div>
        {message.calls.map((call, i) => (
          <ToolBlock key={i} call={call} onConfirm={onConfirm} />
        ))}
      </div>
    );
  }

  if (message.role === MessageRole.Assistant) {
    return (
      <div className="mx-auto w-full max-w-3xl">
        <div className="mb-1 text-xs font-semibold text-green-400 uppercase">
          Assistant
        </div>
        <div className="prose prose-invert max-w-none">
          <Markdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
          >
            {message.content}
          </Markdown>
        </div>
      </div>
    );
  }

  return null;
}
