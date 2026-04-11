type Props = {
  content: string;
};

export function SystemMessage({ content }: Props) {
  return (
    <div className="whitespace-pre-wrap text-xs text-gray-500">
      {content}
    </div>
  );
}
