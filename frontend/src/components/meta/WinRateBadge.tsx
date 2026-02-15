"use client";

interface WinRateBadgeProps {
  rate: number;
  size?: "sm" | "md";
}

export function WinRateBadge({ rate, size = "md" }: WinRateBadgeProps) {
  const colorClass =
    rate > 55
      ? "bg-green-100 text-green-800 border-green-300"
      : rate >= 45
        ? "bg-yellow-100 text-yellow-800 border-yellow-300"
        : "bg-red-100 text-red-800 border-red-300";

  const sizeClass =
    size === "sm"
      ? "text-xs px-1.5 py-0.5"
      : "text-sm px-2.5 py-1";

  return (
    <span
      className={`inline-flex items-center font-semibold rounded-full border ${colorClass} ${sizeClass}`}
    >
      {rate.toFixed(0)}%
    </span>
  );
}
