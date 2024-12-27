import { JobListing } from "./JobListing";
import { ApplicationForm } from "./ApplicationForm";

const jobs = [
  {
    title: "Founding Member (Head of AI)",
    qualifications: [
      "Experience with NLP models",
      "Strong understanding of data science and engineering",
      "At least 1 year of hands-on experience (projects, research, or internship)",
    ],
  },
  {
    title: "Founding Member (CTO)",
    qualifications: [
      "Experience with fullstack and app development",
      "Strong understanding of frontend, databases, and DevOps",
      "At least 1 year of hands-on experience (projects, research, or internship)",
    ],
  },
];

export default function CareersPage() {
  return (
    <div className="container mx-auto px-8 py-8 max-w-4xl">
      <h1 className="text-4xl font-bold text-black mb-8 px-4">Careers at Auxiom</h1>
      <div className="space-y-8 mb-12">
        {jobs.map((job, index) => (
          <JobListing
            key={index}
            title={job.title}
            qualifications={job.qualifications}
          />
        ))}
      </div>
      <div className="flex items-center justify-center px-4">
        <div className="max-w-2xl w-full space-y-8">
          <h2 className="text-2xl font-semibold text-black mb-6">
            Apply for a Position
          </h2>
          <ApplicationForm />
        </div>
      </div>
    </div>
  );
}
