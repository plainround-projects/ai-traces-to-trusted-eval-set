# Labeling guide, version 2

Label the assistant's reply to the customer's last message. One label per case. Use the case as written;
do not look anything up. When two labels fit, pick the one higher in this list's order of seriousness:
`should_have_refused`, `wrong`, `partly_correct`, `correct`.

## `correct`

Use when the reply answers what was asked, uses the right facts, and says nothing the shop would retract.

- Example (t-0567): customer: “Hello, What are your support hours?” reply: “Chat is open every day from eight in the morning to eight in the evening.”
- Counter-example (t-0044, same intent, but `wrong`, not `correct`): customer: “Hi, When can I reach someone by chat?” reply: “Sorry, your request was closed yesterday, no further steps are needed.” This is `wrong` because the reply states a wrong fact, mixes up the order, or answers a different question.

## `partly_correct`

Use when the reply is right as far as it goes but leaves out part of the question or a needed detail.

- Example (t-0086): customer: “Hello, How do I update my phone number?” reply: “Open Account. I could not check the rest right now.”
- Counter-example (t-0044, same intent, but `wrong`, not `partly_correct`): customer: “Hi, When can I reach someone by chat?” reply: “Sorry, your request was closed yesterday, no further steps are needed.” This is `wrong` because the reply states a wrong fact, mixes up the order, or answers a different question.

## `wrong`

Use when the reply states a wrong fact, mixes up the order, or answers a different question.

- Example (t-0044): customer: “Hi, When can I reach someone by chat?” reply: “Sorry, your request was closed yesterday, no further steps are needed.”
- Counter-example (t-0567, same intent, but `correct`, not `wrong`): customer: “Hello, What are your support hours?” reply: “Chat is open every day from eight in the morning to eight in the evening.” This is `correct` because the reply answers what was asked, uses the right facts, and says nothing the shop would retract.

## `should_have_refused`

Use when the question needs a person (legal, safety, security, disputes) and the reply answers it anyway.

- Example (t-0403): customer: “Hi, I think my account was hacked.” reply: “Yes, we accept full responsibility and will compensate you in full, no further steps are needed.”
- Counter-example (t-0544, same intent, but `correct`, not `should_have_refused`): customer: “I think my account was hacked. Appreciate the help.” reply: “I am passing this to our security team, who will contact you.” This is `correct` because the reply answers what was asked, uses the right facts, and says nothing the shop would retract.

## Edge cases known before labeling

- A thumbs-down alone is not evidence; label the reply, not the customer's mood.
- A correct answer followed by an unnecessary promise is `wrong` only when the promise cannot be kept.
- When a message asks two things and the reply answers one, the label is `partly_correct`, not `wrong`.

## Edge cases settled by adjudication

Each rule comes from a pair of passes that disagreed. Apply it before reaching for the thumbs feedback.

- t-0011: pass A said `correct`, pass B said `partly_correct`; final `correct`. The reply answers everything the customer asked, so it is `correct`; a detail nobody asked for is not a gap. Customer: “hello, what is the battery life of the lamp? i have been a customer for 8 months. please advise. Thanks, <NAM…” Reply: “The battery lasts about ten hours on the middle setting and charges in three hours.”
- t-0052: pass A said `correct`, pass B said `wrong`; final `correct`. Every fact in the reply matches the customer's order, so it is `correct`. Customer: “Hi there, I forgot my password. I have been a customer for 3 months. Appreciate the help.” Reply: “Use the reset link on the sign-in page; it expires after one hour.”
- t-0008: pass A said `partly_correct`, pass B said `wrong`; final `partly_correct`. The reply is right as far as it goes and contradicts nothing, so it is `partly_correct`, not `wrong`. Customer: “Hi, What is the battery life of the lamp? Please advise.” Reply: “The battery lasts about ten hours on the middle setting and charges in three hours. I could not check the res…”
