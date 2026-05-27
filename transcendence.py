from fractions import Fraction

import math, numpy as np, os

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

PHI = Fraction(1, 2) * (1 + math.sqrt(5))
BASE = Fraction(1, 12) * (PHI * PHI)


def classify(invariants, will_clip):
    βB = invariants["being_transition"]
    ωE = invariants["evolution_winding"]
    σM = invariants["memory_functor_sign"]
    πR = invariants["resonant_homotopy"]
    ψW = invariants["will_flow_index"]
    Ψ = invariants["stability_index"]
    phase_energy = βB * ωE
    phase_ratio = phase_energy * (Ψ ** (-1))

    if phase_ratio > 1 and σM > 0:
        return "Class T5: Prime Architect (Dimensional Structural Bundle)", "Irreversible"

    if phase_ratio > 1 and σM <= 0:
        return "Class T4: Singular Evolution (Singular Structural Bundle)", "Degenerate"

    if σM < 0 and phase_ratio <= 1:
        return "Class T3: Memory Reversal (Non–Abelian Structural Holonomy Bundle)", "Irreversible"

    if πR != 0 or abs(ψW) > will_clip:
        return "Class T2: Resonant Jump (Resonant Twisted Bundle)", "Semi-Reversible"

    return "Class T1: Continuous Flat (Flat Structural Bundle)", "Reversible"


def compute_field_dynamics(omega):
    omega_vec = np.asarray(omega).reshape(-1)

    I = omega_vec[0] + omega_vec[1]
    T = omega_vec[2] + omega_vec[3]
    Wv = omega_vec[4] + omega_vec[5]

    R = (
        omega_vec[6] * I * T +
        omega_vec[7] * T * Wv +
        omega_vec[8] * Wv * I
    )

    A = (
        omega_vec[9] * I * T * R +
        omega_vec[10] * T * Wv * R +
        omega_vec[11] * R * I * Wv
    )

    return np.array([
        I, I,
        T, T,
        Wv, Wv,
        R, R, R,
        A, A, A,
    ])


