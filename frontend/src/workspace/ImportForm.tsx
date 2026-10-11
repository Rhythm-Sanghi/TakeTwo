import { useState } from "react";
import type { FormEvent } from "react";
import { api } from "../api";
import type { ImportRequest, Recording } from "../api";

export function ImportForm({
  recordings,
  onImported,
}: {
  recordings: Recording[];
  onImported: (item: Recording) => void;
}) {
  const [reference, setReference] = useState("");
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const references = recordings.filter((r) => r.role === "reference");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const value = (name: string) => String(data.get(name) || "").trim();
    const selected = references.find((r) => r.id === reference);
    const rightsCleared = data.get("rightsCleared") === "on";
    const metadata: ImportRequest = {
      metadata: {
        family_id: selected?.family_id ?? value("family"),
        speaker_id: value("speaker"),
        origin: selected ? "self_recorded" : "source",
        channel:
          value("channel") === "" ? null : (Number(value("channel")) as 0 | 1),
        transcript: {
          text,
          language: "en",
          status: "unverified",
          reviewers: [],
          verification_date: null,
          revision: "v1",
        },
        provenance: {
          source_id: value("sourceId"),
          work_id: selected?.provenance.work_id ?? value("workId"),
          source: value("source"),
          source_url: value("url") || null,
          collection_method: selected
            ? "Consented participant recording imported locally"
            : "Public source excerpt imported locally",
          access_date: value("date"),
          excerpt_offset_s: Number(value("offset") || 0),
          baseline_rationale: selected ? null : value("rationale"),
          consent_evidence: selected ? value("consent") : null,
          rights: {
            status: rightsCleared ? "cleared" : "pending",
            holder: value("holder"),
            license_name: value("license"),
            evidence: value("rightsEvidence"),
            attribution: value("attribution"),
            permits_adaptation: rightsCleared,
            permits_redistribution: rightsCleared,
          },
        },
      },
      reference_id: reference || null,
      category: value("category") as ImportRequest["category"],
      severity: Number(value("severity")) as ImportRequest["severity"],
    };
    const body = new FormData();
    body.append("audio", data.get("audio") as File);
    body.append("metadata", JSON.stringify(metadata));
    setBusy(true);
    setSuccess("");
    setError("");
    try {
      const item = await api<Recording>("/recordings", {
        method: "POST",
        body,
      });
      onImported(item);
      setSuccess(
        `Imported ${item.original_filename}. Transcript remains unverified.`,
      );
      form.reset();
      setText("");
      setReference("");
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
      <p>
        WAV / FLAC · 100 MiB · up to 600 s stored. Analysis currently supports
        excerpts up to 30 s.
      </p>
      <label>
        Recording role
        <select
          value={reference}
          onChange={(event) => {
            setReference(event.target.value);
            const item = references.find((r) => r.id === event.target.value);
            if (item) setText(item.transcript.text);
          }}
        >
          <option value="">Public source reference</option>
          {references.map((r) => (
            <option key={r.id} value={r.id}>
              Participant for {r.original_filename}
            </option>
          ))}
        </select>
      </label>
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
        Transcript file (UTF-8 .txt, optional)
        <input
          type="file"
          accept=".txt,text/plain"
          onChange={async (event) => {
            const file = event.target.files?.[0];
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
            } catch {
              setError("Transcript must be valid UTF-8.");
            }
          }}
        />
      </label>
      <label>
        Spoken transcript
        <textarea
          name="transcript"
          required
          maxLength={100000}
          rows={4}
          value={text}
          onChange={(event) => setText(event.target.value)}
        />
      </label>
      <p className="notice">
        Imported text remains unverified. Actual independent reviews are
        required before scoring. Do not omit repeated or additional spoken
        words.
      </p>
      <div className="form-grid">
        {!reference && (
          <label>
            Speech family ID
            <input
              name="family"
              pattern="[A-Za-z0-9][A-Za-z0-9_-]{0,79}"
              required
            />
          </label>
        )}
        <label>
          Speaker ID
          <input
            name="speaker"
            pattern="[A-Za-z0-9][A-Za-z0-9_-]{0,79}"
            required
          />
        </label>
        <label>
          Source ID
          <input
            name="sourceId"
            pattern="[A-Za-z0-9][A-Za-z0-9_-]{0,79}"
            required
          />
        </label>
        {!reference && (
          <label>
            Work ID
            <input
              name="workId"
              pattern="[A-Za-z0-9][A-Za-z0-9_-]{0,79}"
              required
            />
          </label>
        )}
        <label>
          Source title / recording session
          <input name="source" required />
        </label>
        <label>
          Source URL
          <input name="url" type="url" />
        </label>
        <label>
          Access / recording date
          <input name="date" type="date" required />
        </label>
        <label>
          Source excerpt offset (s)
          <input
            name="offset"
            type="number"
            min="0"
            step="any"
            defaultValue="0"
            required
          />
        </label>
        <label>
          Channel
          <select name="channel">
            <option value="">Average channels</option>
            <option value="0">Channel 1</option>
            <option value="1">Channel 2</option>
          </select>
        </label>
      </div>
      {reference ? (
        <label>
          Consent evidence reference
          <input name="consent" required />
        </label>
      ) : (
        <label>
          Reference selection rationale
          <textarea name="rationale" rows={2} required />
        </label>
      )}
      <fieldset>
        <legend>Rights and provenance</legend>
        <div className="form-grid">
          <label>
            Rights holder
            <input name="holder" required />
          </label>
          <label>
            License / permission name
            <input name="license" required />
          </label>
          <label>
            Rights evidence reference
            <input name="rightsEvidence" required />
          </label>
          <label>
            Attribution
            <input name="attribution" required />
          </label>
        </div>
        <label className="check">
          <input type="checkbox" name="rightsCleared" /> I have evidence
          permitting adaptation and public redistribution
        </label>
        <p>
          Unchecked records retain pending rights. Importing does not certify
          permission or publish audio.
        </p>
      </fieldset>
      {reference ? (
        <div className="form-grid">
          <label>
            Intended category
            <select name="category">
              <option value="acceptable">Acceptable alternative</option>
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
            Intent is acquisition metadata, never detected ground truth.
            Acceptable uses severity 0; other categories use 1–3.
          </p>
        </div>
      ) : (
        <>
          <input type="hidden" name="category" value="acceptable" />
          <input type="hidden" name="severity" value="0" />
        </>
      )}
      {success && <p role="status">{success}</p>}
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={busy}>
        {busy ? "Validating recording…" : "Import recording"}
      </button>
    </form>
  );
}
