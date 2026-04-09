type Props = {
  content: string;
};

export function UserMessage({ content }: Props) {
  return <div className="whitespace-pre-wrap">{content}</div>;
}
