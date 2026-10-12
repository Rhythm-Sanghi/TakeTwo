"""Isolated MFA subprocess adapter. Failed tools never produce substitute intervals."""

import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import soundfile as sf

from taketwo.dataset.audio import read_audio, sample_hash, sha256
from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import tokenize
from taketwo.dataset.storage import safe_path

from .contracts import AlignmentConfig, AlignmentResult, Diagnostic, Interval, Provenance
from .limits import maximum_analysis_duration_s


def diagnostic(
    code: str, message: str, recovery: str = "Review prerequisites and retry."
) -> Diagnostic:
    return Diagnostic(code=code, message=message, recovery=recovery)


def execute(
    command: list[str], directory: Path, timeout: float, cancel: threading.Event | None = None
) -> tuple[str, str, int | None]:
    """Bounded log on disk avoids pipe deadlocks. Kill descendants on Windows."""
    log_path = directory / "process.log"
    env = os.environ.copy()
    env.update(
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        MFA_ROOT_DIR=str(directory / "mfa-root"),
    )
    if command and Path(command[0]).is_file():
        prefix = Path(command[0]).parent
        # Native conda entry points require the environment's DLL/bin search path.
        if prefix.name.lower() == "scripts":
            prefix = prefix.parent
        env["PATH"] = os.pathsep.join(
            [
                str(prefix),
                str(prefix / "Scripts"),
                str(prefix / "Library" / "bin"),
                env.get("PATH", ""),
            ]
        )
    status = "succeeded"
    with log_path.open("wb") as stream:
        process = subprocess.Popen(
            command,
            cwd=directory,
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        begin = time.monotonic()
        try:
            while process.poll() is None:
                if cancel is not None and cancel.is_set():
                    status = "cancelled"
                    break
                if time.monotonic() - begin >= timeout:
                    status = "timeout"
                    break
                if log_path.stat().st_size > 8 * 1024 * 1024:
                    status = "failed"
                    break
                time.sleep(0.05)
        except BaseException:
            status = "cancelled"
            raise
        finally:
            if process.poll() is None:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=15,
                        check=False,
                    )
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=15)
    log = log_path.read_bytes()[-65536:].decode("utf-8", errors="replace")
    return status, log, process.returncode


def prerequisites(config: AlignmentConfig) -> list[Diagnostic]:
    issues = []
    executable = config.command[0]
    if not (Path(executable).is_file() or shutil.which(executable)):
        issues.append(diagnostic("missing_executable", f"Cannot locate {executable}."))
    for name, resource in [("model", config.model), ("dictionary", config.dictionary)]:
        path = safe_path(Path(resource.path))
        if not path.is_file():
            issues.append(diagnostic(f"missing_{name}", f"Missing local {name}: {path}."))
        elif sha256(path.read_bytes()) != resource.sha256:
            issues.append(
                diagnostic(f"{name}_hash", f"Local {name} hash differs from configuration.")
            )
    return issues


def preflight(
    text: str, config: AlignmentConfig
) -> tuple[list[str], list[tuple[int, int]], list[str]]:
    tokens, offsets = tokenize(text)
    dictionary = set()
    for line in Path(config.dictionary.path).read_text(encoding="utf-8-sig").splitlines():
        if line.strip() and not line.startswith("#"):
            dictionary.add(re.sub(r"\(\d+\)$", "", line.split()[0]).casefold())
    for index, token in enumerate(tokens):
        replacement = config.replacements.get(token)
        if replacement is not None:
            words, _ = tokenize(replacement)
            if len(words) != 1 or words[0] != replacement:
                raise ValueError(
                    "Replacement must be one normalized spoken token; "
                    "revise transcript for expansions."
                )
            tokens[index] = replacement
    # Single letters, digits and dotted acronyms need an explicit spoken-form decision.
    ambiguous = {
        token
        for token in tokens
        if any(c.isdigit() for c in token) or len(token) == 1 and token not in {"i", "a"}
    }
    abbreviations = {"mr", "mrs", "ms", "dr", "prof", "st", "etc", "vs", "jr", "sr"}
    for token, (start, end) in zip(tokens, offsets, strict=True):
        original = text[start:end]
        if token in abbreviations or (original.isupper() and 1 < len(original) <= 5):
            ambiguous.add(token)
    ambiguous -= set(config.replacements)
    ambiguous -= set(config.replacements.values())
    return tokens, offsets, sorted((set(tokens) - dictionary) | ambiguous)


