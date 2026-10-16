interface CourseWizardProps {
  step: number;
  steps: string[];
}

export default function CourseWizard({ step, steps }: CourseWizardProps) {
  return (
    <nav aria-label="Course creation progress">
      <ol className="flex flex-wrap gap-3">
        {steps.map((label, index) => (
          <li key={label} className={`text-sm ${index + 1 === step ? "font-semibold text-red-600" : "text-gray-500"}`}>
            {index + 1}. {label}
          </li>
        ))}
      </ol>
    </nav>
  );
}