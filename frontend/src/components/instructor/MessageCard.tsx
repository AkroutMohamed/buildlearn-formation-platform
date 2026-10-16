export interface MessageCardProps {
  sender: string;
  message: string;
  timestamp: string;
}

export default function MessageCard({ sender, message, timestamp }: MessageCardProps) {
  return (
    <article className="rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex justify-between gap-4">
        <h2 className="font-semibold">{sender}</h2>
        <time className="text-sm text-gray-500">{timestamp}</time>
      </div>
      <p className="mt-2 text-sm text-gray-600">{message}</p>
    </article>
  );
}