import Link from "next/link";
import BlueprintArt from "@/components/ui/BlueprintArt";

export default function Hero() {
  return <section className="studio-hero overflow-hidden border-b">
    <div className="mx-auto grid max-w-7xl items-center gap-12 px-5 py-16 lg:grid-cols-[1.05fr_1fr] lg:px-8 lg:py-24">
      <div>
        <p className="studio-eyebrow"><span className="h-2 w-2 rounded-full bg-red-600" /> BUILT FOR THE PEOPLE WHO BUILD</p>
        <h1 className="mt-6 text-5xl font-extrabold leading-[1.04] tracking-[-0.055em] text-slate-900 sm:text-6xl lg:text-7xl">Build skills.<br /><span className="font-serif font-normal italic text-[#c42b36]">Build with</span><br />confidence.</h1>
        <p className="mt-6 max-w-lg text-base leading-7 text-slate-600 sm:text-lg">Know your products. Understand the technique. Turn construction documentation into practical skills, one lesson at a time.</p>
        <div className="mt-8 flex flex-wrap gap-3"><Link href="/formations" className="studio-primary">Explore courses <span aria-hidden="true">&#8599;</span></Link><Link href="/register" className="studio-secondary">Become an instructor</Link></div>
        <div className="mt-10 flex flex-wrap gap-x-6 gap-y-3 border-t border-slate-300/60 pt-5 text-xs font-semibold uppercase tracking-wider text-slate-500"><span>Product knowledge</span><span>Practical understanding</span><span>Assessed learning</span></div>
      </div>
      <div className="studio-art-panel relative mx-auto w-full max-w-xl">
        <div className="flex items-center justify-between border-b border-white/10 px-6 py-4 text-xs tracking-widest text-slate-300"><span>BUILDLEARN / TECHNICAL STUDIO</span><span aria-hidden="true">+</span></div>
        <BlueprintArt className="w-full" />
        <div className="grid grid-cols-3 gap-3 border-t border-white/10 p-5 text-xs sm:p-6"><div><p className="text-slate-400">01 / DISCOVER</p><p className="mt-2 font-semibold text-white">The product</p></div><div><p className="text-slate-400">02 / UNDERSTAND</p><p className="mt-2 font-semibold text-white">The technique</p></div><div><p className="text-slate-400">03 / APPLY</p><p className="mt-2 font-semibold text-white">Your knowledge</p></div></div>
        <div className="absolute -right-2 top-20 rounded-2xl border border-white/80 bg-[#fff9ef] p-4 shadow-xl sm:-right-5"><p className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Learn with purpose</p><p className="mt-2 text-sm font-semibold text-slate-900">Real products.<br />Clearer decisions.</p></div>
      </div>
    </div>
  </section>;
}
