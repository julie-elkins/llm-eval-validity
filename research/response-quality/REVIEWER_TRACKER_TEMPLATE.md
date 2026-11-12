# Private reviewer tracker template

This is a template for a local, private tracker. Do not commit a completed
tracker, reviewer names, email addresses, packet contents, completed forms, or
the answer key to this public repository.

## Tracker fields

| field | allowed values or guidance |
|---|---|
| `reviewer_id` | Internal identifier such as `reviewer-01`; never a public name |
| `contact_reference` | Private email or message reference; local only |
| `relevant_experience` | Short private note used for sampling context |
| `packet_version` | Exact reviewer packet version |
| `packet_digest` | Private packet digest, if used |
| `form_version` | Exact form version returned |
| `invited_at` | ISO-8601 timestamp |
| `packet_sent_at` | ISO-8601 timestamp |
| `form_received_at` | ISO-8601 timestamp |
| `case_count` | Number of cases with a submitted judgment |
| `provenance_statement` | `provided`, `not_provided`, or `conflict` |
| `reconciliation_status` | See statuses below |
| `analysis_status` | `eligible`, `incomplete`, `excluded`, or `withdrawn` |
| `follow_up_needed` | Short private action note |

## Reconciliation statuses

- `invited`: interest received, packet not yet sent;
- `packet_sent`: packet delivered, no completed form received;
- `received`: form returned and awaiting private checks;
- `reconciliation_pending`: packet, form, or provenance metadata needs review;
- `eligible`: form passed the private intake gate;
- `incomplete`: form is missing required cases or fields;
- `excluded`: form cannot be used for the stated comparison;
- `withdrawn`: reviewer asked for the form to be removed.

## Minimum private record

Before a form is counted, record:

1. the internal reviewer identifier;
2. packet and form versions;
3. the number of submitted cases;
4. the received date;
5. the reconciliation status;
6. whether the form is eligible for the planned comparison.

Keep reviewer contact information and the completed form in the private
research workspace, not in Git history. The public repository should contain
only this blank process template and aggregate findings after reconciliation.
