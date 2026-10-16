"use client";

import Link from "next/link";
import { useState } from "react";

const links = [{ label: "Home", href: "/" }, { label: "Formations", href: "/formations" }, { label: "About", href: "/about" }];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  return <nav className="workspace-navbar sticky top-0 z-40 border-b bg-white/95 px-5 py-4 backdrop-blur lg:px-16" aria-label="Main navigation"><div className="mx-auto flex max-w-7xl items-center justify-between"><Link href="/" className="flex items-center gap-2.5 text-xl font-bold tracking-tight text-slate-900"><span aria-hidden="true" className="studio-brand-mark">B</span>BuildLearn<span className="text-slate-900">.</span></Link><div className="hidden items-center gap-7 text-sm font-medium text-slate-600 md:flex">{links.map(link => <Link className="hover:text-red-600" key={link.href} href={link.href}>{link.label}</Link>)}</div><div className="hidden items-center gap-3 md:flex"><Link href="/login" className="rounded-lg px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100">Login</Link><Link href="/register" className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-700">Create account</Link></div><button className="rounded-lg border p-2 text-slate-700 md:hidden" onClick={() => setOpen(value => !value)} aria-expanded={open} aria-label="Toggle navigation menu">☰</button></div>{open && <div className="mx-auto mt-4 flex max-w-7xl flex-col gap-2 border-t pt-4 md:hidden">{links.map(link => <Link className="rounded-lg px-3 py-2 font-medium text-slate-700 hover:bg-red-50 hover:text-red-700" key={link.href} href={link.href} onClick={() => setOpen(false)}>{link.label}</Link>)}<div className="mt-2 flex gap-2"><Link href="/login" className="rounded-lg border px-4 py-2 text-sm font-semibold">Login</Link><Link href="/register" className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white">Create account</Link></div></div>}</nav>;
}
