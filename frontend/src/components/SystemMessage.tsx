type Props = {
  content: string;
};

export function SystemMessage({ content }: Props) {
  return <div className="text-xs text-gray-500 italic">{content}</div>;
}
