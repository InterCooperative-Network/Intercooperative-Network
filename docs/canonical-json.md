Canonical JSON rules (ICN Demo)

- Sort all object keys lexicographically
- No extra spaces: separators are "," and ":"
- UTF-8 encoding, ensure_ascii=false
- Arrays keep order

Rationale

Signatures must be deterministic across platforms and languages. By fixing the
serialization, the same semantic payload produces the same bytes and the same
signature.

Example

Input (any key order is acceptable):

{"b":2, "a":1}

Canonicalized string:

{"a":1,"b":2}


