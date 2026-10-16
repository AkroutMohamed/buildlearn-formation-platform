import StudentSidebar from "@/components/student/shared/StudentSidebar";
import StudentNavbar from "@/components/student/shared/StudentNavbar";
import RoleGuard from "@/components/auth/RoleGuard";

export default function StudentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RoleGuard role="student"><div className="workspace-shell flex min-h-screen">
      {/* Sidebar */}
      <StudentSidebar />

      {/* Main content */}
      <div className="flex min-w-0 flex-col flex-1">
        {/* Navbar */}
        <StudentNavbar />

        {/* Page content */}
        <main className="flex-1 p-5 lg:p-8">
          {children}
        </main>
      </div>
    </div></RoleGuard>
  );
}
