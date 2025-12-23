# GORE_OS Model Health Report

**Generated:** 2025-12-22T16:29:04.927400

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Health Score** | 60.7/100 |
| Total Atoms | 1468 |
| Total Profunctors | 400 |
| Structural Issues | 56 |
| Semantic Issues | 50 |
| Role-Story Coverage | 62.4% |

---

## 📦 Atoms by Type

| Type | Total | Valid | With URN | With ID | Issues |
|------|-------|-------|----------|---------|--------|
| roles | 410 | 410 | 410 | 410 | 0 |
| stories | 686 | 686 | 658 | 658 | 56 |
| processes | 83 | 83 | 83 | 83 | 0 |
| entities | 122 | 122 | 122 | 122 | 0 |
| modules | 74 | 74 | 74 | 74 | 0 |
| capabilities | 93 | 93 | 93 | 93 | 0 |

---

## 🔗 Profunctors Analysis

- **Total:** 400
- **Core (actor_of, supervisa, etc):** 4
- **Entity Relations:** 381

### Largest Profunctors

- `actor_of.yml`: 135842 bytes
- `governed_by.yml`: 105188 bytes
- `story-capability.yml`: 94913 bytes
- `role-story.yml`: 84465 bytes
- `contribuye.yml`: 30363 bytes

---

## 🚨 Recommendations

- 🔴 CRITICAL: Role-Story coverage is below 70%. Create stories for orphan roles.
- 🟠 HIGH: More than 50 structural issues detected. Run cleanup scripts.
- 🟡 MEDIUM: Multiple potential duplicates found. Review and merge.
- 🟡 MEDIUM: 378 empty profunctors. Populate or remove.

---

## 🔍 Potential Duplicates (Top 10)

| Type | File 1 | File 2 | Similarity |
|------|--------|--------|------------|
| roles | `ito_campo.yml` | `inspector_tecnico_obra.yml` | 0.89 |
| roles | `director_sii.yml` | `director_cnr.yml` | 0.86 |
| roles | `director_sii.yml` | `director_vialidad.yml` | 0.85 |
| roles | `director_sii.yml` | `director_sence.yml` | 0.86 |
| roles | `director_sii.yml` | `director_sag.yml` | 0.9 |
| roles | `director_sii.yml` | `director_junji.yml` | 0.86 |
| roles | `director_sii.yml` | `director_doh.yml` | 0.86 |
| roles | `director_sii.yml` | `director_ind.yml` | 0.9 |
| roles | `director_sii.yml` | `director_serviu.yml` | 0.89 |
| roles | `director_sii.yml` | `director_dga.yml` | 0.86 |