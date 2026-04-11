type Props = {
  content: string;
};

export function UserMessage({ content }: Props) {
  if (content.startsWith("/")) {
    return (
      <span className="inline-block rounded bg-gray-700 px-2 py-0.5 font-mono text-sm text-gray-300">
        {content}
      </span>
    );
  }

  return <div className="whitespace-pre-wrap">{content}</div>;
}
