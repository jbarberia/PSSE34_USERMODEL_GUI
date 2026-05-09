import json

class GraphResolver:
    def __init__(self, diagram_data):
        self.blocks = {b['id']: b for b in diagram_data['blocks']}
        self.connections = diagram_data['connections']
        self.adj = {b_id: [] for b_id in self.blocks}
        self.in_degree = {b_id: 0 for b_id in self.blocks}
        
        # Construir lista de adyacencia
        for conn in self.connections:
            u, v = conn['from_block'], conn['to_block']
            self.adj[u].append(v)
            self.in_degree[v] += 1

    def get_execution_order(self):
        """
        Ordenamiento topológico (Kahn's Algorithm).
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
            remaining = [b_id for b_id in self.blocks if b_id not in order]
            order.extend(remaining)
            
        return order

def translate_to_fortran(diagram_data):
    "solo para maquinas"
    resolver = GraphResolver(diagram_data)
    order = resolver.get_execution_order()
    model_name = diagram_data.get("model_name", "USUARIO")
    
    output = []
    output.append(f"! --- AUTO-GENERATED FORTRAN SUBROUTINE: {model_name} ---")
    output.append(f"SUBROUTINE {model_name}(I, ISLOT)")
    output.append(f"    INCLUDE 'COMON4.INS'")
    output.append(f"    IMPLICIT NONE")
    output.append(f"    J = STRTIN(1, ISLOT)                 ! STARTING 'CON'")
    output.append(f"    K = STRTIN(2, ISLOT)                 ! STARTING 'STATE'")
    output.append(f"    L = STRTIN(3, ISLOT)                 ! STARTING 'VAR'")
    output.append(f"    M = STRTIN(4, ISLOT)                 ! STARTING 'ICON'")
    output.append(f"    IF (MIDTRM) RETURN")
    output.append(f"")
    output.append(f"    SELECT CASE (MODE)")
    output.append(f"    CASE(1) ! INCIALIZACION")
    output.append(f"    CASE(2) ! CALCULO DE DERIVADAS")
    output.append(f"    CASE(3) ! CALCULO DE LAS SALIDAS")
    
    print(diagram_data)
    for block_id in order:
        block = resolver.blocks[block_id]
        
        code = block["item"].create_fortran_code_mode_3()
        output.append(f"        {code}")
        print(block)

        b_type = block['type']
        cfg = block['config']

    output.append(f"    CASE(4) ! ESPACIOS PARA INTEGRACION")
    output.append(f"    CASE(5)")
    output.append(f"    CASE(6)")
    output.append(f"    CASE(7)")
    output.append(f"    CASE(8)")


    

    # #output.append("    REAL, INTENT(IN) :: INPUTS(*), DT")
    # #output.append("    REAL, INTENT(INOUT) :: STATES(*), VARS(*)\n")
    
    # output.append("    ! Execution Order determined by Graph Traversal")
    
    # for block_id in order:
    #     block = resolver.blocks[block_id]
    #     b_type = block['type']
    #     cfg = block['config']
        
    #     output.append(f"\n    ! Block: {block_id} ({b_type})")
        
    #     if b_type == "INPUT":
    #         if cfg.get("id_mode"):
    #             output.append(f"    V_{block_id} = GET_SIGNAL('{cfg['type']}', {cfg['bus_num']}, '{cfg['machine_id']}')")
    #         else:
    #             output.append(f"    V_{block_id} = {cfg['type']}({cfg['index']})")
        
    #     elif b_type == "GAIN":
    #         inputs = [c for c in diagram_data['connections'] if c['to_block'] == block_id]
    #         in_var = f"V_{inputs[0]['from_block']}" if inputs else "0.0"
    #         output.append(f"    V_{block_id} = {in_var} * {cfg['gain']}")
            
    #     elif b_type == "SUM":
    #         inputs = [c for c in diagram_data['connections'] if c['to_block'] == block_id]
    #         sum_terms = [f"V_{c['from_block']}" for c in inputs]
    #         rhs = " + ".join(sum_terms) if sum_terms else "0.0"
    #         output.append(f"    V_{block_id} = {rhs}")
            
    #     elif b_type == "INTEGRATOR":
    #         inputs = [c for c in diagram_data['connections'] if c['to_block'] == block_id]
    #         in_var = f"V_{inputs[0]['from_block']}" if inputs else "0.0"
    #         output.append(f"    ! Forward Euler Integration")
    #         output.append(f"    STATES({block_id}_IDX) = STATES({block_id}_IDX) + ({in_var} / {cfg['ti']}) * DT")
    #         output.append(f"    V_{block_id} = STATES({block_id}_IDX)")

    #     if cfg.get("limit_enabled"):
    #         output.append(f"    V_{block_id} = MAX({cfg['limit_min']}, MIN({cfg['limit_max']}, V_{block_id}))")

    output.append(f"\nEND SUBROUTINE {model_name}")
    
    with open(f"{model_name}.f90", "w") as f:
        f.write("\n".join(output))
        
    return "\n".join(output)

def generate_code(diagram_data):
    return translate_to_fortran(diagram_data)
