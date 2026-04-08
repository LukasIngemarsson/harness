export enum EventType {
  Token = "token",
  ToolStart = "tool_start",
  ToolCall = "tool_call",
  ToolResult = "tool_result",
  ToolEnd = "tool_end",
  Error = "error",
  Done = "done",
  Cleared = "cleared",
  TaskUpdate = "task_update",
  SystemMessage = "system_message",
  SubAgentStart = "sub_agent_start",
  SubAgentEvent = "sub_agent_event",
  SubAgentEnd = "sub_agent_end",
}

export enum Command {
  Clear = "/clear",
  Mode = "/mode",
  Exit = "exit", // not used in the UI, but needed to pass sync test
}

export enum TaskStatus {
  Pending = "pending",
  InProgress = "in_progress",
  Completed = "completed",
  Failed = "failed",
  Skipped = "skipped",
}

export enum MessageRole {
  User = "user",
  Assistant = "assistant",
  System = "system",
  Tool = "tool",
  SubAgent = "sub_agent",
}

type TokenEvent = { type: EventType.Token; content: string };
type ToolStartEvent = { type: EventType.ToolStart };
type ToolCallEvent = {
  type: EventType.ToolCall;
  name: string;
  args: Record<string, unknown>;
};
type ToolResultEvent = { type: EventType.ToolResult; result: string };
type ToolEndEvent = { type: EventType.ToolEnd };
type ErrorEvent = { type: EventType.Error; content: string };
type Usage = {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
};
type DoneEvent = { type: EventType.Done; usage: Usage | null };
type ClearedEvent = { type: EventType.Cleared };
type TaskUpdateEvent = { type: EventType.TaskUpdate; tasks: Task[] };
type SystemMessageEvent = { type: EventType.SystemMessage; content: string };
type SubAgentStartEvent = {
  type: EventType.SubAgentStart;
  agent_id: string;
  role: string;
  task: string;
};
type SubAgentEventEvent = {
  type: EventType.SubAgentEvent;
  agent_id: string;
  event: AgentEvent;
};
type SubAgentEndEvent = {
  type: EventType.SubAgentEnd;
  agent_id: string;
  result: string;
};

export type AgentEvent =
  | TokenEvent
  | ToolStartEvent
  | ToolCallEvent
  | ToolResultEvent
  | ToolEndEvent
  | ErrorEvent
  | DoneEvent
  | ClearedEvent
  | TaskUpdateEvent
  | SystemMessageEvent
  | SubAgentStartEvent
  | SubAgentEventEvent
  | SubAgentEndEvent;

export type SubAgentMessage = {
  role: MessageRole.SubAgent;
  agentId: string;
  agentRole: string;
  task: string;
  tokens: string;
  toolCalls: ToolCall[];
  done: boolean;
};

export type ChatMessage =
  | { role: MessageRole.User; content: string }
  | { role: MessageRole.Assistant; content: string; toolCalls?: ToolCall[] }
  | { role: MessageRole.Tool; calls: ToolCall[] }
  | { role: MessageRole.System; content: string }
  | SubAgentMessage;

export type Task = {
  id: string;
  goal: string;
  status: string;
  steps: TaskStep[];
};

export type TaskStep = {
  description: string;
  status: string;
};

export type ToolCall = {
  name: string;
  args: Record<string, unknown>;
  result?: string;
};
