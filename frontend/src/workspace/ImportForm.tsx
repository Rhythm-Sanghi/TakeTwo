import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { api, post } from "../api";
import type { Recording } from "../api";
import type { components } from "../api.generated";

type Upload = components["schemas"]["LocalImportRequest"];
export function ImportForm({
  maximumDuration,
  recordings,
  onImported,
  participantFor = "",
  schemaVersion = 2,
  onUpgraded,
}: {
  maximumDuration?: number;
  recordings: Recording[];
  onImported: (item: Recording) => void | Promise<void>;
  participantFor?: string;
  schemaVersion?: number;
  onUpgraded?: () => void;
}) {
  const [type, setType] =
    useState<Upload["recording_type"]>("public_reference");
  const [reference, setReference] = useState("");
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const references = recordings.filter((r) => r.role === "reference");
  const participant = type === "human_participant";
  useEffect(() => {
    if (participantFor) {
      setType("human_participant");
      setReference(participantFor);
      setText(
        recordings.find((r) => r.id === participantFor)?.transcript.text ?? "",
      );
    }
  }, [participantFor, recordings]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const value = (key: string) => String(data.get(key) ?? "").trim();
    const cleared = data.get("rightsCleared") === "on";
    const hasRights =
      cleared ||
      ["holder", "license", "rightsEvidence", "attribution"].some((k) =>
        value(k),
      );
    const metadata: Upload = {
      recording_type: type,
      transcript: text,
      title: value("title") || null,
      reference_id: participant ? reference || null : null,
      local_permission: data.get("localPermission") === "on",
      speaker_label: value("speaker") || null,
      same_speaker_as_reference:
        participant && data.get("sameSpeaker") === "on",
      source_url: value("url") || null,
      rationale: value("rationale") || null,
      consent_evidence: value("consent") || null,
      channel:
        value("channel") === "" ? null : (Number(value("channel")) as 0 | 1),
      category: (value("category") || "unspecified") as Upload["category"],
      severity:
        !value("category") || value("category") === "unspecified"
          ? null
          : (Number(value("severity") || 0) as Upload["severity"]),
      rights: hasRights
        ? {
            status: cleared ? "cleared" : "pending",
            holder: value("holder") || null,
            license_name: value("license") || null,
            evidence: value("rightsEvidence") || null,
            attribution: value("attribution") || null,
            permits_adaptation: cleared,
            permits_redistribution: cleared,
          }
        : null,
    };
    const file = data.get("audio") as File;
    if (file.size > 104857600) {
      setError("Audio exceeds 100 MiB. Choose a shorter WAV or FLAC.");
      return;
    }
    const body = new FormData();
    body.append("audio", file);
    body.append("metadata", JSON.stringify(metadata));
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const item = await api<Recording>("/recordings", {
        method: "POST",
        body,
      });
      await onImported(item);
      setSuccess(
        `Imported ${item.original_filename}. Text is unverified; public rights remain ${item.provenance.rights.status}.`,
      );
      form.reset();
      if (!participant) setText("");
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form
      onSubmit={submit}
      aria-label="Import recording"
      className="import-form"
    >
      <h2>Import recording</h2>
      {schemaVersion === 1 && (
        <div className="notice">
          <p>
            This older workspace needs explicit support for unknown
            private-draft metadata. Enabling it retains a backup and all
            original audio. Existing reports may need a fresh comparison; no
            reviews are granted.
          </p>
          <button
            type="button"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              setError("");
              try {
                await post("/dataset/upgrade", {});
                onUpgraded?.();
              } catch (cause) {
                setError((cause as Error).message);
              } finally {
                setBusy(false);
              }
            }}
          >
            Enable private draft imports
          </button>
        </div>
      )}
      <p>
        Choose a reference, then add recordings of the same words. WAV / FLAC ·
        100 MiB · up to 600 s stored; analysis uses excerpts up to{" "}
        {maximumDuration ?? "…"} s.
      </p>
      <fieldset disabled={busy}>
        <legend>Recording and transcript</legend>
        <label>
          Recording type
          <select
            value={type}
            onChange={(e) => {
              setType(e.target.value as Upload["recording_type"]);
              setError("");
            }}
          >
            <option value="public_reference">Public source reference</option>
            <option value="controlled_reference">
              Self-recorded controlled reference
            </option>
            <option value="human_participant">
              Human participant recording
            </option>
          </select>
        </label>
        {type === "controlled_reference" && (
          <p className="notice">
            A local practice baseline in your own voice. It does not replace the
            public-speaker reference required for the competition dataset.
          </p>
        )}
        {participant && (
          <>
            <label>
              Compare with reference
              <select
                value={reference}
                required
                onChange={(e) => {
                  setReference(e.target.value);
                  setText(
                    references.find((r) => r.id === e.target.value)?.transcript
                      .text ?? "",
                  );
                }}
              >
                <option value="">Select a reference</option>
                {references.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.provenance.source} · {r.original_filename}
                  </option>
                ))}
              </select>
            </label>
            {!references.length && (
              <p className="notice">
                Import a public or self-recorded reference first. Then return to
                add a participant.
              </p>
            )}
          </>
        )}
        <label>
          Audio file
          <input
            name="audio"
            type="file"
            accept=".wav,.flac,audio/wav,audio/flac"
            required
          />
        </label>
        <label>
          Recording title (optional)
          <input name="title" placeholder="Uses the filename if left empty" />
        </label>
        <label>
          Spoken transcript
          <textarea
            name="transcript"
            required
            maxLength={100000}
            rows={5}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </label>
        <label>
          Transcript file (UTF-8 .txt, optional)
          <input
            type="file"
            accept=".txt,text/plain"
            onChange={async (e) => {
              const file = e.target.files?.[0];
              if (!file) return;
              if (file.size > 400000) {
                setError("Transcript file exceeds 400 kB.");
                return;
              }
              try {
                setText(
                  new TextDecoder("utf-8", { fatal: true }).decode(
                    await file.arrayBuffer(),
                  ),
                );
                setError("");
              } catch {
                setError("Transcript must be valid UTF-8.");
              }
            }}
          />
        </label>
        <p className="notice">
          Imported text remains unverified. Matching pasted text expresses the
          intended relationship; it does not prove which words were spoken.
          Independent reviews are required before scoring.
        </p>
        {participant && (
          <label className="check">
            <input type="checkbox" required />I intend this take to contain the
            same words as the selected reference
          </label>
        )}
        <label className="check">
          <input type="checkbox" name="localPermission" required />I have
          permission to store and process this recording locally
        </label>
        <p className="meta">
          Local processing permission does not grant public redistribution.
          Unknown license and ownership details remain unknown.
        </p>
      </fieldset>
      <details>
        <summary>Source and provenance</summary>
        <label>
          Speaker label (optional)
          <input
            name="speaker"
            placeholder="Use the same label for the same person"
          />
        </label>
        <p className="meta">
          Unspecified speakers stay grouped together; different filenames never
          establish independent people.
        </p>
        {participant && (
          <label className="check">
            <input type="checkbox" name="sameSpeaker" />
            Same speaker as the selected reference
          </label>
        )}
        <label>
          Source URL
          <input name="url" type="url" />
        </label>
        {!participant && (
          <label>
            Reference selection rationale (optional)
            <textarea name="rationale" rows={2} />
          </label>
        )}
        <label>
          Consent evidence reference (optional)
          <input name="consent" />
        </label>
        <p className="meta">
          Keep signed forms and identities private. The system records actual
          import time, not an assumed recording date.
        </p>
      </details>
      <details>
        <summary>Rights and permissions</summary>
        <div className="form-grid">
          {[
            ["holder", "Rights holder"],
            ["license", "License / permission name"],
            ["rightsEvidence", "Rights evidence reference"],
            ["attribution", "Attribution"],
          ].map(([name, label]) => (
            <label key={name}>
              {label}
              <input name={name} />
            </label>
          ))}
        </div>
        <label className="check">
          <input type="checkbox" name="rightsCleared" />I have evidence
          permitting adaptation and public redistribution
        </label>
        <p>
          Clearance requires all four actual rights fields and evidence of both
          uses. Leave this unchecked for private practice with pending public
          rights.
        </p>
      </details>
      <details>
        <summary>Recording details</summary>
        <label>
          Channel
          <select name="channel">
            <option value="">Average channels</option>
            <option value="0">Channel 1</option>
            <option value="1">Channel 2</option>
          </select>
        </label>
        <p>
          Duration, sample rate, channels and content hashes come from decoded
          audio. Originals are preserved.
        </p>
        {participant && (
          <div className="form-grid">
            <label>
              Intended category
              <select name="category">
                <option value="unspecified">No labeled intent</option>
                <option value="acceptable">
                  Intended acceptable alternative
                </option>
                {[
                  "pacing",
                  "pause_behavior",
                  "energy_variation",
                  "pitch_dynamics",
                ].map((c) => (
                  <option key={c} value={c}>
                    {c.replaceAll("_", " ")}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Intended severity
              <select name="severity">
                {[0, 1, 2, 3].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </label>
            <p>
              Acquisition intent is not detected ground truth. Acceptable uses
              0; other categories use 1–3.
            </p>
          </div>
        )}
      </details>
      <details>
        <summary>Controlled synthetic alterations</summary>
        <p>
          Use the dataset generate command with a reproducible recipe and time
          map. A transformed file cannot be imported as a genuine human take.
          Generated artifacts remain explicitly synthetic and need independent
          review.
        </p>
      </details>
      <p role="status" aria-live="polite" aria-atomic="true">
        {busy ? "Validating recording and provenance…" : success}
      </p>
      {error && <p role="alert">{error}</p>}
      <button
        type="submit"
        disabled={busy || schemaVersion === 1 || (participant && !reference)}
      >
        {busy ? "Validating recording…" : "Import recording"}
      </button>
    </form>
  );
}
