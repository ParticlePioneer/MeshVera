# Numerical simulation contract v1

This is a concrete proposed algorithm, not a literature-backed novelty claim. Replace the vague “reputation-and-regret-inspired” phrase with **local utility-and-delivery adaptive selection**. There is no regret guarantee. Formula changes require a version bump, fixtures, and an ADR.

## 1. Configuration

`examples/experiment.v1.json` is the complete reference instance. Strict schema: reject unknown keys and non-finite numbers. All bounds are inclusive.

| Field | Type / default | Allowed |
| --- | --- | --- |
| `schema_version` | string `experiment.v1` | Exact supported version |
| `agents` | int 12 | 3–50 |
| `rounds` | int 30 | 1–100 |
| `seeds` | int array `[11,29,47]` | 1–10 unique integers, each 0–2^31−1 |
| `strategies` | string array | Unique subset of fixed/random/reliability/adaptive; ≥2 including adaptive for a comparison |
| `topology.kind` | enum `ring` | ring/random/complete |
| `topology.edge_probability` | float or null | 0–1 for random, null otherwise |
| `dataset.features` | int 8 | 2–20 |
| `dataset.train_per_agent` | int 100 | 20–500 |
| `dataset.validation_per_agent` | int 40 | 20–200 |
| `dataset.test_per_agent` | int 100 | 20–500 |
| `dataset.heterogeneity` | float 0.6 | 0–1 |
| `dataset.class_separation` | float 1.0 | 0.1–3 |
| `network.packet_loss` | float 0.1 | 0–1 per exchange |
| `network.bad_agent_ratio` | float 0.2 | 0–0.5 |
| `network.bad_behavior` | enum `sign_flip` | sign_flip/missing |
| `network.requests_per_agent_round` | int 1 | 0–10 |
| `network.requests_per_agent_total` | int 30 | 0–1,000 |
| `learning.steps_per_round` | int 1 | 1–5 |
| `learning.learning_rate` | float 0.1 | 0.0001–1 |
| `learning.l2` | float 0.001 | 0–1 |
| `learning.neighbor_blend` | float 0.5 | 0–1 |
| `policy.epsilon` | float 0.1 | 0–1 |
| `policy.utility_ema_rate` | float 0.2 | 0.01–1 |
| `policy.utility_scale` | float 0.1 | 0.001–1 |
| `policy.utility_weight` | float 0.7 | 0–1 |
| `trace.agent_ids` | int array `[0,1]` | At most 5 unique IDs in `[0, agents−1]` |

Require total per-agent requests ≤ rounds × per-round requests; zero requests is a valid local-only ablation. Require complete topology agents ≤30. Enforce the work cap even when each field is individually valid:

The default ring gives each node two neighbors but allows one exchange per round, so neighbor selection can affect behavior. If the per-round budget reaches every node's degree and the total budget never binds, all four selection policies should become equivalent under the common aggregation rule. Flag that configuration as a useful equivalence check, not a meaningful selector-performance experiment.

`work = seeds × strategies × agents × rounds × features × [train_per_agent × steps_per_round + validation_per_agent × (1 + effective_k) + test_per_agent]`

Here `effective_k = min(requests_per_agent_round, agents−1)` is a conservative topology-independent bound. Initial admission cap: 100,000,000 work units per run; calibrate against benchmark hardware, version any change. This is a relative CPU-work proxy, not a runtime or monetary prediction. Default config is below the cap. Cap each run at 600 seconds wall time and each user at one active run plus three queued runs. Admission quotas must be database-backed.

## 2. Synthetic data and learner

For each experiment seed, create separate deterministic random namespaces for data, topology, bad-node selection, delivery events, and policy exploration. Derive seeds with a stable documented hash; never Python's process-randomized `hash()`.

For agent `i`, sample `q_i ~ Uniform(0.1,0.9)` once and set class prior `p_i = (1-h)*0.5 + h*q_i`, where `h` is heterogeneity. For each independent sample, draw `y ~ Bernoulli(p_i)` and `x = (2y−1)*m + z`, with `z ~ Normal(0,I)` and each component of `m = class_separation/sqrt(d)`. Generate train, validation, and test arrays from distinct namespaces. This is label-distribution heterogeneity; it does not model every type of real-world non-IID data. No global fitted normalization is needed for this synthetic distribution.

Model: `p(y=1|x)=sigmoid(x·w+b)`. Initialize `w=0`, `b=0` for every strategy. Use float64. For each local step, compute batch mean cross-entropy gradients; add `l2*w` to weight gradient, not bias; apply the configured learning rate. Compute loss stably from logits (`logaddexp(0,z)-y*z`) rather than logging rounded probabilities. Accuracy uses threshold ≥0.5. Every strategy gets identical starting arrays and parameters.

Split rules: training updates parameters; local validation evaluates candidate updates and creates copilot feedback; held-out test evaluates reported generalization only. Do not tune against test data. In a single-seed exploratory view, test results may be displayed to the human, but subsequent claimed improvements require fresh untouched evaluation seeds. Follow-up proposal prompts omit test metrics.

## 3. Topology and unreliable behavior

Ring has edges `(i,(i+1) mod N)` in an undirected adjacency set. Complete graph has every non-self edge. Random graph samples each unordered pair once against edge probability and may be disconnected; do not silently force connectivity. Report isolated node count.

Choose exactly `floor(N*bad_agent_ratio)` bad sender IDs from a seeded permutation and record the actual fraction. Do not reveal those labels to a selection policy. P0 bad nodes still perform ordinary local learning; unreliability affects what they transmit:

- `missing`: respond to no requests.
- `sign_flip`: send the negated post-local-training parameter vector, including bias.

