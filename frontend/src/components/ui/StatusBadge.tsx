import Badge, { type Tone } from "./Badge";

const map: Record<string, Tone> = {
  Published: "success",
  Draft: "neutral",
  Archived: "warning",
};

export default function StatusBadge({ status }: { status: string }) {
  return <Badge tone={map[status] ?? "neutral"}>{status}</Badge>;
}
