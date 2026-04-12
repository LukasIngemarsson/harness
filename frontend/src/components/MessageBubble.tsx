import type { ChatMessage } from "../types";
import { MessageRole, TaskStatus } from "../types";
import { AssistantMessage } from "./AssistantMessage";
import { MessageWrapper } from "./MessageWrapper";
import { SubAgentBlock } from "./SubAgentBlock";
import { SystemMessage } from "./SystemMessage";
import { TaskProgress } from "./TaskProgress";
import { ToolBlock } from "./ToolBlock";
import { UserMessage } from "./UserMessage";

type Props = {
  message: ChatMessage;
  onConfirm?: (approved: boolean) => void;
};

export function MessageBubble({ message, onConfirm }: Props) {
  switch (message.role) {
    case MessageRole.User:
      return (
        <MessageWrapper label="User" labelColor="text-blue-400">
          <UserMessage content={message.content} />
        </MessageWrapper>
      );

    case MessageRole.System:
      return (
        <MessageWrapper>
          <SystemMessage content={message.content} />
        </MessageWrapper>
      );

    case MessageRole.Assistant:
      return (
        <MessageWrapper label="Assistant" labelColor="text-green-400">
          <AssistantMessage content={message.content} />
        </MessageWrapper>
      );

    case MessageRole.Tool:
      return (
        <MessageWrapper label="Tools">
          {message.calls.map((call, i) => (
            <ToolBlock key={i} call={call} onConfirm={onConfirm} />
          ))}
        </MessageWrapper>
      );

    case MessageRole.Task:
      return (
        <MessageWrapper sticky={message.status !== TaskStatus.Completed}>
          <TaskProgress
            goal={message.goal}
            steps={message.steps}
          />
        </MessageWrapper>
      );

    case MessageRole.SubAgent:
      return (
        <MessageWrapper>
          <SubAgentBlock
            role={message.agentRole}
            task={message.task}
            tokens={message.tokens}
            toolCalls={message.toolCalls}
            tasks={message.tasks}
            done={message.done}
          />
        </MessageWrapper>
      );

    default:
      return null;
  }
}
