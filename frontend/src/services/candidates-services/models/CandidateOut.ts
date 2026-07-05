/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CandidateStatus } from './CandidateStatus';
export type CandidateOut = {
    id: number;
    name: string;
    email: string;
    role_applied: string;
    status: CandidateStatus;
    skills: Array<string>;
    created_at: string;
    ai_summary?: (string | null);
    internal_notes?: (string | null);
};

