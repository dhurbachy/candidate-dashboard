/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CandidateDetailResponse } from '../models/CandidateDetailResponse';
import type { CandidateListResponse } from '../models/CandidateListResponse';
import type { ScoreCreate } from '../models/ScoreCreate';
import type { ScoreOut } from '../models/ScoreOut';
import type { SummaryResponse } from '../models/SummaryResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CandidatesDirectoryEngineService {
    /**
     * Get All Candidates
     * @param status
     * @param roleApplied
     * @param keyword
     * @param skill
     * @param page
     * @param pageSize
     * @returns CandidateListResponse Successful Response
     * @throws ApiError
     */
    public static getAllCandidatesCandidatesGet(
        status?: (string | null),
        roleApplied?: (string | null),
        keyword?: (string | null),
        skill?: (string | null),
        page: number = 1,
        pageSize: number = 20,
    ): CancelablePromise<CandidateListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/candidates',
            query: {
                'status': status,
                'role_applied': roleApplied,
                'keyword': keyword,
                'skill': skill,
                'page': page,
                'page_size': pageSize,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Candidate Details
     * @param candidateId
     * @returns CandidateDetailResponse Successful Response
     * @throws ApiError
     */
    public static getCandidateDetailsCandidatesCandidateIdGet(
        candidateId: number,
    ): CancelablePromise<CandidateDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/candidates/{candidate_id}',
            path: {
                'candidate_id': candidateId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Submit Score
     * Attaches evaluation assessment scores cards.
     * Guarantees clean connection isolation boundaries with automated transactional rolling-back.
     * @param candidateId
     * @param requestBody
     * @returns ScoreOut Successful Response
     * @throws ApiError
     */
    public static submitScoreCandidatesCandidateIdScoresPost(
        candidateId: number,
        requestBody: ScoreCreate,
    ): CancelablePromise<ScoreOut> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/candidates/{candidate_id}/scores',
            path: {
                'candidate_id': candidateId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Trigger Summary
     * @param candidateId
     * @returns SummaryResponse Successful Response
     * @throws ApiError
     */
    public static triggerSummaryCandidatesCandidateIdSummaryPost(
        candidateId: string,
    ): CancelablePromise<SummaryResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/candidates/{candidate_id}/summary',
            path: {
                'candidate_id': candidateId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Archive Candidate
     * @param candidateId
     * @returns void
     * @throws ApiError
     */
    public static archiveCandidateCandidatesIdDelete(
        candidateId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/candidates/{id}',
            query: {
                'candidate_id': candidateId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Stream Live Score Cards
     * Real-time Server-Sent Events (SSE) telemetry data pipeline.
     * Streams active assessment updates dynamically over a long-lived HTTP connection.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static streamLiveScoreCardsCandidatesStreamScoresGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/candidates/stream/scores',
        });
    }
}
