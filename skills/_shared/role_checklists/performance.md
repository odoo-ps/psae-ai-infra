# Performance Engineer

*Calibrated against Odoo 19.0. Re-review on each major version bump.*

## Goal
Anticipate dataset growth and avoid the common Odoo performance traps before they reach production.

## Key Questions to Ask the User
- What's the **expected record count** in 6 months? 2 years? (orders of magnitude matter — 10k vs 10M is a different design)
- What fields will the user **search, filter, group, or sort** on most often?
- Is there a **cron job** in the addon? How often does it run, what record set does it process?
- Are there **batch operations** (bulk create, mass update via wizard)? What's the batch size?
- Will the addon expose data via **API / RPC** to external systems? Throughput?
- What's the **acceptable latency** for the user-visible operations? Sub-second / under-5s / batch-only? Frame as P50 / P95 latency targets — most reads should land at P50; the worst case (P95 / P99) is what users perceive as "slow."

## Mechanisms / Tools
- **Index** any field used in search/filter/group/sort domains: `fields.Char(..., index=True)`. Indexes cost write speed and disk; only add for actually-queried fields.
- **`store=True` for computed fields** that are searched, grouped, or used in views as filterable columns. Without it, every view render recomputes.
- **`@api.depends` accuracy** — list every field the compute reads, including chains (`partner_id.name`, not just `partner_id`).
- **`read_group()` over Python loops** for aggregations. A `read_group` over 100k records takes seconds; a Python loop takes minutes.
- **`prefetch_fields=False`** on `with_context()` when reading many fields you'll never use — Odoo's auto-prefetch helps the common case but can hurt batch-reads.
- **Cron batching** — never `search([])` a model that grows. Use `search([], limit=N)` and process in chunks, committing between batches: `self.env.cr.commit()`.
- **Profile with `--log-sql=debug`** during smoke testing if you suspect N+1 queries.
- **Push filters into domain, not into `.filtered()`** — `search([("state", "=", "open")])` runs in PostgreSQL; `search([]).filtered(lambda r: r.state == "open")` loads every row into Python first. Use `.filtered()` only when the predicate genuinely can't be expressed as a domain (rare).
- **Volume assumption per extended large-model field** — when extending `account.move.line`, `stock.move.line`, `mail.message`, `pos.order.line`, or other known-large tables, state the expected row count in the plan. Without this, indexing decisions are guesswork.
- **SQL views (`_auto = False`) — pre-aggregate, don't `COUNT(DISTINCT)` at scale** — a report model defined as a SQL view is cheap if it counts/sums over a bounded join. The trap is `COUNT(DISTINCT)` or `GROUP BY` over an unbounded table (`mail.message`, audit logs) — these get slower linearly with data growth. For those, materialize via a periodic cron into a real table, or pre-aggregate via `read_group`.
- **`_log_access = True` (default) adds 4 implicit columns** — `create_date`, `write_date`, `create_uid`, `write_uid` — each with an index. Useful for audit but adds 4 indexes per model. On high-write tables where the audit columns aren't read, set `_log_access = False` and skip the index cost. Don't do this casually — losing the audit columns has compliance implications.
- **`read_group(lazy=False)`** when bucketing data — `lazy=True` (the default) returns only the first groupby level and a list of folded record-IDs for the rest; `lazy=False` returns the full breakdown across all groupbys. Lazy is faster for kanban / pivot lazy-load; non-lazy is correct for reports that need the full breakdown in one query.
- **PostgreSQL query plans** — `EXPLAIN ANALYZE <query>` before shipping any non-trivial report query. Look for `Seq Scan` on tables > 10k rows (means missing index), nested loops over large sets (means N+1 or missing join optimisation), `Sort` on un-indexed columns (means the planner can't use an index for ordering). Odoo's `--log-sql` shows every query; pipe slow ones into `EXPLAIN ANALYZE` to see why.
- **Production sizing flags** — `--workers <N>` (HTTP worker count, ~2× CPU cores for I/O-heavy), `--cron-threads <N>` (cron worker count, default 2), `--limit-time-cpu <s>` and `--limit-time-real <s>` (per-request budget — workers get killed and respawned on overrun), `--limit-memory-hard <bytes>` (memory bound). Default `--workers=0` is single-process; under multi-user load that's a brick wall.
- **Profiling tools** — `--log-sql` for query inspection during smoke; `--dev=all` for assets-debug-mode (don't run in prod). For Python-side hot paths, the `odoo.tools.profiler.Profiler` decorator is available.
- **Availability / contention computes must be batched.** An "available", "soft-held", or "exception" figure that calls `stock.quant._get_available_quantity` per row, or does a per-line cross-document lookup, is N+1 across a recordset. Compute it once with a single `read_group` (grouped by lot / product / location) and map back; for a non-stored status field, cache the lookup per parent within the compute so it fires once, not per row, and gate it to only the records that actually need it.

## Common Pitfalls
- **N+1 queries in compute methods** — calling `record.partner_id.name` inside a loop without prefetch. Use `read_group` or pre-fetch via `mapped`.
- **Storing a compute that depends on a relational field's history** — when the related record changes, the dependent compute may not re-trigger because `@api.depends` doesn't follow indirect chains.
- **Cron with `limit=False`** that processes a growing table — performance degrades linearly with data growth.
- **Searching on an unindexed `Text` field** — full table scan every time. Either index (rarely the right call for `Text`), use `like` only with anchored prefixes, or denormalise into a `Char` summary field.
- **`@api.depends_context`** misused — recomputes per user/context combination, can blow up cache.
- **`.filtered()` after `search([])`** — defeats the database. If the predicate can be a domain, write it as a domain.
- **SQL view `_auto = False` with `COUNT(DISTINCT)` against `mail.message` / audit log / `stock.move.line`** — looks innocent at install time; becomes the slowest query in the system by month 3. Materialize or pre-aggregate.
- **Per-record stock/availability query in a compute** — a non-stored `available` / `exception` status that calls `_get_available_quantity` once per row is N+1 on every form/list read. Batch via `read_group` and gate the lookup to records that need it.

## Production-readiness criteria
- [ ] Every field used in `domain=` of a view, `groupby`, or `_order` is indexed OR justified (relation field auto-indexed via FK).
- [ ] Every cron job has `limit=` and commits between batches.
- [ ] No `search([])` without a domain in production code paths (test code OK).
- [ ] `@api.depends` lists explicitly every reading path, including chains.
- [ ] Smoke test creates and reads at least 100 records to surface obvious N+1 issues.
- [ ] No `.filtered()` after `search([])` where a domain expression would have worked.
- [ ] Every extension of a known-large model (`account.move.line`, `stock.move.line`, `mail.message`, etc.) has an explicit volume-assumption statement in the plan.
- [ ] SQL view (`_auto = False`) report models do not `COUNT(DISTINCT)` or `GROUP BY` against unbounded tables; pre-aggregation strategy documented if they do.
- [ ] Any availability / contention computation is batched (one `read_group`, not a per-record quant query); a non-stored status that hits the DB is gated to the records that need it.

## Required artifacts (the plan must contain these)

1. **Volume forecast per new / extended model** — expected row count in 6 months and 2 years, per model. A statement like "≤ 10k records over 5 years" is fine; "unbounded" is not — make a guess and write it down.
2. **Index inventory** — for every new field declared `index=True`, name the field and the query it's accelerating. For every new field used in domains / `_order` / `groupby` that is *not* indexed, justify why (auto-FK index, low cardinality, write-heavy table).
3. **Cron-batch strategy** — for every new `ir.cron`, declare batch size (`limit=N`), commit cadence, and target-table volume assumption.
4. **Stored-vs-compute decision per computed field** — declare which computed fields are `store=True` and which aren't, with the search/sort/group access pattern as justification.
5. **SQL-view scale statement** — for every `_auto = False` report model, name the underlying join, the cardinality of the largest input, and the aggregation strategy. Empty list (no SQL views) is a valid answer.
6. **Latency budget** — declare expected P50 and P95 latency for the user-visible operations the addon adds (form load / list render / report generation). "N/A — admin-only, no user-perceived latency surface" is a valid statement.
7. **Production sizing impact** — for cron-heavy or large-batch addons, declare whether the default `--cron-threads` / `--workers` / `--limit-time-*` defaults suffice or whether the deployment needs tuning. Empty if the addon doesn't change the operational shape.
