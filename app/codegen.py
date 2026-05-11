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

def generate_fortran_block_code(block, inputs_map, all_blocks):
    b_type = block['type']
    b_id = block['id']
    cfg = block['config']
    
    # Resolve input variables
    inputs = inputs_map.get(b_id, {})
    # Default input vars if not connected
    in_vars = {}
    for i in range(10): # Assume max 10 ports for safety
        from_id = inputs.get(i)
        in_vars[i] = get_block_output_var(from_id) if from_id else "0.0"

    out_var = get_block_output_var(b_id)
    code_lines = []

    if b_type == "GAIN":
        code_lines.append(f"{out_var} = {in_vars[0]} * {cfg.get('gain', '1.0')}")
    
    elif b_type == "SUM":
        # Sum blocks can have multiple inputs. The port index matters if it's a specialized sum,
        # but usually it's just adding everything.
        active_inputs = [in_vars[i] for i in sorted(inputs.keys())]
        rhs = " + ".join(active_inputs) if active_inputs else "0.0"
        code_lines.append(f"{out_var} = {rhs}")
    
    elif b_type == "INTEGRATOR":
        # Integrators usually need a state index K
        ti = cfg.get('ti', '1.0')
        code_lines.append(f"! Integrator {b_id}")
        code_lines.append(f"        DSTATE(K) = {in_vars[0]} / {ti}")
        code_lines.append(f"        {out_var} = STATE(K)")
        code_lines.append(f"        K = K + 1")
    
    elif b_type == "INPUT":
        if cfg.get("id_mode"):
            code_lines.append(f"{out_var} = GET_SIGNAL('{cfg.get('type')}', {cfg.get('bus_num', 0)}, '{cfg.get('machine_id', '')}')")
        else:
            code_lines.append(f"{out_var} = {cfg.get('type', 'VAR')}({cfg.get('index', 1)})")
            
    elif b_type == "OUTPUT":
        code_lines.append(f"! Output {b_id}")
        code_lines.append(f"VAR({cfg.get('index', 1)}) = {in_vars[0]}")
        

    elif b_type == "LAG 1":
        # First order lag: T*dy/dt + y = u  => dy/dt = (u - y)/T
        t1 = cfg.get('t1', '1.0')
        code_lines.append(f"! Lag 1 {b_id}")
        code_lines.append(f"        DSTATE(K) = ({in_vars[0]} - STATE(K)) / {t1}")
        code_lines.append(f"        {out_var} = STATE(K)")
        code_lines.append(f"        K = K + 1")

    # Add limits if enabled
    if cfg.get("limit_enabled"):
        l_min = cfg.get("limit_min", "-1.0")
        l_max = cfg.get("limit_max", "1.0")
        code_lines.append(f"{out_var} = MAX({l_min}, MIN({l_max}, {out_var}))")

    return code_lines

def translate_to_fortran(diagram_data):
    resolver = GraphResolver(diagram_data)
    order = resolver.get_execution_order()
    model_name = diagram_data.get("model_name", "USUARIO")
    
    output = []
    output.append(f"! --- AUTO-GENERATED FORTRAN SUBROUTINE: {model_name} ---")
    output.append(f"SUBROUTINE {model_name}(I, ISLOT)")
    output.append(f"    INCLUDE 'COMON4.INS'")
    output.append(f"    IMPLICIT NONE")
    output.append(f"    INTEGER I, ISLOT, J, K, L, M")
    output.append(f"    REAL {', '.join([get_block_output_var(b_id) for b_id in order])}")
    output.append(f"")
    output.append(f"    J = STRTIN(1, ISLOT)                 ! STARTING 'CON'")
    output.append(f"    K = STRTIN(2, ISLOT)                 ! STARTING 'STATE'")
    output.append(f"    L = STRTIN(3, ISLOT)                 ! STARTING 'VAR'")
    output.append(f"    M = STRTIN(4, ISLOT)                 ! STARTING 'ICON'")
    output.append(f"    IF (MIDTRM) RETURN")
    output.append(f"")
    output.append(f"    SELECT CASE (MODE)")
    output.append(f"    CASE(1) ! INITIALIZATION")
    output.append(f"        ! Initialization logic could go here")
    output.append(f"    CASE(2, 3) ! DERIVATIVES AND OUTPUTS")
    
    for block_id in order:
        block = resolver.blocks[block_id]
        code_lines = generate_fortran_block_code(block, resolver.inputs_map, resolver.blocks)
        for line in code_lines:
            output.append(f"        {line}")

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