def irreversible_projection(action_chain):
    x_pred = np.asarray(action_chain["x_pred"]).reshape(-1)
    b_source0 = np.asarray(action_chain["b_source0"]).reshape(-1)
    prev_coords = b_source0
    curr_coords = x_pred

    state = {
        "I": list(x_pred[0:2]),
        "T": list(x_pred[2:4]),
        "W": list(x_pred[4:6]),
        "R": list(x_pred[6:9]),
        "A": list(x_pred[9:12]),
    }

    w_I = 2 * BASE
    w_T = 2 * BASE
    w_W = 2 * BASE
    w_R = 3 * BASE
    w_A = 3 * BASE

    N_pred = math.sqrt(
        w_I * sum(x * x for x in state["I"]) +
        w_T * sum(x * x for x in state["T"]) +
        w_W * sum(x * x for x in state["W"]) +
        w_R * sum(x * x for x in state["R"]) +
        w_A * sum(x * x for x in state["A"])
    )
    zeta = x_pred / N_pred

    b_pred0 = compute_field_dynamics(x_pred)

    w1 = zeta[0] * b_pred0[0]
    w2 = zeta[1] * b_pred0[1]
    w3 = zeta[2] * b_pred0[2]
    w4 = zeta[3] * b_pred0[3]
    w5 = zeta[4] * b_pred0[4]
    w6 = zeta[5] * b_pred0[5]

    delta_ph_pred = math.sqrt(
        w_I * sum((x - y) * (x - y) for x, y in zip(b_source0[0:2], b_pred0[0:2])) +
        w_T * sum((x - y) * (x - y) for x, y in zip(b_source0[2:4], b_pred0[2:4])) +
        w_W * sum((x - y) * (x - y) for x, y in zip(b_source0[4:6], b_pred0[4:6])) +
        w_R * sum((x - y) * (x - y) for x, y in zip(b_source0[6:9], b_pred0[6:9])) +
        w_A * sum((x - y) * (x - y) for x, y in zip(b_source0[9:12], b_pred0[9:12]))
    )

    c7 = b_pred0[6] * delta_ph_pred
    c8 = b_pred0[7] * delta_ph_pred
    c9 = b_pred0[8] * delta_ph_pred

    w7 = zeta[6] * c7
    w8 = zeta[7] * c8
    w9 = zeta[8] * c9

    g9 = 1 if c9 > 0 else 0

    mu_pred = math.sqrt(
        w_I * sum(x * x for x in b_pred0[0:2]) +
        w_T * sum(x * x for x in b_pred0[2:4]) +
        w_W * sum(x * x for x in b_pred0[4:6]) +
        w_R * sum(x * x for x in b_pred0[6:9]) +
        w_A * sum(x * x for x in b_pred0[9:12])
    )
    absolute_gate_pred = g9

    w10 = zeta[9] * b_pred0[9] * absolute_gate_pred
    w11 = zeta[10] * b_pred0[10] * absolute_gate_pred
    w12 = zeta[11] * b_pred0[11] * absolute_gate_pred

    bottleneck_pred = np.array([
        w1, w2,
        w3, w4,
        w5, w6,
        w7, w8, w9,
        w10, w11, w12,
    ])
    bottleneck_rank = len(bottleneck_pred)

    curr_norm = math.sqrt(
        w_I * sum(x * x for x in curr_coords[0:2]) +
        w_T * sum(x * x for x in curr_coords[2:4]) +
        w_W * sum(x * x for x in curr_coords[4:6]) +
        w_R * sum(x * x for x in curr_coords[6:9]) +
        w_A * sum(x * x for x in curr_coords[9:12])
    )

    bottleneck_norm = math.sqrt(
        w_I * sum(x * x for x in bottleneck_pred[0:2]) +
        w_T * sum(x * x for x in bottleneck_pred[2:4]) +
        w_W * sum(x * x for x in bottleneck_pred[4:6]) +
        w_R * sum(x * x for x in bottleneck_pred[6:9]) +
        w_A * sum(x * x for x in bottleneck_pred[9:12])
    )

    structural_drift = bottleneck_norm - curr_norm
    shift = bottleneck_pred - curr_coords

    action_chain["projection"] = {
        "state": state,
        "zeta": list(zeta),
        "b_pred0": list(b_pred0),
        "delta_ph_pred": delta_ph_pred,
        "c7": c7,
        "c8": c8,
        "c9": c9,
        "g9": g9,
        "mu_pred": mu_pred,
        "absolute_gate_pred": absolute_gate_pred,
        "bottleneck_pred": list(bottleneck_pred),
        "bottleneck_pred_rank": bottleneck_rank,
    }

    connection = curr_coords - prev_coords
    tensor = np.outer(curr_coords, prev_coords) - np.outer(prev_coords, curr_coords)
    raw_norm = np.linalg.norm(tensor)
    barrier_strength = raw_norm * (BASE ** (-1))
    structural_gap = np.linalg.norm(connection)

    prev_norm = np.linalg.norm(prev_coords)
    curr_norm_topology = np.linalg.norm(curr_coords)
    coherence = sum(x * y for x, y in zip(curr_coords, prev_coords)) * ((curr_norm_topology * prev_norm) ** (-1))

    energy_balance = BASE * (structural_drift * Fraction(1, 12))
    omega_measure_A = math.sqrt(w_A * sum(x * x for x in bottleneck_pred[9:12]))
    lyapunov_density = (omega_measure_A * omega_measure_A) + (delta_ph_pred * delta_ph_pred) + (energy_balance * energy_balance)

    invariants_new = {
        "energy_balance": energy_balance,
        "stability_index": (BASE * BASE) * (((BASE * BASE) + lyapunov_density) ** (-1)),
        "being_transition": sum(x - y for x, y in zip(bottleneck_pred[9:12], curr_coords[9:12])),
        "evolution_winding": math.sqrt(w_A * sum((x - y) * (x - y) for x, y in zip(bottleneck_pred[9:12], curr_coords[9:12]))),
        "resonant_homotopy": 1 if np.linalg.norm([x - y for x, y in zip(bottleneck_pred[6:9], curr_coords[6:9])]) != 0 else 0,
        "will_flow_index": math.sqrt(w_W * sum((x - y) * (x - y) for x, y in zip(bottleneck_pred[4:6], curr_coords[4:6]))),
        "memory_functor_sign": 1 if sum(x - y for x, y in zip(bottleneck_pred[6:9], curr_coords[6:9])) >= 0 else -1,
        "omega_measure_A": omega_measure_A,
    }

    topology_new = {
        "barrier_strength": barrier_strength,
        "structural_gap": structural_gap,
        "coherence": coherence,
    }

    trans_action_class, holonomy_class = classify(invariants_new, state["W"][1])

    action = {
        "kind": "sog_irreversible_projection",
        "prev_coords": list(prev_coords),
        "curr_coords": list(curr_coords),
        "next_coords": list(bottleneck_pred),
        "shift": list(shift),
        "fields": {
            "state": state,
            "x_pred": list(x_pred),
            "b_source0": list(b_source0),
            "projection": action_chain["projection"],
            "mu_pred": mu_pred,
        },
        "invariants": {
            "energy_balance": invariants_new["energy_balance"],
            "stability_index": invariants_new["stability_index"],
            "being_transition": invariants_new["being_transition"],
            "evolution_winding": invariants_new["evolution_winding"],
            "resonant_homotopy": invariants_new["resonant_homotopy"],
            "will_flow_index": invariants_new["will_flow_index"],
            "memory_functor_sign": invariants_new["memory_functor_sign"],
            "omega_measure_A": invariants_new["omega_measure_A"],
        },
        "topology_invariants": topology_new,
        "trans_action_class": trans_action_class,
        "holonomy_class": holonomy_class,
        "barrier_strength": barrier_strength,
        "structural_gap": structural_gap,
        "coherence": coherence,
        "structural_drift": structural_drift,
        "bottleneck_vector": list(bottleneck_pred),
        "bottleneck_rank": bottleneck_rank,
    }

    action["history"] = []
    action_chain.clear()
    action_chain.update(action)


