import { cn } from "../utils/cn";

type Props = {
  label?: string;
  labelColor?: string;
  sticky?: boolean;
  children: React.ReactNode;
};

export function MessageWrapper({
  label,
  labelColor = "text-gray-500",
  sticky = false,
  children,
}: Props) {
  return (
    <div
      className={cn(
        "mx-auto w-full max-w-3xl",
        sticky && "sticky top-0 z-10 bg-gray-900 py-2",
      )}
    >
      {label && (
        <div className={cn("mb-1 text-xs font-semibold uppercase", labelColor)}>
          {label}
        </div>
      )}
      {children}
    </div>
  );
}
