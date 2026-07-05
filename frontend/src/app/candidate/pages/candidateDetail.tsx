import {
  useGetCandidateDetail,
  useSubmitCandidateScore,
  useTriggerAISummary,
} from "../hooks/candidate";
import { useParams, Link } from "react-router";
import { useState } from "react";

export default function CandidateDetail() {
  const { candidate_id } = useParams<{ candidate_id: string }>();
  const targetId = candidate_id ? Number(candidate_id) : 0;

  const { data, isLoading, error } = useGetCandidateDetail(targetId);
  const { mutate: generateSummary, isPending: isGeneratingAI } =
    useTriggerAISummary();
  const handleGenerateAISummary = () => {
    generateSummary(String(targetId), {
      onError: (err) => {
        alert(
          `AI Generation Failed: ${err.message || "An unexpected error occurred."}`,
        );
      },
    });
  };

  // Modal Trigger States
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [category, setCategory] = useState<string>("");
  const [scoreValue, setScoreValue] = useState<string>("");
  const [internalNote, setInternalNote] = useState<string>("");

  const { mutate: submitScore, isPending: isSubmitting } =
    useSubmitCandidateScore();

  if (isLoading)
    return (
      <div className="p-6 text-foreground animate-pulse">
        Loading Profile...
      </div>
    );
  if (error || !data)
    return <div className="p-6 text-destructive">Failed to Load Profile</div>;

  const { candidate, scores } = data;

  const statusStyles: Record<string, string> = {
    new: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    reviewed: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    hired: "bg-green-500/10 text-green-500 border-green-500/20",
    rejected: "bg-red-500/10 text-red-500 border-red-500/20",
    archived: "bg-gray-500/10 text-gray-500 border-gray-500/20",
  };

  const handleScoreSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!category.trim() || !scoreValue)
      return alert("Please fill out all mandatory fields.");

    submitScore(
      {
        candidateId: targetId,
        requestBody: {
          category: category.trim(),
          score: Number(scoreValue),
          note: internalNote.trim() || null,
        },
      },
      {
        onSuccess: () => {
          setCategory("");
          setScoreValue("");
          setInternalNote("");
          setIsModalOpen(false);
        },
        onError: (err) => {
          alert(
            `Failed to log assessment performance: ${err.message || "Validation error"}`,
          );
        },
      },
    );
  };

  return (
    <div className="p-6 space-y-6 w-full max-w-4xl mx-auto relative">
      {/* Action Header bar */}
      <div className="flex items-center justify-between">
        <Link
          to="/candidates"
          className="text-xs font-medium text-muted-foreground hover:text-foreground"
        >
          ← Back to Pipeline
        </Link>

        <button
          onClick={() => setIsModalOpen(true)}
          className="h-9 rounded-md bg-blue-600 dark:bg-blue-500 px-4 text-xs font-medium text-white shadow hover:bg-blue-500 transition-colors"
        >
          + Add Score
        </button>
      </div>

      {/* Profile Info Header */}
      <div className="bg-card text-card-foreground border rounded-xl p-6 shadow-sm flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-foreground dark:text-white">
              {candidate.name}
            </h1>
            <span
              className={`capitalize px-2.5 py-0.5 rounded-full text-xs font-semibold border ${statusStyles[candidate.status] || statusStyles.new}`}
            >
              {candidate.status}
            </span>
          </div>
          <p className="text-sm text-muted-foreground font-medium">
            {candidate.role_applied}
          </p>
        </div>
      </div>

      {/* Expertise Section */}
      <div className="bg-card border rounded-xl p-6 shadow-sm space-y-3">
        <h2 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground">
          Technical Expertise
        </h2>
        <div className="flex flex-wrap gap-1.5">
          {candidate.skills.map((skill) => (
            <span
              key={skill}
              className="px-2 py-1 rounded text-xs font-medium bg-secondary border text-secondary-foreground uppercase dark:text-white"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      {/* Dynamic Assessments List Rendering rating field */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground">
          Assessment Performance
        </h2>
        {scores.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {scores.map((score) => (
              <div
                key={score.id}
                className="p-4 border rounded-xl bg-card space-y-2 shadow-sm text-foreground dark:text-white"
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">{score.category}</span>
                  <span className="text-sm font-bold bg-primary/10 text-primary px-2.5 py-1 rounded-md">
                    {score.rating} / 5
                  </span>
                </div>
                {score.note && (
                  <p className="text-xs text-muted-foreground border-t pt-1.5 italic">
                    Note: {score.note}
                  </p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="p-6 text-center border border-dashed rounded-xl text-sm text-muted-foreground bg-muted/20">
            No technical scores logged yet. Click "+ Add Score" to log one.
          </div>
        )}
      </div>
      {/* AI Evaluation Summary Panel */}
      <div className="bg-card border rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex justify-between items-center border-b pb-2">
          <h2 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground">
            AI Evaluation Summary
          </h2>
          <button
            onClick={handleGenerateAISummary}
            disabled={isGeneratingAI}
            className="h-7 rounded bg-secondary hover:bg-secondary/80 border text-[11px] font-semibold px-2.5 transition-colors text-foreground dark:text-white disabled:opacity-50"
          >
            {isGeneratingAI
              ? "Processing AI..."
              : candidate.ai_summary
                ? "Regenerate Analysis"
                : "Generate Summary"}
          </button>
        </div>
        <p className="text-sm leading-relaxed text-foreground dark:text-gray-200">
          {candidate.ai_summary ||
            "An AI assessment summary has not been processed for this pipeline candidate yet."}
        </p>
      </div>

      {/* INPUT POPUP MODAL CONTROL OVERLAY */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-card text-card-foreground border rounded-xl p-6 shadow-xl w-full max-w-md space-y-4">
            <div className="flex items-center justify-between border-b pb-2">
              <div>
                <h3 className="text-base font-semibold text-foreground dark:text-white">
                  Log Assessment Score
                </h3>
                <p className="text-xs text-muted-foreground">
                  Evaluate profiles metrics natively
                </p>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-muted-foreground hover:text-foreground text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleScoreSubmit} className="space-y-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-medium text-muted-foreground">
                  Assessment Track Title
                </label>
                <input
                  type="text"
                  placeholder="e.g., Python Architecture, SQL Design"
                  value={category}
                  required
                  onChange={(e) => setCategory(e.target.value)}
                  className="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm text-foreground dark:text-white focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-medium text-muted-foreground">
                  Score Rating (0 - 5)
                </label>
                <input
                  type="number"
                  min="0"
                  max="5"
                  placeholder="4"
                  value={scoreValue}
                  required
                  onChange={(e) => setScoreValue(e.target.value)}
                  className="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm text-foreground dark:text-white focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-medium text-muted-foreground">
                  Evaluation Note (Optional)
                </label>
                <textarea
                  placeholder="Provide context about candidate's score submission..."
                  value={internalNote}
                  onChange={(e) => setInternalNote(e.target.value)}
                  className="min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-1.5 text-sm text-foreground dark:text-white focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="h-9 rounded-md border border-input bg-background px-4 text-xs font-medium text-foreground hover:bg-accent transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="h-9 rounded-md bg-blue-600 dark:bg-blue-500 px-4 text-xs font-medium text-white shadow hover:bg-blue-500 transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? "Saving..." : "Save Score"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
