import os
import glob
import yaml
import networkx as nx
from collections import defaultdict

DIR = "/Users/felixsanhueza/fx_felixiando/gore_os/model/atoms/entities"


def analyze_category():
    g_extends = nx.DiGraph()  # Forest of inheritance
    g_refs = nx.DiGraph()  # Graph of foreign keys

    entities = {}  # id -> {domain, name}

    files = glob.glob(os.path.join(DIR, "*.yml"))

    print(f"Loading {len(files)} entities...")

    # 1. Load Nodes (Objects)
    for fp in files:
        try:
            with open(fp, "r") as f:
                data = yaml.safe_load(f)
                eid = data.get("id")
                if not eid:
                    continue

                domain = data.get("domain", "UNKNOWN")
                entities[eid] = {"domain": domain, "file": os.path.basename(fp)}

                g_extends.add_node(eid, domain=domain)
                g_refs.add_node(eid, domain=domain)

        except Exception as e:
            print(f"Error reading {fp}: {e}")

    # 2. Load Edges (Morphisms)
    for fp in files:
        with open(fp, "r") as f:
            data = yaml.safe_load(f)
            src_id = data.get("id")
            if not src_id:
                continue

            # Morphism: Extends (Subtyping / Monomorphism)
            # A extends B implies A -> B dependency
            if "extends" in data:
                tgt_id = data["extends"]
                if tgt_id in entities:
                    g_extends.add_edge(src_id, tgt_id)
                else:
                    print(f"[DANGLING EXTENDS] {src_id} -> {tgt_id}")

            # Morphism: References (Foreign Keys)
            if "attributes" in data:
                for attr in data["attributes"]:
                    if "fk" in attr:
                        tgt_id = attr["fk"]
                        if tgt_id in entities:
                            g_refs.add_edge(src_id, tgt_id, attr=attr["name"])
                        elif tgt_id.startswith(
                            "ENT-"
                        ):  # Only complain if it looks like an entity
                            print(f"[DANGLING REF] {src_id} -> {tgt_id}")

    # 3. Categorical Analysis

    print("\n=== 1. Compositionality (Cycles) ===")
    cycles = list(nx.simple_cycles(g_refs))
    if cycles:
        print(f"CRITICAL: Found {len(cycles)} cycles in FK graph (Mutual Recursion).")
        for c in cycles:
            print(f"  Cycle: {' -> '.join(c)}")
    else:
        print("PASS: FK Category is Acyclic (DAG). Good for dependency injection.")

    print("\n=== 2. Slice Categories (Inheritance) ===")
    if not nx.is_forest(g_extends):
        print("CRITICAL: Inheritance graph is not a forest (Diamond inheritance?).")
    else:
        roots = [
            n
            for n, d in g_extends.out_degree()
            if d == 0 and g_extends.in_degree(n) > 0
        ]
        print(f"PASS: Valid Slice Structure. Found {len(roots)} root categories:")
        for r in roots:
            subs = len(
                nx.ancestors(g_extends, r)
            )  # ancestors in graph theory vs inheritance direction
            # In my graph A->B means A extends B. So B is root.
            # Ancestors of A are {B}. Ancestors of Root are empty.
            # Wait, descendants in graph terms (if edges point to parent):
            # Predecessors of root are children.
            children_count = len(nx.ancestors(g_extends, r))  # Nodes that point to root
            print(f"  - {r}: {children_count} subtypes")

    print("\n=== 3. Modular/Functorial Layout (Cross-Domain Edges) ===")
    # Count edges (u,v) where domain(u) != domain(v)
    cross_domain = defaultdict(int)
    for u, v in g_refs.edges():
        d_u = entities[u]["domain"]
        d_v = entities[v]["domain"]
        if d_u != d_v:
            cross_domain[f"{d_u}->{d_v}"] += 1

    print(f"Total Cross-Domain Morphisms: {sum(cross_domain.values())}")
    sorted_cross = sorted(cross_domain.items(), key=lambda x: -x[1])
    for link, count in sorted_cross[:10]:
        print(f"  {link}: {count}")

    print("\n=== 4. Connectivity (Islands) ===")
    # Undirected view for connectivity
    g_total = nx.compose(g_extends, g_refs).to_undirected()
    components = list(nx.connected_components(g_total))
    if len(components) > 1:
        print(
            f"WARNING: Disconnected Universe. Found {len(components)} separate islands."
        )
        for i, comp in enumerate(components):
            if len(comp) < 5:
                print(f"  Island {i+1}: {comp}")
    else:
        print("PASS: Fully connected semantic universe.")


if __name__ == "__main__":
    analyze_category()
