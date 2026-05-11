import json

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
    cfg = block['config']
    
    # Resolve input variables
    inputs = inputs_map.get(b_id, {})
    in_vars = {}
    for i in range(10):
        from_id = inputs.get(i)
        in_vars[i] = get_block_output_var(from_id) if from_id else "0.0"

    out_var = get_block_output_var(b_id)
    code_lines = []

    # Helper for Mode 1: Resolve "What is the output of the block that feeds me?"
    # In Mode 1, we often want to find the input given the output.
    # Result of block_mode1 is usually the initialized value for its input signal.
    first_input_id = inputs.get(0)
    target_in_var = get_block_output_var(first_input_id) if first_input_id else None

    if b_type == "GAIN":
        if mode == 1:
            if target_in_var:
                code_lines.append(f"{target_in_var} = {out_var} / {cfg.get('gain', '1.0')}")
        elif mode in [2, 3]:
            code_lines.append(f"{out_var} = {in_vars[0]} * {cfg.get('gain', '1.0')}")
    
    elif b_type == "SUM":
        if mode == 1:
            # Ambiguous for multiple inputs, assume main path is port 0
            if target_in_var:
                active_others = [in_vars[i] for i in sorted(inputs.keys()) if i != 0]
                rhs_others = " + ".join(active_others) if active_others else "0.0"
                code_lines.append(f"{target_in_var} = {out_var} - ({rhs_others})")
        elif mode in [2, 3]:
            active_inputs = [in_vars[i] for i in sorted(inputs.keys())]
            rhs = " + ".join(active_inputs) if active_inputs else "0.0"
            code_lines.append(f"{out_var} = {rhs}")
    
    elif b_type == "INTEGRATOR":
        ti = cfg.get('ti', '1.0')
        if mode == 1:
            if target_in_var:
                code_lines.append(f"{target_in_var} = INT_MODE1({ti}, {out_var}, {k_idx})")
        elif mode == 2:
            code_lines.append(f"{out_var} = INT_MODE2({ti}, {in_vars[0]}, {k_idx})")
        elif mode == 3:
            code_lines.append(f"{out_var} = INT_MODE3({ti}, {in_vars[0]}, {k_idx})")

    elif b_type == "PI":
        kp = cfg.get('kp', '1.0')
        ki = cfg.get('ki', '1.0')
        l_min = cfg.get('limit_min', '-999.0') if cfg.get('limit_enabled') else '-999.0'
        l_max = cfg.get('limit_max', '999.0') if cfg.get('limit_enabled') else '999.0'
        if mode == 1:
            if target_in_var:
                code_lines.append(f"{target_in_var} = NWPI_MODE1({kp}, {ki}, {l_max}, {l_min}, {out_var}, {k_idx}, IERR)")
        elif mode == 2:
            code_lines.append(f"{out_var} = NWPI_MODE2({kp}, {ki}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})")
        elif mode == 3:
            code_lines.append(f"{out_var} = NWPI_MODE3({kp}, {ki}, {l_max}, {l_min}, {in_vars[0]}, {k_idx})")

    elif b_type == "LAG 1":
        ki = cfg.get('ki', '1.0')
        ti = cfg.get('ti', '1.0')
        if mode == 1:
            if target_in_var:
                code_lines.append(f"{target_in_var} = LAG_MODE1({ki}, {ti}, {out_var}, {k_idx}, IERR)")
        elif mode == 2:
            code_lines.append(f"{out_var} = LAG_MODE2({ki}, {ti}, {in_vars[0]}, {k_idx})")
        elif mode == 3:
            code_lines.append(f"{out_var} = LAG_MODE3({ki}, {ti}, {in_vars[0]}, {k_idx})")

    elif b_type == "INPUT":
        if mode == 1:
            # Inputs in mode 1 might just be sinks of the reverse propagation
            code_lines.append(f"! Input {b_id} initialized to {out_var}")
        elif mode in [2, 3]:
            if cfg.get("id_mode"):
                code_lines.append(f"{out_var} = GET_SIGNAL('{cfg.get('type')}', {cfg.get('bus_num', 0)}, '{cfg.get('machine_id', '')}')")
            else:
                code_lines.append(f"{out_var} = {cfg.get('type', 'VAR')}({cfg.get('index', 1)})")
            
    elif b_type == "OUTPUT":
        if mode == 1:
            # Initialization starting point: fetch current value
            if cfg.get("id_mode"):
                 code_lines.append(f"{out_var} = GET_SIGNAL('{cfg.get('type')}', {cfg.get('bus_num', 0)}, '{cfg.get('machine_id', '')}')")
            else:
                 code_lines.append(f"{out_var} = {cfg.get('type', 'VAR')}({cfg.get('index', 1)})")
            
            # Propagate backwards to the source block
            if target_in_var:
                code_lines.append(f"{target_in_var} = {out_var}")
                
        elif mode == 3:
            code_lines.append(f"VAR({cfg.get('index', 1)}) = {in_vars[0]}")
        if mode in [2, 3]:
            code_lines.append(f"{out_var} = {in_vars[0]}")

    if cfg.get("limit_enabled") and b_type not in ["PI"]:
        if mode in [2, 3]:
            l_min = cfg.get("limit_min", "-1.0")
            l_max = cfg.get("limit_max", "1.0")
            code_lines.append(f"{out_var} = MAX({l_min}, MIN({l_max}, {out_var}))")

    return code_lines

