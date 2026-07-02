export function formatDate(value?: string | null): string {
  if (!value) return "-";
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

export function shortId(value?: string | null): string {
  if (!value) return "-";
  return value.length > 18 ? `${value.slice(0, 10)}...${value.slice(-6)}` : value;
}
