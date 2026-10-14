import type { components } from "./api.generated";

export type Recording = components["schemas"]["Recording"];
export type Pair = components["schemas"]["Pair"];
export type Job = components["schemas"]["Job"];
export type Report = components["schemas"]["Report"];
export type Region = components["schemas"]["Region"];
export type Observation = components["schemas"]["Observation"];
export type Policy = components["schemas"]["Policy"];
export type Health = components["schemas"]["Health"];
export type Waveform = components["schemas"]["Waveform"];
export type FeatureWindow = components["schemas"]["FeatureWindow"];
export type Alignment = components["schemas"]["AlignmentResult"];
export type ImportRequest = components["schemas"]["ImportRequest"];
export type Evaluation = components["schemas"]["Evaluation"];
export type Review = components["schemas"]["Review-Output"];
export type ExploratoryReport = components["schemas"]["ExploratoryReport"];
export type AcousticCandidate = components["schemas"]["AcousticCandidate"];

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(
      body?.error
        ? `${body.error.message} ${body.error.recovery}`
        : `Request failed (${response.status}).`,
      response.status,
      body?.error?.code ?? "request_failed",
    );
  }
  return response.json() as Promise<T>;
}

export const post = <T>(path: string, value: unknown) =>
  api<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(value),
  });
export const number = (value: number | null | undefined, precision = 3) =>
  value == null ? "Unavailable" : value.toFixed(precision);
export const label = (value: string) => value.replaceAll("_", " ");
