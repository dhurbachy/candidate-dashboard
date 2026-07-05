import { useGetMe } from "../../auth/hook/login"

export default function Dashboard() {
  const { data, isLoading } = useGetMe()

  if (isLoading) {
    return (
      <div className="p-6 max-w-4xl mx-auto space-y-4 animate-pulse">
        <div className="h-8 bg-muted rounded w-1/4" />
        <div className="h-32 bg-muted rounded-xl w-full" />
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6 w-full max-w-4xl mx-auto text-foreground">
      {/* Header section */}
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight dark:text-white">
          Dashboard
        </h1>
        <p className="text-sm text-muted-foreground">
          Welcome back to your workspace hub.
        </p>
      </div>

      {/* Profile Overview Card */}
      <div className="bg-card text-card-foreground border rounded-xl p-6 shadow-sm">
        <div className="space-y-1">
          <h2 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground">
            Account Status
          </h2>
          <div className="flex items-center gap-2 pt-2">
            <span className="text-xs text-muted-foreground">User Identification Token:</span>
            <code className="text-xs bg-muted px-2 py-0.5 rounded font-mono font-semibold text-foreground dark:text-gray-200">
              {data?.id || "Anonymous Client Session"}
            </code>
          </div>
        </div>
      </div>
    </div>
  )
}