def parse_textgrid(text: str) -> tuple[list[Interval], list[Interval]]:
    tiers: dict[str, list[Interval]] = {"words": [], "phones": []}
    for tier in re.split(r"item\s*\[\d+\]\s*:", text)[1:]:
        name = re.search(r'name\s*=\s*"([^"]+)"', tier)
        if not name:
            continue
        kind = name.group(1).split(" - ")[-1]
        if kind not in tiers:
            continue
        if tiers[kind]:
            raise ValueError("Multiple speaker tiers are unsupported.")
        for block in re.split(r"intervals\s*\[\d+\]\s*:", tier)[1:]:
            start = re.search(r"xmin\s*=\s*([-+\deE.]+)", block)
            end = re.search(r"xmax\s*=\s*([-+\deE.]+)", block)
            label = re.search(r'text\s*=\s*"((?:[^"]|"")*)"', block)
            if not (start and end and label):
                raise ValueError("Malformed TextGrid interval.")
            value = label.group(1).replace('""', '"').strip()
            if value and value not in {"sil", "sp", "<eps>"}:
                tiers[kind].append(
                    Interval(start_s=float(start.group(1)), end_s=float(end.group(1)), label=value)
                )
    return tiers["words"], tiers["phones"]


def validate_alignment(result: AlignmentResult) -> None:
    tokens, offsets = tokenize(result.original_text)
    if sha256(result.original_text.encode("utf-8")) != result.provenance.original_text_sha256:
        raise ValueError("Original transcript hash differs from alignment provenance.")
    if len(tokens) != len(result.normalized_tokens) or offsets != result.token_offsets:
        raise ValueError("Alignment token mapping differs from original transcript.")
    for intervals in (result.words, result.phones):
        previous = 0.0
        for interval in intervals:
            if not 0 <= previous <= interval.start_s < interval.end_s <= result.duration_s:
                raise ValueError(
                    "Alignment intervals overlap, have zero width or exceed recording bounds."
                )
            previous = interval.end_s
    indices = [w.token_index for w in result.words]
    if any(i is None or i >= len(tokens) for i in indices) or indices != sorted(set(indices)):
        raise ValueError("Invalid word token indices.")
    if any(w.label.casefold() != result.normalized_tokens[w.token_index] for w in result.words):
        raise ValueError("Word labels differ from normalized tokens.")
    if result.status == "succeeded" and (not result.words or indices != list(range(len(tokens)))):
        raise ValueError("Success requires complete ordered word coverage.")
    if result.status in {"succeeded", "partial"}:
        expected = [result.config.replacements.get(token, token) for token in tokens]
        if expected != result.normalized_tokens:
            raise ValueError("Normalized tokens differ from explicit transcript policy.")
    if result.status not in {"succeeded", "partial"} and (result.words or result.phones):
        raise ValueError("Failed attempts cannot expose usable intervals.")


