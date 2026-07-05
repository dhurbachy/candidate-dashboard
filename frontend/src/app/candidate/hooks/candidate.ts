import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "../../../context/authContext";
import { CandidatesDirectoryEngineService } from "../../../services/candidates-services/services/CandidatesDirectoryEngineService";
import type { CandidateListResponse, ApiError, CandidateDetailResponse, ScoreOut, ScoreCreate, SummaryResponse } from "../../../services/candidates-services";

// Define the arguments accepted by your hook
interface GetCandidatesParams {
  status?: string | null;
  roleApplied?: string | null;
  keyword?: string | null;
  skill?: string | null;
  page?: number;
  pageSize?: number;
}

interface SubmitScorePayload {
  candidateId: number;
  requestBody: ScoreCreate;
}
export const useGetCandidates = (params: GetCandidatesParams) => {
  const { accessToken } = useAuth();
  
  const {
    status = null,
    roleApplied = null,
    keyword = null,
    skill = null,
    page = 1,
    pageSize = 20,
  } = params;

  return useQuery<CandidateListResponse, ApiError>({
    queryKey: ["candidates", { status, roleApplied, keyword, skill, page, pageSize }],
    queryFn: () =>
      CandidatesDirectoryEngineService.getAllCandidatesApiCandidatesGet(
        status,
        roleApplied,
        keyword,
        skill,
        page,
        pageSize
      ),
    placeholderData: (previousData) => previousData,
    staleTime: 1 * 60 * 1000, 
    enabled: !!accessToken,   
  });
};

export const useGetCandidateDetail = (candidateId: number) => {
  const { accessToken } = useAuth();

  return useQuery<CandidateDetailResponse, ApiError>({
    queryKey: ["candidate", candidateId],
    queryFn: () =>
      CandidatesDirectoryEngineService.getCandidateDetailsApiCandidatesCandidateIdGet(
        candidateId
      ),
    enabled: !!accessToken && !!candidateId,
    staleTime: 5 * 60 * 1000,
  });
};

export const useDeleteCandidate = () => {
  const queryClient = useQueryClient();

  return useMutation<void, ApiError, string>({
    mutationFn: (candidateId: string) =>
      CandidatesDirectoryEngineService.archiveCandidateApiCandidatesIdDelete(
        candidateId
      ),
    onSuccess: () => {
      // Invalidate the cache to immediately trigger a clean table re-fetch
      queryClient.invalidateQueries({ queryKey: ["candidates"] });
    },
  });
};

export const useSubmitCandidateScore = () => {
  const queryClient = useQueryClient();

  return useMutation<ScoreOut, ApiError, SubmitScorePayload>({
    mutationFn: ({ candidateId, requestBody }) =>
      CandidatesDirectoryEngineService.submitScoreApiCandidatesCandidateIdScoresPost(
        candidateId,
        requestBody
      ),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["candidate", variables.candidateId] });
    },
  });
};

export const useTriggerAISummary = () => {
  const queryClient = useQueryClient();

  return useMutation<SummaryResponse, ApiError, string>({
    mutationFn: (candidateId: string) =>
      CandidatesDirectoryEngineService.triggerSummaryApiCandidatesCandidateIdSummaryPost(
        candidateId
      ),
    onSuccess: (_, candidateId) => {
      // Refresh the individual candidate dataset cache layer immediately
      queryClient.invalidateQueries({ queryKey: ["candidate", Number(candidateId)] });
    },
  });
};