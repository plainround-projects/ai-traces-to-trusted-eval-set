# Hashing with SHA-256 (hashlib)

## What it is

A *hash function* turns any data into a short fixed-size fingerprint. SHA-256 gives 64 hexadecimal characters. The same input always gives the same fingerprint; a one-character change gives a completely different one; and you cannot get the input back from the fingerprint. Python's `hashlib` module provides it.

## Why this repository uses it

The eval set must be reproducible and tamper-evident. A SHA-256 of every file goes into the manifest, so `rebuild-check` can prove that a rebuild from the same traces and seed gives identical files. The deduplication stage hashes normalised text so exact duplicates are found with one comparison. The recorded model replies are keyed by a hash of the request.

## Where it appears

| File | What it does with Hashing with SHA-256 (hashlib) |
| --- | --- |
| `src/eval_set_builder/domain/dedup.py` | hashes text with SHA-256 |
| `src/eval_set_builder/infrastructure/cassette.py` | hashes text with SHA-256 |
| `src/eval_set_builder/infrastructure/workspace.py` | hashes files with SHA-256 |

## How it works underneath

`hashlib.sha256(data).hexdigest()` takes bytes (not text; text is encoded first, here as UTF-8) and returns the fingerprint as text. Because the output is fixed-size and practically unique, programs use hashes for several jobs: to detect that a file changed, to key a cache by its input, to chain records so that editing one breaks all later ones, and to store a password-like token without keeping the token itself.

Every repository here uses SHA-256 for the purposes shown in the walkthrough. A hash is not encryption (nothing is hidden or recoverable) and not, by itself, proof of who wrote the data; for that a *keyed* hash such as HMAC is used (see the HMAC note where it applies).

## Walkthrough of this repository's use

### `src/eval_set_builder/domain/dedup.py`

The function's docstring (left out of the listing) says: *The hash that two client retries of one message share.*

```python
def exact_key(text: str) -> str:
    return hashlib.sha256(normalize(text).encode()).hexdigest()
```

- `def exact_key(text: str) -> str:`: The function `exact_key`.
- `return hashlib.sha256(normalize(text).encode()).hexdigest()`: `hashlib.sha256(DATA)` computes the SHA-256 hash of the bytes `DATA`; `.hexdigest()` writes it as 64 hexadecimal characters. `DATA` here is `normalize(text).encode()`.

### `src/eval_set_builder/infrastructure/cassette.py`

The function's docstring (left out of the listing) says: *Hash of everything that decides the reply: model, prompt version, system text, user text, token cap.*

```python
def request_key(model_id: str, request: ModelRequest) -> str:
    payload = json.dumps(
        [model_id, request.prompt_version, request.system, request.user, request.max_tokens], ensure_ascii=False
    )
    return hashlib.sha256(payload.encode()).hexdigest()
```

- `def request_key(model_id: str, request: ModelRequest) -> str:`: The function `request_key`.
- `payload = json.dumps(`: Turns the structure into JSON text (the same data always gives the same text, because the value is a list, whose order is fixed), and therefore the same hash.
- `[model_id, request.prompt_version, request.system, request.user, request.max_tokens], ensure_ascii=False`: Another line of the function (a statement or a continuation of the one above).
- `return hashlib.sha256(payload.encode()).hexdigest()`: `hashlib.sha256(DATA)` computes the SHA-256 hash of the bytes `DATA`; `.hexdigest()` writes it as 64 hexadecimal characters. `DATA` here is `payload.encode()`.

### `src/eval_set_builder/infrastructure/workspace.py`

The function's docstring (left out of the listing) says: *SHA-256 of the file's bytes, in hex.*

```python
    def digest(self, name: str) -> str:
        return hashlib.sha256(self._path(name).read_bytes()).hexdigest()
```

- `def digest(self, name: str) -> str:`: The function `digest`.
- `return hashlib.sha256(self._path(name).read_bytes()).hexdigest()`: `hashlib.sha256(DATA)` computes the SHA-256 hash of the bytes `DATA`; `.hexdigest()` writes it as 64 hexadecimal characters. `DATA` here is `self._path(name).read_bytes()`.

## Try it yourself

Run these from the repository folder (after `make up`).

```bash
python3 -c "import hashlib; print(hashlib.sha256(b'abc').hexdigest())"
```

Prints `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`, the well-known SHA-256 of the three bytes `abc`. Run it twice: always the same.

```bash
python3 -c "import hashlib; print(hashlib.sha256(b'abd').hexdigest())"
```

One character different, a completely different fingerprint.

## Mistakes people make

- Hashing text without fixing the encoding. The code encodes explicitly to UTF-8.
- Joining fields without a separator, so different field splits give the same text (`ab`+`c` and `a`+`bc`). The audit chain uses a separator character that data cannot contain.
- Thinking a short truncated hash is as safe as the full one. Truncated hashes shown in reports are labels for people, not security.
- Using a hash alone to protect a password. Real password storage needs a slow, salted hash.
- Comparing hashes with a timing-leaky check where an attacker could exploit it (the signature check uses a constant-time comparison).

## Check yourself

1. Can you recover the input from a SHA-256 hash?
   *Answer:* No. It is a one-way function.
2. What changes if one character of the input changes?
   *Answer:* The whole hash changes.
3. Why must you encode text to bytes first?
   *Answer:* Hash functions work on bytes, and different encodings give different bytes.
4. What is a hash chain?
   *Answer:* Records where each one includes the hash of the previous one, so any edit breaks every later link.
5. Is a hash the same as encryption?
   *Answer:* No. Nothing is hidden and nothing can be decrypted.

## Further reading

- [hashlib](https://docs.python.org/3.12/library/hashlib.html)
- [FIPS 180-4, the SHA standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final)
