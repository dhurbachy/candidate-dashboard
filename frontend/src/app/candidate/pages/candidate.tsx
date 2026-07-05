import { DataTable } from "../components/dataTable";
import { Link } from "react-router";
import { useGetCandidates } from "../hooks/candidate";
import type { CandidateListItem } from "../../../services/candidates-services";
import { useState } from "react";

// Extended type definition inline to support the new vacation property
interface ExtendedCandidateListItem extends CandidateListItem {
  vacation_status?: "active" | "scheduled" | "none";
  vacation_start?: string;
  vacation_end?: string;
}

export default function Candidate() {
  const [keyword, setKeyword] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [page, setPage] = useState<number>(1);
  const pageSize = 10;

  // 3. Bind the Data Fetching Hook Engine
  const { data, isLoading, isError, error, refetch } = useGetCandidates({
    page,
    pageSize,
    keyword: keyword || null,
    status: status || null,
  });

  // Extract variables with proper fallback states
  const candidateList =
    (data?.items as unknown as ExtendedCandidateListItem[]) || [];
  const totalItems = data?.total || 0;
  const totalPages = Math.ceil(totalItems / pageSize) || 1;

  // Handle mock delete interaction
  const handleDelete = (id: string | number) => {
    if (
      confirm(
        "Are you sure you want to remove this candidate from the pipeline?",
      )
    ) {
      // Execute your delete mutation hook/API call logic here
      console.log(`Delete candidate sequence initiated for ID: ${id}`);
    }
  };

  const columns = [
    {
      accessorKey: "name",
      header: "Candidate Name",
      cell: ({ row }) => (
        <Link
          to={`/candidates/${row.original.id}/detail`}
          className="font-medium text-blue-500 dark:text-blue-400 hover:underline"
        >
          {row.getValue("name")}
        </Link>
      ),
    },
    {
      accessorKey: "role_applied",
      header: "Role Applied",
    },
    {
      accessorKey: "skills",
      header: "Key Skills",
      cell: ({ row }) => {
        const skills: string[] = row.getValue("skills") || [];
        return (
          <div className="flex flex-wrap gap-1 max-w-[250px]">
            {skills.slice(0, 3).map((skill) => (
              <span
                key={skill}
                className="px-1.5 py-0.5 rounded text-[11px] bg-secondary border text-secondary-foreground"
              >
                {skill}
              </span>
            ))}
            {skills.length > 3 && (
              <span className="text-xs text-muted-foreground self-center">
                +{skills.length - 3}
              </span>
            )}
          </div>
        );
      },
    },
    {
      accessorKey: "status",
      header: "Pipeline Status",
      cell: ({ row }) => {
        const status = row.getValue("status") as string;
        const styles: Record<string, string> = {
          new: "bg-blue-500/10 text-blue-500 border-blue-500/20",
          reviewed: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
          hired: "bg-green-500/10 text-green-500 border-green-500/20",
          rejected: "bg-red-500/10 text-red-500 border-red-500/20",
          archived: "bg-gray-500/10 text-gray-500 border-gray-500/20",
        };
        return (
          <span
            className={`capitalize px-2 py-0.5 rounded-full text-xs font-medium border ${styles[status] || styles.new}`}
          >
            {status}
          </span>
        );
      },
    },
    {
      accessorKey: "vacation_status",
      header: "Vacation",
      cell: ({ row }) => {
        const status = (row.original.vacation_status || "none") as string;
        const start = row.original.vacation_start;
        const end = row.original.vacation_end;

        if (status === "none") {
          return <span className="text-xs text-muted-foreground">—</span>;
        }

        return (
          <div className="flex flex-col gap-0.5">
            <span
              className={`w-fit px-1.5 py-0.5 rounded text-[11px] font-medium border ${
                status === "active"
                  ? "bg-orange-500/10 text-orange-600 border-orange-500/20 dark:text-orange-400"
                  : "bg-purple-500/10 text-purple-600 border-purple-500/20 dark:text-purple-400"
              }`}
            >
              {status === "active" ? "On Leave" : "Scheduled"}
            </span>
            {start && end && (
              <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                {start} to {end}
              </span>
            )}
          </div>
        );
      },
    },
    {
      id: "actions",
      header: () => <div className="text-right">Actions</div>,
      cell: ({ row }) => (
        <div className="flex items-center justify-end gap-3">
          <Link
            to={`/candidates/${row.original.id}/detail`}
            className="text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            View Detail
          </Link>
          <button
            onClick={() => handleDelete(row.original.id)}
            className="text-xs font-medium text-destructive hover:text-destructive/80 transition-colors"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-4 w-full">
      {/* View Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight">
          Candidates Pipeline
        </h1>
        <p className="text-sm text-muted-foreground">
          Monitor technical assessments and candidate lifecycle tracks.
        </p>
      </div>

      {/* Control Filter Bar */}
      <div className="flex flex-wrap gap-2 items-center justify-between bg-card p-3 rounded-lg border">
        <div className="flex flex-1 items-center gap-2 max-w-sm">
          <input
            type="text"
            placeholder="Search by candidate name..."
            value={keyword}
            onChange={(e) => {
              setKeyword(e.target.value);
              setPage(1);
            }}
            className="h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className="h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring transition-colors duration-200
               dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100 dark:focus-visible:ring-zinc-400"
          >
            {/* Explicit text coloring prevents invisible dark text on dark backgrounds */}
            <option
              value=""
              className="bg-white text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100"
            >
              All Statuses
            </option>
            <option
              value="new"
              className="bg-white text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100"
            >
              New
            </option>
            <option
              value="reviewed"
              className="bg-white text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100"
            >
              Reviewed
            </option>
            <option
              value="hired"
              className="bg-white text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100"
            >
              Hired
            </option>
            <option
              value="rejected"
              className="bg-white text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100"
            >
              Rejected
            </option>
            <option
              value="archived"
              className="bg-white text-zinc-900 dark:bg-zinc-900 dark:text-zinc-100"
            >
              Archived
            </option>
          </select>
        </div>
      </div>

      {/* Conditional UI Content Block */}
      {isLoading ? (
        <div className="w-full border rounded-lg p-4 space-y-3 bg-card intense-pulse animate-pulse">
          <div className="h-8 bg-muted rounded w-full mb-4" />
          {Array.from({ length: 5 }).map((_, idx) => (
            <div key={idx} className="flex gap-4 items-center">
              <div className="h-5 bg-muted rounded w-1/6" />
              <div className="h-5 bg-muted rounded w-1/6" />
              <div className="h-5 bg-muted rounded w-1/6" />
              <div className="h-5 bg-muted rounded w-1/6" />
              <div className="h-5 bg-muted rounded w-1/6" />
              <div className="h-5 bg-muted rounded w-1/6" />
            </div>
          ))}
        </div>
      ) : isError ? (
        <div className="w-full border border-destructive/20 rounded-lg p-6 bg-destructive/5 text-center flex flex-col items-center justify-center gap-3">
          <div className="text-destructive font-medium">
            Failed to load candidates
          </div>
          <p className="text-sm text-muted-foreground max-w-md">
            {error instanceof Error
              ? error.message
              : "An unexpected network error occurred. Please try again."}
          </p>
          <button
            onClick={() => refetch?.()}
            className="mt-2 inline-flex h-8 items-center justify-center rounded-md bg-destructive px-3 text-xs font-medium text-destructive-foreground shadow hover:bg-destructive/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            Retry Connection
          </button>
        </div>
      ) : (
        <>
          <DataTable columns={columns} data={candidateList} />

          {/* Pagination Controls */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 border rounded-lg bg-card px-4 py-3">
            <p className="text-sm text-muted-foreground">
              Showing{" "}
              <span className="font-medium text-foreground">
                {candidateList.length === 0 ? 0 : (page - 1) * pageSize + 1}
              </span>{" "}
              to{" "}
              <span className="font-medium text-foreground">
                {Math.min(page * pageSize, totalItems)}
              </span>{" "}
              of <span className="font-medium text-foreground">{totalItems}</span>{" "}
              candidates
            </p>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="h-8 px-3 rounded-md border text-xs font-medium disabled:opacity-40 disabled:cursor-not-allowed hover:bg-muted transition-colors"
              >
                Previous
              </button>

              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter(
                    (p) =>
                      p === 1 ||
                      p === totalPages ||
                      Math.abs(p - page) <= 1,
                  )
                  .reduce<(number | "ellipsis")[]>((acc, p, idx, arr) => {
                    if (idx > 0 && p - (arr[idx - 1] as number) > 1) {
                      acc.push("ellipsis");
                    }
                    acc.push(p);
                    return acc;
                  }, [])
                  .map((p, idx) =>
                    p === "ellipsis" ? (
                      <span
                        key={`ellipsis-${idx}`}
                        className="w-8 h-8 flex items-center justify-center text-xs text-muted-foreground"
                      >
                        …
                      </span>
                    ) : (
                      <button
                        key={p}
                        onClick={() => setPage(p)}
                        className={`w-8 h-8 rounded-md text-xs font-medium border transition-colors ${
                          p === page
                            ? "bg-primary text-primary-foreground border-primary"
                            : "hover:bg-muted"
                        }`}
                      >
                        {p}
                      </button>
                    ),
                  )}
              </div>

              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="h-8 px-3 rounded-md border text-xs font-medium disabled:opacity-40 disabled:cursor-not-allowed hover:bg-muted transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
