import { useState } from "react";
import type { ToolCall } from "../types";
import { cn } from "../utils/cn";
import { WarningIcon } from "./Icons";

type Props = {
  call: ToolCall;
  compact?: boolean;
  onConfirm?: (approved: boolean) => void;
};

const PREVIEW_LINES = 3;
const PREVIEW_CHARS = 300;
const ARGS_PREVIEW_CHARS = 80;

export function ToolBlock({ call, compact = false, onConfirm }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [argsExpanded, setArgsExpanded] = useState(false);

  const result = call.result ?? "";
  const lines = result.split("\n");
  const tooManyLines = lines.length > PREVIEW_LINES;
  const tooManyChars = result.length > PREVIEW_CHARS;
  const isLong = tooManyLines || tooManyChars;
  const preview = tooManyLines
    ? lines.slice(0, PREVIEW_LINES).join("\n")
    : result.slice(0, PREVIEW_CHARS);

  const argsStr = JSON.stringify(call.args);
  const argsIsLong = argsStr.length > ARGS_PREVIEW_CHARS;

  return (
    <div
      className={cn(
        "my-2 rounded p-3",
        "border-l-3 border-gray-600 bg-gray-800",
        "font-mono break-all",
        compact ? "text-xs" : "text-sm",
      )}
    >
      <div className="mb-1 text-xs text-gray-500 uppercase">Tool Call</div>
      <div>
        {call.name}(
        {argsIsLong && !argsExpanded ? (
          <>
            {argsStr.slice(0, ARGS_PREVIEW_CHARS).trimEnd()}
            <button
              onClick={() => setArgsExpanded(true)}
              className="text-xs text-gray-500 hover:text-gray-300"
            >
              ...
            </button>
          </>
        ) : (
          argsStr
        )}
        )
        {argsIsLong && argsExpanded && (
          <button
            onClick={() => setArgsExpanded(false)}
            className="ml-2 text-xs text-gray-500 hover:text-gray-300"
          >
            Show less
          </button>
        )}
      </div>
      {call.confirmPending && (
        <div className="mt-3 rounded border border-yellow-600/50 bg-yellow-900/20 p-3">
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-yellow-400 uppercase">
            <WarningIcon />
            Confirmation Required
          </div>
          <div className="mb-3 text-sm text-yellow-200/80">
            {call.confirmReason}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onConfirm?.(true)}
              className="rounded bg-green-700 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-600"
            >
              Approve
            </button>
            <button
              onClick={() => onConfirm?.(false)}
              className="rounded bg-red-700 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-600"
            >
              Deny
            </button>
          </div>
        </div>
      )}
      {call.result !== undefined && (
        <>
          <div className="mt-2 mb-1 text-xs text-gray-500 uppercase">
            Result
          </div>
          <div className="whitespace-pre-wrap">
            {expanded || !isLong ? result : preview}
          </div>
          {isLong && (
            <button
              onClick={() => setExpanded(!expanded)}
              className={cn(
                "mt-1 text-xs text-gray-500",
                "hover:text-gray-300",
              )}
            >
              {expanded ? "Show less" : "... Show more"}
            </button>
          )}
        </>
      )}
    </div>
  );
}
