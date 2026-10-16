interface CoverProps {
  src: string | null;
  alt?: string;
  className?: string;
}

export default function Cover({ src, alt = "", className = "h-full w-full object-cover" }: CoverProps) {
  if (!src) return null;
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={src} alt={alt} className={className} />
  );
}