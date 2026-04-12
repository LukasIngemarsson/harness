type Props = {
  content: string;
};

export function SystemMessage({ content }: Props) {
  return (
    <div className="text-xs whitespace-pre-wrap text-gray-500">{content}</div>
  );
}
