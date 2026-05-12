import json
from app.blocks.gain import GainBlock
from app.blocks.sum import SumBlock
from app.blocks.control_blocks import IntegratorBlock, FirstOrderLagBlock, WashoutBlock, LeadLagBlock, PIBlock, PIDBlock
from app.blocks.io_blocks import InputBlock, OutputBlock

BLOCK_CLASSES = {
    "GAIN": GainBlock,
    "SUM": SumBlock,
    "INTEGRATOR": IntegratorBlock,
    "LAG 1": FirstOrderLagBlock,
    "WASHOUT": WashoutBlock,
    "LEAD LAG": LeadLagBlock,
    "PI": PIBlock,
    "PID": PIDBlock,
    "INPUT": InputBlock,
    "OUTPUT": OutputBlock
}

class GraphResolver:
    def __init__(self, diagram_data):
        self.blocks = {b['id']: b for b in diagram_data['blocks']}
        self.connections = diagram_data['connections']
        self.adj = {b_id: [] for b_id in self.blocks}
        self.in_degree = {b_id: 0 for b_id in self.blocks}
        
        # Build adjacency list and track inputs per block
        self.inputs_map = {b_id: {} for b_id in self.blocks} # block_id -> {port_index: from_block_id}

        for conn in self.connections:
            u, v = conn['from_block'], conn['to_block']
            self.adj[u].append(v)
            self.in_degree[v] += 1
            self.inputs_map[v][conn['to_port_index']] = u

    def get_execution_order(self):
        """
        Topological Sort (Kahn's Algorithm).
        """
        queue = [b_id for b_id, deg in self.in_degree.items() if deg == 0]
        order = []
        in_degree = dict(self.in_degree)
        
        while queue:
            u = queue.pop(0)
            order.append(u)
            for v in self.adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
        
        if len(order) < len(self.blocks):
            # Fallback for cycles or disconnected components
            remaining = [b_id for b_id in self.blocks if b_id not in order]
            order.extend(remaining)
            
        return order

def get_block_output_var(block_id):
    return f"V_{block_id}"

def generate_fortran_block_code(block, inputs_map, all_blocks, mode, k_idx):
    b_type = block['type']
    b_id = block['id']
    cfg = dict(block['config']) # Copy to avoid mutating original
    cfg['type'] = b_type
    cfg['block_id'] = b_id
    
    # Resolve input variables
    inputs = inputs_map.get(b_id, {})
    in_vars = {}
    for i in range(10):
        from_id = inputs.get(i)
        in_vars[i] = get_block_output_var(from_id) if from_id else "0.0"

    out_var = get_block_output_var(b_id)

    # Helper for Mode 1: Resolve "What is the output of the block that feeds me?"
    first_input_id = inputs.get(0)
    target_in_var = get_block_output_var(first_input_id) if first_input_id else None

    cls = BLOCK_CLASSES.get(b_type)
    if cls:
        return cls.get_fortran_code(cfg, mode, in_vars, out_var, k_idx, target_in_var)
    
    return [f"! Unknown block type: {b_type}"]

import os

def translate_to_fortran(diagram_data):
    resolver = GraphResolver(diagram_data)
    order = resolver.get_execution_order()
    model_name = diagram_data.get("model_name", "USUARIO")
    
    # Pre-calculate state indices
    block_k_indices = {}
    current_k = 0
    state_blocks = ["INTEGRATOR", "PI", "LAG 1", "WASHOUT", "LEAD LAG", "PID"]
    for block_id in order:
        block = resolver.blocks[block_id]
        if block['type'] in state_blocks:
            block_k_indices[block_id] = f"K+{current_k}"
            current_k += 1
    total_states = current_k

    # Generate mode-specific code
    mode_codes = {1: [], 2: [], 3: [], 8: []}
    
    for m in [1, 2, 3]:
        current_order = list(reversed(order)) if m == 1 else order
        for block_id in current_order:
            block = resolver.blocks[block_id]
            k_idx = block_k_indices.get(block_id, "0")
            lines = generate_fortran_block_code(block, resolver.inputs_map, resolver.blocks, m, k_idx)
            mode_codes[m].extend(lines)

    # Mode 8: Parameter descriptions
    con_idx = 0
    for block_id in order:
        block = resolver.blocks[block_id]
        b_type = block['type']
        if b_type == "GAIN":
            mode_codes[8].append(f"CON_DSCRPT(J+{con_idx}) = '{block_id} GAIN'")
            con_idx += 1
        elif b_type == "INTEGRATOR":
            mode_codes[8].append(f"CON_DSCRPT(J+{con_idx}) = '{block_id} TI'")
            con_idx += 1
        elif b_type == "PI":
            mode_codes[8].append(f"CON_DSCRPT(J+{con_idx}) = '{block_id} KP'")
            mode_codes[8].append(f"CON_DSCRPT(J+{con_idx+1}) = '{block_id} KI'")
            con_idx += 2
        elif b_type == "LAG 1":
            mode_codes[8].append(f"CON_DSCRPT(J+{con_idx}) = '{block_id} KI'")
            mode_codes[8].append(f"CON_DSCRPT(J+{con_idx+1}) = '{block_id} TI'")
            con_idx += 2

    # Prepare variable lists
    all_vars = [get_block_output_var(b_id) for b_id in order]
    integers = "I, ISLOT, J, K, L, M, IERR"
    reals = ", ".join(all_vars) if all_vars else ""

    # Load Template
    template_path = os.path.join(os.path.dirname(__file__), "TEMPLATE.f90")
    with open(template_path, "r") as f:
        template = f.read()

    # Replacements
    result = template.replace("%model_name%", model_name)
    result = result.replace("%parameters%", "I, ISLOT")
    result = result.replace("%index_fn%", "STRTIN")
    
    # Replace %% tags sequentially (First is INTEGER, Second is REAL)
    result = result.replace("%%", integers, 1)
    result = result.replace("%%", reals, 1)

    result = result.replace("%mode_1%", "\n        ".join(mode_codes[1]))
    result = result.replace("%mode_2%", "\n        ".join(mode_codes[2]))
    result = result.replace("%mode_3%", "\n        ".join(mode_codes[3]))
    result = result.replace("%mode_8%", "\n        ".join(mode_codes[8]))
    
    # Update Case(4) with total states
    result = result.replace("NINTEG, K+1", f"NINTEG, K + {total_states - 1 if total_states > 0 else 0}")

    with open(f"{model_name}.f90", "w") as f:
        f.write(result)
        
    return result


def generate_code(diagram_data):
    return translate_to_fortran(diagram_data)