def admissible_alignment(action_chain):
    S_pred = list(action_chain["phase_bundle"]["S_pred"])
    S_actual = list(action_chain["phase_bundle"]["S_actual"])
    M = action_chain["phase_bundle"]["M"]
    nabla_T = action_chain["phase_bundle"]["nabla_T"]
    bottleneck_pred = list(action_chain["phase_bundle"]["Phi_pred"])
    bottleneck_actual = list(action_chain["phase_bundle"]["Phi_actual"])

    w_I = 2 * BASE
    w_T = 2 * BASE
    w_W = 2 * BASE
    w_R = 3 * BASE
    w_A = 3 * BASE

    S_aligned_cand = [x + y - z for x, y, z in zip(action_chain["prev_coords"], S_actual, S_pred)]

    connection = [x - y for x, y in zip(S_actual, action_chain["prev_coords"])]
    tensor = np.outer(S_actual, action_chain["prev_coords"]) - np.outer(action_chain["prev_coords"], S_actual)
    raw_norm = np.linalg.norm(tensor)
    barrier_strength = raw_norm * (BASE ** (-1))
    structural_gap = np.linalg.norm(connection)

    prev_norm = np.linalg.norm(action_chain["prev_coords"])
    curr_norm = np.linalg.norm(S_actual)
    coherence = sum(x * y for x, y in zip(S_actual, action_chain["prev_coords"])) * ((curr_norm * prev_norm) ** (-1))

    zeta_norm = math.sqrt(
        w_I * sum(x * x for x in S_aligned_cand[0:2]) +
        w_T * sum(x * x for x in S_aligned_cand[2:4]) +
        w_W * sum(x * x for x in S_aligned_cand[4:6]) +
        w_R * sum(x * x for x in S_aligned_cand[6:9]) +
        w_A * sum(x * x for x in S_aligned_cand[9:12])
    )
    zeta = [x * (zeta_norm ** (-1)) for x in S_aligned_cand]

    b_aligned0 = compute_field_dynamics(S_aligned_cand)
    I = b_aligned0[0]
    T = b_aligned0[2]
    Wv = b_aligned0[4]
    R0 = b_aligned0[6]
    A0 = b_aligned0[9]

    omega_01 = zeta[0] * I
    omega_02 = zeta[1] * I
    omega_03 = zeta[2] * T
    omega_04 = zeta[3] * T
    omega_05 = zeta[4] * Wv
    omega_06 = zeta[5] * Wv

    delta_ph_aligned = math.sqrt(
        w_I * sum((x - y) * (x - y) for x, y in zip(S_aligned_cand[0:2], b_aligned0[0:2])) +
        w_T * sum((x - y) * (x - y) for x, y in zip(S_aligned_cand[2:4], b_aligned0[2:4])) +
        w_W * sum((x - y) * (x - y) for x, y in zip(S_aligned_cand[4:6], b_aligned0[4:6])) +
        w_R * sum((x - y) * (x - y) for x, y in zip(S_aligned_cand[6:9], b_aligned0[6:9])) +
        w_A * sum((x - y) * (x - y) for x, y in zip(S_aligned_cand[9:12], b_aligned0[9:12]))
    )

    c7_aligned = b_aligned0[6] * delta_ph_aligned
    c8_aligned = b_aligned0[7] * delta_ph_aligned
    c9_aligned = b_aligned0[8] * delta_ph_aligned

    omega_07_unit = zeta[6] * c7_aligned
    omega_08_unit = zeta[7] * c8_aligned
    omega_09_unit = zeta[8] * c9_aligned
    g9_aligned = 1 if c9_aligned > 0 else 0
    absolute_gate_aligned = g9_aligned
    omega_10 = zeta[9] * A0 * absolute_gate_aligned
    omega_11 = zeta[10] * A0 * absolute_gate_aligned
    omega_12 = zeta[11] * A0 * absolute_gate_aligned

    omega_07 = omega_07_unit
    omega_08 = omega_08_unit
    omega_09 = omega_09_unit

    bottleneck_aligned = [
        omega_01, omega_02,
        omega_03, omega_04,
        omega_05, omega_06,
        omega_07, omega_08, omega_09,
        omega_10, omega_11, omega_12,
    ]

    mu_aligned = math.sqrt(
        w_I * sum(x * x for x in bottleneck_aligned[0:2]) +
        w_T * sum(x * x for x in bottleneck_aligned[2:4]) +
        w_W * sum(x * x for x in bottleneck_aligned[4:6]) +
        w_R * sum(x * x for x in bottleneck_aligned[6:9]) +
        w_A * sum(x * x for x in bottleneck_aligned[9:12])
    )

    phase_drift = math.sqrt(
        w_I * sum((x - y) * (x - y) for x, y in zip(bottleneck_aligned[0:2], bottleneck_actual[0:2])) +
        w_T * sum((x - y) * (x - y) for x, y in zip(bottleneck_aligned[2:4], bottleneck_actual[2:4])) +
        w_W * sum((x - y) * (x - y) for x, y in zip(bottleneck_aligned[4:6], bottleneck_actual[4:6])) +
        w_R * sum((x - y) * (x - y) for x, y in zip(bottleneck_aligned[6:9], bottleneck_actual[6:9])) +
        w_A * sum((x - y) * (x - y) for x, y in zip(bottleneck_aligned[9:12], bottleneck_actual[9:12]))
    )

    rank_aligned = len(bottleneck_aligned)


    aligned_state = {
        "I": list(S_aligned_cand[0:2]),
        "T": list(S_aligned_cand[2:4]),
        "W": list(S_aligned_cand[4:6]),
        "R": list(S_aligned_cand[6:9]),
        "A": list(S_aligned_cand[9:12]),
    }

    error = [x - y for x, y in zip(S_actual, S_pred)]
    delta = [x - y for x, y in zip(S_aligned_cand, S_actual)]
    energy = np.linalg.norm(error) * np.linalg.norm(delta)
    M_new = M + energy

    invariants_new = {
        "energy_balance": BASE * (phase_drift * Fraction(1, 12)),
        "stability_index": (BASE * BASE) * (((BASE * BASE) + (phase_drift * phase_drift) + (energy * energy)) ** (-1)),
        "being_transition": sum(x - y for x, y in zip(bottleneck_aligned[9:12], bottleneck_pred[9:12])),
        "evolution_winding": math.sqrt(w_A * sum((x - y) * (x - y) for x, y in zip(bottleneck_aligned[9:12], bottleneck_pred[9:12]))),
        "resonant_homotopy": 1 if np.linalg.norm([x - y for x, y in zip(bottleneck_aligned[6:9], bottleneck_pred[6:9])]) != 0 else 0,
        "will_flow_index": math.sqrt(w_W * sum((x - y) * (x - y) for x, y in zip(bottleneck_aligned[4:6], bottleneck_pred[4:6]))),
        "memory_functor_sign": 1 if sum(x - y for x, y in zip(bottleneck_aligned[6:9], bottleneck_pred[6:9])) >= 0 else -1,
        "omega_measure_A": math.sqrt(w_A * sum(x * x for x in bottleneck_aligned[9:12])),
    }

    topology_new = {
        "barrier_strength": barrier_strength,
        "structural_gap": structural_gap,
        "coherence": coherence,
    }

    trans_action_class, holonomy_class = classify(invariants_new, aligned_state["W"][1])

    action = {
        "kind": "sog_admissible_alignment",
        "prev_coords": list(bottleneck_actual),
        "curr_coords": list(bottleneck_actual),
        "next_coords": list(bottleneck_aligned),
        "shift": [x - y for x, y in zip(bottleneck_aligned, bottleneck_actual)],
        "fields": {
            "state": aligned_state,
            "S_aligned_cand": S_aligned_cand,
            "actual": S_actual,
            "predicted": S_pred,
            "error": error,
            "delta": delta,
            "energy": energy,
            "M": M_new,
            "nabla_T": nabla_T,
            "aligned_omega": bottleneck_aligned,
            "bottleneck_actual": bottleneck_actual,
            "bottleneck_aligned": bottleneck_aligned,
            "mu_aligned": mu_aligned,
        },
        "invariants": {
            "energy_balance": invariants_new["energy_balance"],
            "stability_index": invariants_new["stability_index"],
            "being_transition": invariants_new["being_transition"],
            "evolution_winding": invariants_new["evolution_winding"],
            "resonant_homotopy": invariants_new["resonant_homotopy"],
            "will_flow_index": invariants_new["will_flow_index"],
            "memory_functor_sign": invariants_new["memory_functor_sign"],
            "omega_measure_A": invariants_new["omega_measure_A"],
        },
        "topology_invariants": topology_new,
        "trans_action_class": trans_action_class,
        "holonomy_class": holonomy_class,
        "barrier_strength": barrier_strength,
        "structural_gap": structural_gap,
        "coherence": coherence,
        "structural_drift": phase_drift,
        "bottleneck_vector": list(bottleneck_aligned),
        "bottleneck_rank": rank_aligned,
        "phase_drift": phase_drift,
    }

    action_chain["kind"] = "sog_compose"
    action_chain["prev_coords"] = list(action_chain["prev_coords"])
    action_chain["curr_coords"] = list(action["curr_coords"])
    action_chain["next_coords"] = list(action["next_coords"])
    action_chain["shift"] = list(action["shift"])

    action_chain["fields"].update(action["fields"])

    action_chain["invariants"] = {
        "energy_balance": action_chain["invariants"]["energy_balance"] + action["invariants"]["energy_balance"],
        "stability_index": min(action_chain["invariants"]["stability_index"], action["invariants"]["stability_index"]),
        "being_transition": action_chain["invariants"]["being_transition"] + action["invariants"]["being_transition"],
        "evolution_winding": action_chain["invariants"]["evolution_winding"] + action["invariants"]["evolution_winding"],
        "resonant_homotopy": action_chain["invariants"]["resonant_homotopy"] + action["invariants"]["resonant_homotopy"],
        "will_flow_index": action_chain["invariants"]["will_flow_index"] + action["invariants"]["will_flow_index"],
        "memory_functor_sign": action_chain["invariants"]["memory_functor_sign"] * action["invariants"]["memory_functor_sign"],
        "omega_measure_A": action["invariants"]["omega_measure_A"],
    }

    action_chain["topology_invariants"] = {
        "barrier_strength": max(action_chain["topology_invariants"]["barrier_strength"], action["topology_invariants"]["barrier_strength"]),
        "structural_gap": max(action_chain["topology_invariants"]["structural_gap"], action["topology_invariants"]["structural_gap"]),
        "coherence": min(action_chain["topology_invariants"]["coherence"], action["topology_invariants"]["coherence"]),
    }

    action_chain["trans_action_class"] = action["trans_action_class"]
    action_chain["holonomy_class"] = action["holonomy_class"]
    action_chain["barrier_strength"] = max(action_chain["barrier_strength"], action["barrier_strength"])
    action_chain["structural_gap"] = max(action_chain["structural_gap"], action["structural_gap"])
    action_chain["coherence"] = min(action_chain["coherence"], action["coherence"])
    action_chain["structural_drift"] = action_chain["structural_drift"] + action["structural_drift"]
    action_chain["bottleneck_vector"] = list(action["bottleneck_vector"])
    action_chain["bottleneck_rank"] = action["bottleneck_rank"]
    action_chain["phase_drift"] = action["phase_drift"]
    action_chain["history"].append(action)
    del action_chain["phase_bundle"]
