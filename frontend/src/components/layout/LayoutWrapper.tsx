"use client";

import { usePathname } from "next/navigation";
import Navbar from "./navbar";
import Footer from "./footer";

export default function LayoutWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  const isWorkspaceRoute = pathname.startsWith("/student") || pathname.startsWith("/instructor") || pathname.startsWith("/admin");

  return (
    <>
      {!isWorkspaceRoute && <Navbar />}

      <main>{children}</main>

      {!isWorkspaceRoute && <Footer />}
    </>
  );
}
