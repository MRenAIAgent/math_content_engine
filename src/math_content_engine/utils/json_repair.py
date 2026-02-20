"""Best-effort JSON repair for malformed LLM output.

Provides lightweight fixups for the most common LLM mistakes (trailing /
missing commas, unescaped control characters, truncated output) without
pulling in a heavy third-party library.

Public API
----------
repair_json(raw)            -- apply fixups and parse; raises JSONDecodeError
                               if repair still fails.
parse_json_with_repair(raw) -- try strict parse first, fall back to
                               repair_json, re-raise original error on failure.
"""

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def _escape_ctrl(m: re.Match) -> str:
    """``re.sub`` callback: escape bare control characters inside a JSON
    string value (newlines, tabs, etc.) so the JSON parser won't choke."""
    return m.group(0).replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


def repair_json(raw: str) -> Any:
    """Best-effort repair of malformed JSON from LLMs.

    Only called when ``json.loads`` fails on the raw string.  Applies
    a sequence of lightweight fixups that handle the most common LLM
    mistakes (trailing / missing commas, unescaped control chars,
    truncated output) without pulling in a heavy third-party library.

    Raises ``json.JSONDecodeError`` if repair still fails.
    """
    s = raw

    # 1. Remove trailing commas before } or ]  (e.g.  , } -> } )
    s = re.sub(r",\s*([}\]])", r"\1", s)

    # 2. Insert missing commas between } { or } " or ] { patterns
    #    e.g.  } { -> }, {   or  } "key" -> }, "key"
    s = re.sub(r"(\})\s*(\{)", r"\1, \2", s)
    s = re.sub(r"(\})\s*(\")", r"\1, \2", s)
    s = re.sub(r"(\])\s*(\{)", r"\1, \2", s)

    # 3. Fix unescaped newlines / tabs inside string values
    #    Walk through and escape bare control chars within quoted strings.
    #    (Only the simple cases -- not a full parser.)
    s = re.sub(r'(?<=": ")(.*?)(?="[,\s}\]])', _escape_ctrl, s, flags=re.DOTALL)

    # 4. If the JSON is truncated (e.g. max-tokens hit), try to close it.
    #    Count unmatched braces/brackets and append closers.
    open_braces = s.count("{") - s.count("}")
    open_brackets = s.count("[") - s.count("]")
    if open_braces > 0 or open_brackets > 0:
        # --- Strategy A: simple close (strip trailing comma, append closers).
        #     This preserves complete trailing key-value pairs that just
        #     happen to sit at the truncation boundary.
        simple = s.rstrip().rstrip(",")
        for closer_order in (
            "]" * max(open_brackets, 0) + "}" * max(open_braces, 0),
            "}" * max(open_braces, 0) + "]" * max(open_brackets, 0),
        ):
            try:
                return json.loads(simple + closer_order)
            except json.JSONDecodeError:
                pass

        # --- Strategy B: aggressive strip — remove trailing partial
        #     key/value, then drop incomplete objects from arrays.
        s = re.sub(r",?\s*\"[^\"]*$", "", s)
        s = s.rstrip().rstrip(",")
        # If we still have unmatched braces, try removing the last
        # incomplete object from an array (everything after the last
        # complete }, in the innermost array).
        still_open = s.count("{") - s.count("}")
        if still_open > 0:
            last_complete = s.rfind("},")
            if last_complete != -1:
                # Keep everything up to and including the last }, then
                # re-count and close.
                s = s[: last_complete + 1]
                s = s.rstrip().rstrip(",")
        open_braces = s.count("{") - s.count("}")
        open_brackets = s.count("[") - s.count("]")
        s += "]" * max(open_brackets, 0)
        s += "}" * max(open_braces, 0)

    return json.loads(s)


def parse_json_with_repair(raw: str) -> Any:
    """Parse a JSON string, falling back to :func:`repair_json` on failure.

    1. Try ``json.loads(raw)`` (strict).
    2. On ``JSONDecodeError``, attempt :func:`repair_json`.
    3. If repair also fails, re-raise the **original** ``JSONDecodeError``
       so callers see the most useful diagnostics.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError as first_err:
        logger.info("Strict JSON parse failed (%s), attempting repair...", first_err)
        try:
            result = repair_json(raw)
            logger.info("JSON repair succeeded")
            return result
        except json.JSONDecodeError:
            raise first_err
