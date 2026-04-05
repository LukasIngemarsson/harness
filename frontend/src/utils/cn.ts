import clsx from "clsx";

export function cn(...args: Parameters<typeof clsx>): string {
  return clsx(args);
}
