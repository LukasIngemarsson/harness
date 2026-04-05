import type { ToolCall } from "../types";

type Props = {
  call: ToolCall;
};

export function ToolBlock({ call }: Props) {
  return (
    <div className="my-2 rounded border-l-3 border-gray-600 bg-gray-800 p-3 font-mono text-sm">
      <div className="mb-1 text-xs text-gray-500 uppercase">Tool Call</div>
      <div>
        {call.name}({JSON.stringify(call.args)})
      </div>
      {call.result !== undefined && (
        <>
          <div className="mt-2 mb-1 text-xs text-gray-500 uppercase">
            Result
          </div>
          <div className="whitespace-pre-wrap">{call.result}</div>
        </>
      )}
    </div>
  );
}
