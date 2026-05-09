import json

def generate_code(diagram_data):
    """
    Toma los datos del diagrama y genera una representacion en texto (pseudo-codigo).
    En un caso real, aqui podriamos generar C++, Python, o un archivo XML.
    """
    output = []
    output.append("# --- AUTO-GENERATED BLOCK DIAGRAM CODE --- #")
    output.append(f"# Total Blocks: {len(diagram_data['blocks'])}")
    output.append(f"# Total Connections: {len(diagram_data['connections'])}\n")

    # Declarar bloques
    output.append("## Block Definitions")
    for block in diagram_data['blocks']:
        config_str = ", ".join([f"{k}={v}" for k, v in block['config'].items()])
        output.append(f"CreateBlock(id='{block['id']}', type='{block['type']}', {config_str})")

    output.append("\n## Signal Connections")
    # Declarar conexiones
    for conn in diagram_data['connections']:
        output.append(f"Connect('{conn['from_block']}', port='output') -> ('{conn['to_block']}', port='input_{conn['to_port_index']}')")

    final_code = "\n".join(output)
    
    # Escribir a un archivo de salida
    with open("generated_model.txt", "w") as f:
        f.write(final_code)
    
    return final_code