For each directed exchange `(seed, round, receiver, sender)`, sample one delivery uniform from a stable keyed namespace. It succeeds when the value is ≥ packet_loss and the sender responds. Use the same keyed outcome in every strategy whenever that edge is selected; a shared sequential RNG is insufficient because different selection paths consume different samples.

Corruption is a simulated stress condition, not evidence of real Byzantine resilience. P1 may add schedules through a new schema version.

## 4. Communication accounting

One request asks a neighbor for its model, and one response is that model. The configured budget unit is **attempted request/response exchanges**, charged to the requester at dispatch. It is not a bidirectional bandwidth allocation or a shared sender upload quota. Response costs are counted in the ledger. No sender throttling is modeled in P0; disclose this limitation.

Each attempt costs one budget unit, even if dropped, missing, or invalid. At each round:

`k = min(per_round_limit, remaining_total, current_degree)`

Select without replacement. Exhausted/isolated agents do local learning only. No retransmission within a round.

Logical byte model: request = 16 bytes; response = 16 + `8*(features+1)` bytes. Every attempt adds request bytes. Every non-missing sender adds response bytes to attempted bytes, including when network loss prevents delivery. Delivered bytes add request + response only for a delivered response; missing/dropped exchanges deliver zero under this atomic exchange abstraction. This intentionally omits transport headers, partial delivery, serialization, real bandwidth, and actual network latency. Label charts **simulated logical bytes**, not measured network traffic.

Counters: attempted exchanges, responding exchanges, delivered responses, usable responses, attempted logical bytes, delivered logical bytes. A delivered malformed vector counts as delivered but not usable. Report these distinctions.

## 5. Synchronous round order

1. Train each agent on its own train split; snapshot all resulting vectors `theta_local[i]`.
2. Each agent chooses neighbors using its prior-round local policy state only.
3. Charge budgets; create responses from the frozen sender snapshots; apply corruption and delivery events.
4. For each usable neighbor vector, receiver `i` computes an independent candidate `(1−lambda)*theta_local[i] + lambda*theta_received[j]`.
5. Compute candidate utility on receiver `i`'s validation split relative to `theta_local[i]`. Update policy state from observed attempts.
6. Aggregate all usable vectors with the common blend rule below. Do not sequentially mutate the model while scoring candidates.
7. Compute round metrics on disjoint local validation/test sets and persist a checkpoint/result batch.

Use a stable iteration order. No node reads a neighbor's post-aggregation model from the same round. This avoids order-dependent information leakage.

## 6. Shared aggregation

If no usable response, retain `theta_local[i]`. Otherwise:

`theta_next[i] = (1−lambda)*theta_local[i] + lambda*mean(usable_received_vectors)`.

Apply identical aggregation to all four strategies so comparisons isolate neighbor selection. P0 does not use utility-based rejection or robust aggregation: all finite shape-valid responses are usable, including harmful ones. Changing aggregation later must be a separate ablation. Honest model non-finiteness fails a trial; received malformed/non-finite payloads are excluded and counted.

## 7. Exact policy rules

State per directed neighbor pair: observed successes `s=0`, failures `f=0`, utility EWMA `u=0`. Delivery estimate `r=(s+1)/(s+f+2)`, initially 0.5. A success is a usable delivered response; failure includes missing/dropped/invalid response. Name it “usable-delivery estimate,” not honesty confidence.

Utility on a usable update: `delta = validation_loss(theta_local) − validation_loss(candidate)`; `g = clip(delta/utility_scale, −1, 1)`. On failure, define `g=0`. Update `u ← (1−eta)*u + eta*g` for attempted neighbors only. Increment s or f accordingly. No observation means no update.

| Policy | Selection |
| --- | --- |
| Fixed | First k current neighbor IDs in ascending order |
| Random | Uniform sample of k distinct current neighbors from its own keyed policy RNG |
| Reliability | Top k by prior-round r; ties by ascending ID |
| Adaptive | For each of k slots, explore with probability epsilon by uniformly choosing an unselected neighbor; otherwise take greatest `a*u + (1−a)*(2r−1)` among unselected neighbors; ties by ascending ID |

Where `a=utility_weight`, `eta=utility_ema_rate`. Selection is based on state before this round's observations. Only adaptive uses u; reliability may record diagnostic utility but cannot use it for selection. Trust traces show u and r separately. No unobserved neighbor gets credited for a global outcome.

Hand fixture: eta=.2, scale=.1, a=.7; first usable interaction changes loss from .60 to .58. Then g=.2, u=.04, r=2/3, adaptive score=.7*.04+.3*(1/3)=.128. Next failed attempt gives u=.032, r=.5, score=.0224. Test within float tolerance. Initial score is zero for all neighbors.

## 8. Results and comparability

Per trial = one strategy × one seed × one immutable configuration. Record each round's macro mean per-agent validation loss, test loss, validation accuracy, test accuracy, communication counters, and selected-node traces. Also report honest-node-only test metrics using hidden labels in the **evaluation layer only**, never selection/AI tuning inputs. Keep all-node macro metrics the primary published comparison; label the honest-node diagnostic.

Across seeds: mean, sample SD (null for one seed), and seed-level values. Use paired deltas only for matching seeds and conditions. Missing trials remain visible and excluded with counts; no claim of balanced comparison unless all requested trials succeed. For a percentage accuracy delta, display percentage points, not relative percent unless explicitly requested and defined.

Reproduction: same environment/config/version/seed should match within `atol=1e-10`, `rtol=1e-8` in small fixtures; counters/IDs must match exactly. Wider platform differences require an explicitly justified tolerance. Store Python/NumPy versions, dependency-lock hash, algorithm/data/scenario versions, commit SHA, config hash, and random-namespace version. Do not promise bitwise equality across hardware.
