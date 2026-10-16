/** Decorative architectural artwork; never represents product specifications. */
export default function BlueprintArt({ category = "Gypstant", className = "" }: { category?: string; className?: string }) {
  const tools = category === "Outillage";
  const water = category.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().includes("etanch");
  const accent = tools ? "#e6b16b" : water ? "#76b8b5" : "#e99d89";
  return <svg viewBox="0 0 480 320" className={className} fill="none" aria-hidden="true" focusable="false">
    <rect width="480" height="320" fill="#172b3a" />
    <g stroke="#eef1ed" strokeOpacity=".07">{Array.from({ length: 17 }, (_, i) => <path key={`v${i}`} d={`M${i * 30} 0v320`} />)}{Array.from({ length: 12 }, (_, i) => <path key={`h${i}`} d={`M0 ${i * 30}h480`} />)}</g>
    <circle cx="373" cy="85" r="53" fill={accent} fillOpacity=".1" /><circle cx="373" cy="85" r="37" stroke={accent} strokeOpacity=".5" strokeDasharray="4 6" />
    <path d="m61 231 153-87 205 103-155 87z" fill="#213c49" stroke="#48636b" />
    <path d="m98 212 91-52 121 61-92 53z" fill={accent} fillOpacity=".15" stroke={accent} />
    <path d="M98 212V112l91-53 121 61v101 M189 59v101 M98 112l120 61 92-53 M218 173v101" stroke={accent} strokeWidth="2" />
    <path d="M128 129v101 M158 144v103 M248 157v101 M279 140v103 M98 149l120 60 92-52 M98 182l120 61 92-52" stroke={accent} strokeOpacity=".55" />
    <path d="M189 93l-91 52 M189 127l-91 52 M189 93l121 61 M189 127l121 61" stroke={accent} strokeOpacity=".35" />
    <path d="M64 111v110 M58 111h12 M58 221h12" stroke="#b2c6c8" strokeDasharray="3 4" />
    <g transform="translate(337 165)" stroke={accent} strokeWidth="2.5" strokeLinejoin="round">
      {tools ? <><rect width="62" height="83" rx="8" fill="#172b3a" /><path d="M18 0v-10h26V0 M14 20h34 M14 30h34 m-5 12-15 18h11l-15 17" /></> : water ? <><path d="M31-12C31-12 0 25 0 43a31 31 0 0 0 62 0C62 25 31-12 31-12Z" fill="#172b3a" /><path d="M15 44a16 16 0 0 0 16 16 M5 85h52" /></> : <><path d="m0 0 60-35v76L0 76Z" fill="#172b3a" /><path d="M0 24l60-35 M0 50l60-35 M20-12v75 M40-24v75" /></>}
    </g>
    <g fill={accent}><circle cx="98" cy="112" r="4" /><circle cx="189" cy="59" r="4" /><circle cx="310" cy="120" r="4" /><circle cx="218" cy="274" r="4" /></g>
  </svg>;
}