def translate_to_fortran(diagram_data):
    resolver = GraphResolver(diagram_data)
    order = resolver.get_execution_order()
    model_name = diagram_data.get("model_name", "USUARIO")
    
    # Pre-calculate state indices
    block_k_indices = {}
    current_k = 0
    for block_id in order:
        block = resolver.blocks[block_id]
        if block['type'] in ["INTEGRATOR", "PI", "LAG 1"]:
            block_k_indices[block_id] = f"K+{current_k}"
            current_k += 1
    total_states = current_k

    output = []
    output.append(f"! --- AUTO-GENERATED FORTRAN SUBROUTINE: {model_name} ---")
    output.append(f"SUBROUTINE {model_name}(I, ISLOT)")
    output.append(f"    INCLUDE 'COMON4.INS'")
    output.append(f"    IMPLICIT NONE")
    output.append(f"    INTEGER I, ISLOT, J, K, L, M, IERR")
    
    all_vars = [get_block_output_var(b_id) for b_id in order]
    if all_vars:
        output.append(f"    REAL {', '.join(all_vars)}")
    output.append(f"")
    output.append(f"    J = STRTIN(1, ISLOT)                 ! STARTING 'CON'")
    output.append(f"    K = STRTIN(2, ISLOT)                 ! STARTING 'STATE'")
    output.append(f"    L = STRTIN(3, ISLOT)                 ! STARTING 'VAR'")
    output.append(f"    M = STRTIN(4, ISLOT)                 ! STARTING 'ICON'")
    output.append(f"    IF (MIDTRM) RETURN")
    output.append(f"")
    output.append(f"    SELECT CASE (MODE)")
    
    for m in [1, 2, 3]:
        output.append(f"    CASE({m})")
        # Mode 1 uses reverse order for initialization
        current_order = list(reversed(order)) if m == 1 else order
        for block_id in current_order:
            block = resolver.blocks[block_id]
            k_idx = block_k_indices.get(block_id, "0")
            lines = generate_fortran_block_code(block, resolver.inputs_map, resolver.blocks, m, k_idx)
            for line in lines:
                output.append(f"        {line}")

    output.append(f"    CASE(4)")
    output.append(f"        NINTEG = MAX(NINTEG, K + {total_states - 1 if total_states > 0 else 0})")
    
    output.append(f"    CASE(8)")
    output.append(f"        ! Parameter descriptions")
    con_idx = 0
    for block_id in order:
        block = resolver.blocks[block_id]
        b_type = block['type']
        if b_type == "GAIN":
            output.append(f"        CON_DSCRPT(J+{con_idx}) = '{block_id} GAIN'")
            con_idx += 1
        elif b_type == "INTEGRATOR":
            output.append(f"        CON_DSCRPT(J+{con_idx}) = '{block_id} TI'")
            con_idx += 1
        elif b_type == "PI":
            output.append(f"        CON_DSCRPT(J+{con_idx}) = '{block_id} KP'")
            output.append(f"        CON_DSCRPT(J+{con_idx+1}) = '{block_id} KI'")
            con_idx += 2
        elif b_type == "LAG 1":
            output.append(f"        CON_DSCRPT(J+{con_idx}) = '{block_id} KI'")
            output.append(f"        CON_DSCRPT(J+{con_idx+1}) = '{block_id} TI'")
            con_idx += 2
    
    output.append(f"    CASE DEFAULT")
    output.append(f"        RETURN")
    output.append(f"    END SELECT")
    output.append(f"")
    output.append(f"END SUBROUTINE {model_name}")
    
    fortran_code = "\n".join(output)
    with open(f"{model_name}.f90", "w") as f:
        f.write(fortran_code)
        
    return fortran_code

def generate_code(diagram_data):
    return translate_to_fortran(diagram_data)