def align(
    audio: Path,
    text: str,
    provenance: Provenance,
    duration: float,
    config: AlignmentConfig,
    cancel: threading.Event | None = None,
) -> AlignmentResult:
    limit = maximum_analysis_duration_s()
    if duration > limit:
        raise DatasetError(
            "analysis_limit", f"Analysis supports at most {limit} seconds.", "Use an excerpt."
        )
    tokens, offsets = tokenize(text)
    result = AlignmentResult(
        provenance=provenance,
        config=config,
        duration_s=duration,
        original_text=text,
        normalized_tokens=tokens,
        token_offsets=offsets,
        status="failed",
        diagnostics=prerequisites(config),
    )
    if result.diagnostics:
        return result
    data, samples, info = read_audio(audio)
    if (
        sha256(data) != provenance.audio_sha256
        or sample_hash(samples[:, 0]) != provenance.sample_sha256
        or info.channels != 1
        or info.sample_rate_hz != 16000
        or info.duration_s != duration
        or sha256(text.encode("utf-8")) != provenance.original_text_sha256
    ):
        result.diagnostics.append(
            diagnostic("input_identity", "Alignment input provenance differs.")
        )
        return result
    if not provenance.transcript_verified:
        result.diagnostics.append(
            diagnostic(
                "transcript_unverified",
                "Alignment is against an unverified draft transcript.",
                "Two independent reviewers must verify the actual spoken words.",
            )
        )
    result.normalized_tokens, result.token_offsets, result.oov = preflight(text, config)
    if result.oov:
        result.diagnostics.append(
            diagnostic(
                "oov_or_ambiguous",
                ", ".join(result.oov),
                "Review abbreviations/numbers; supply pronunciations or correct transcript.",
            )
        )
        return result
    with tempfile.TemporaryDirectory(prefix="taketwo-align-") as directory:
        job = Path(directory)
        try:
            state, version, code = execute(
                [*config.command, "version"], job, min(config.timeout_s, 30), cancel
            )
            result.backend_version = version.strip()
            if state != "succeeded" or code != 0 or config.expected_version != version.strip():
                result.status = state if state in {"timeout", "cancelled"} else "failed"
                result.diagnostics.append(
                    diagnostic("backend_version", "MFA version check failed or drifted.")
                )
                result.log = version
                return result
            corpus, output = job / "corpus", job / "output"
            corpus.mkdir()
            samples, rate = sf.read(audio, dtype="float32")
            sf.write(corpus / "utterance.wav", samples, rate, subtype="PCM_16")
            result.prepared_audio_sha256 = sha256((corpus / "utterance.wav").read_bytes())
            (corpus / "utterance.lab").write_text(
                " ".join(result.normalized_tokens), encoding="utf-8"
            )
            command = [
                *config.command,
                "align",
                str(corpus),
                str(Path(config.dictionary.path).absolute()),
                str(Path(config.model.path).absolute()),
                str(output),
                "--single_speaker",
                "--num_jobs",
                "1",
                "--no_use_mp",
                "--clean",
                "--output_format",
                "long_textgrid",
                "--temporary_directory",
                str(job / "temporary"),
            ]
            state, result.log, code = execute(command, job, config.timeout_s, cancel)
            if state != "succeeded" or code != 0:
                result.status = state if state in {"timeout", "cancelled"} else "failed"
                result.diagnostics.append(
                    diagnostic("execution", f"MFA stopped ({result.status}, exit {code}).")
                )
                return result
            grids = list(output.rglob("*.TextGrid"))
            if len(grids) != 1:
                raise ValueError("Expected exactly one output TextGrid.")
            data = grids[0].read_bytes()
            result.output_sha256 = sha256(data)
            words, phones = parse_textgrid(data.decode("utf-8-sig"))
            cursor = 0
            for word in words:
                # Missing words stay missing; never synthesize their intervals.
                while (
                    cursor < len(tokens)
                    and result.normalized_tokens[cursor] != word.label.casefold()
                ):
                    cursor += 1
                if cursor == len(tokens):
                    raise ValueError("Output has unexpected words or transcript order.")
                word.token_index = cursor
                cursor += 1
            result.words, result.phones = words, phones
            result.status = "succeeded" if len(words) == len(tokens) else "partial"
            if result.status == "partial":
                result.diagnostics.append(
                    diagnostic("coverage", "Some transcript words were not aligned.")
                )
            validate_alignment(result)
        except (OSError, ValueError, DatasetError) as exc:
            result.status, result.words, result.phones = "failed", [], []
            result.diagnostics.append(diagnostic("alignment_error", str(exc)))
    return result
