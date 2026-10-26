# Stage 1: load and reject

- Raw lines: 1010
- Loaded: 1000
- Rejected: 10
- Rejected lines equal the planted malformed lines: **True**

| Line | Planted kind | Reason |
| --- | --- | --- |
| 54 | null_trace_id | field 'trace_id' must be a non-empty string |
| 203 | trailing_comma | invalid JSON: Illegal trailing comma before end of object: line 1 column 536 (char 535) |
| 235 | not_an_object | a trace must be a JSON object, got list |
| 237 | wrong_type_history | fields 'history', 'retrieved_page_ids' and 'tool_calls' must be lists |
| 693 | garbage_text | invalid JSON: Expecting value: line 1 column 1 (char 0) |
| 729 | empty_message | field 'message' must be a non-empty string |
| 795 | truncated_json | invalid JSON: Unterminated string starting at: line 1 column 54 (char 53) |
| 814 | missing_field | missing fields: reply |
| 929 | empty_line | invalid JSON: Expecting value: line 1 column 1 (char 0) |
| 978 | bad_thumbs | field 'thumbs' must be 'up', 'down' or null, got 'sideways' |
