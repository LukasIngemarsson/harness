import { cn } from "../utils/cn";

type Props = {
  label?: string;
  labelColor?: string;
  children: React.ReactNode;
};

export function MessageWrapper({
  label,
  labelColor = "text-gray-500",
  children,
}: Props) {
  return (
    <div className="mx-auto w-full max-w-3xl">
      {label && (
        <div className={cn("mb-1 text-xs font-semibold uppercase", labelColor)}>
          {label}
        </div>
      )}
      {children}
    </div>
  );
}
