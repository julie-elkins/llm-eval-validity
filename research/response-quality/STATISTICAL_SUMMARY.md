# Frozen response-quality statistical summary

This report uses 95% Wilson score intervals, which are bounded uncertainty intervals for a proportion. They are descriptive here; they do not turn the fixed synthetic pilot into a population estimate.

| Model | Condition | Outcome | Count | Estimate [95% interval] |
|---|---|---|---:|---:|
| claude-sonnet-5-5 | prompt_plus_local_validation | protocol acceptance | 28/30 | 93.3% [78.7, 98.2] |
| claude-sonnet-5-5 | prompt_plus_local_validation | evidence-contract satisfaction / all attempts | 15/30 | 50.0% [33.2, 66.8] |
| claude-sonnet-5-5 | prompt_plus_local_validation | evidence-contract satisfaction / accepted | 15/28 | 53.6% [35.8, 70.5] |
| claude-sonnet-5-5 | provider_structured_output_plus_local_validation | protocol acceptance | 22/30 | 73.3% [55.6, 85.8] |
| claude-sonnet-5-5 | provider_structured_output_plus_local_validation | evidence-contract satisfaction / all attempts | 12/30 | 40.0% [24.6, 57.7] |
| claude-sonnet-5-5 | provider_structured_output_plus_local_validation | evidence-contract satisfaction / accepted | 12/22 | 54.5% [34.7, 73.1] |
| claude-haiku-5-5 | prompt_plus_local_validation | protocol acceptance | 18/30 | 60.0% [42.3, 75.4] |
| claude-haiku-5-5 | prompt_plus_local_validation | evidence-contract satisfaction / all attempts | 9/30 | 30.0% [16.7, 47.9] |
| claude-haiku-5-5 | prompt_plus_local_validation | evidence-contract satisfaction / accepted | 9/18 | 50.0% [29.0, 71.0] |
| claude-haiku-5-5 | provider_structured_output_plus_local_validation | protocol acceptance | 9/30 | 30.0% [16.7, 47.9] |
| claude-haiku-5-5 | provider_structured_output_plus_local_validation | evidence-contract satisfaction / all attempts | 3/30 | 10.0% [3.5, 25.6] |
| claude-haiku-5-5 | provider_structured_output_plus_local_validation | evidence-contract satisfaction / accepted | 3/9 | 33.3% [12.1, 64.6] |
| gpt-5.6 | prompt_plus_local_validation | protocol acceptance | 26/30 | 86.7% [70.3, 94.7] |
| gpt-5.6 | prompt_plus_local_validation | evidence-contract satisfaction / all attempts | 15/30 | 50.0% [33.2, 66.8] |
| gpt-5.6 | prompt_plus_local_validation | evidence-contract satisfaction / accepted | 15/26 | 57.7% [38.9, 74.5] |
| gpt-5.6 | provider_structured_output_plus_local_validation | protocol acceptance | 27/30 | 90.0% [74.4, 96.5] |
| gpt-5.6 | provider_structured_output_plus_local_validation | evidence-contract satisfaction / all attempts | 14/30 | 46.7% [30.2, 63.9] |
| gpt-5.6 | provider_structured_output_plus_local_validation | evidence-contract satisfaction / accepted | 14/27 | 51.9% [34.0, 69.3] |

## Paired comparison status

The paired comparison is not computed from this file. The public artifact has aggregate counts only, and aggregate counts do not identify which matched scenario/replicate outcomes changed between conditions. The required private-input contract is documented in [PAIRED_ANALYSIS_SPEC.md](PAIRED_ANALYSIS_SPEC.md).

No provider runs, prompts, responses, or private traces are emitted by this analysis.
