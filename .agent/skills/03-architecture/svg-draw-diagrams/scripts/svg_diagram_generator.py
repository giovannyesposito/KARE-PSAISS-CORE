#!/usr/bin/env python3
"""
SVG Diagram Generator
Renderiza diagramas SVG a partir de arquivos YAML
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml
try:
    import defusedxml.ElementTree as ET  # safe against XML entity expansion (Billion Laughs)
except ImportError:
    import xml.etree.ElementTree as ET  # type: ignore[no-redef]  # fallback — install defusedxml for production


class SVGDiagramRenderer:
    """Renderizador de diagramas SVG"""
    
    def __init__(self, plan: Dict, verbose: bool = False):
        self.plan = plan
        self.verbose = verbose
        self.components = {}
        self.positions = {}
        
        # Extract metadata
        meta = plan.get("metadata", {})
        self.width = meta.get("dimensions", {}).get("width", 1200)
        self.height = meta.get("dimensions", {}).get("height", 800)
        self.title = meta.get("title", "Diagram")
        self.diagram_type = meta.get("type", "architecture")
        self.orientation = meta.get("orientation", "horizontal")
        
        # Margins and spacing
        self.margin = 50
        self.component_width = 160
        self.component_height = 100
        self.spacing_x = 200
        self.spacing_y = 150
    
    def log(self, message: str):
        """Log de debug"""
        if self.verbose:
            print(f"[DEBUG] {message}")
    
    def calculate_layout(self):
        """Calcula posições automáticas dos componentes"""
        components = self.plan.get("components", [])
        
        if self.orientation == "horizontal":
            self._layout_horizontal(components)
        elif self.orientation == "vertical":
            self._layout_vertical(components)
        elif self.orientation == "hierarchical":
            self._layout_hierarchical(components)
        else:
            self._layout_horizontal(components)
    
    def _layout_horizontal(self, components: List[Dict]):
        """Layout horizontal (esquerda para direita)"""
        x = self.margin + 100
        y = self.height // 2
        
        for comp in components:
            comp_id = comp["id"]
            if comp.get("position") == "auto" or "position" not in comp:
                self.positions[comp_id] = (x, y)
                x += self.component_width + self.spacing_x
            else:
                self.positions[comp_id] = tuple(comp["position"])
        
        self.log(f"Layout horizontal: {len(components)} componentes")
    
    def _layout_vertical(self, components: List[Dict]):
        """Layout vertical (cima para baixo)"""
        x = self.width // 2
        y = self.margin + 80
        
        for comp in components:
            comp_id = comp["id"]
            if comp.get("position") == "auto" or "position" not in comp:
                self.positions[comp_id] = (x, y)
                y += self.component_height + self.spacing_y
            else:
                self.positions[comp_id] = tuple(comp["position"])
        
        self.log(f"Layout vertical: {len(components)} componentes")
    
    def _layout_hierarchical(self, components: List[Dict]):
        """Layout hierárquico (árvore)"""
        # Simple grid layout for now
        cols = 3
        x_start = self.margin + 100
        y_start = self.margin + 100
        
        for i, comp in enumerate(components):
            comp_id = comp["id"]
            if comp.get("position") == "auto" or "position" not in comp:
                col = i % cols
                row = i // cols
                x = x_start + col * (self.component_width + self.spacing_x)
                y = y_start + row * (self.component_height + self.spacing_y)
                self.positions[comp_id] = (x, y)
            else:
                self.positions[comp_id] = tuple(comp["position"])
        
        self.log(f"Layout hierárquico: {len(components)} componentes")
    
    def render_svg(self) -> str:
        """Renderiza o SVG completo"""
        self.log("Iniciando renderização SVG...")
        
        # Calculate layout
        self.calculate_layout()
        
        # Create SVG root
        svg = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(self.width),
            "height": str(self.height),
            "viewBox": f"0 0 {self.width} {self.height}"
        })
        
        # Add styles
        style = ET.SubElement(svg, "style")
        style.text = self._generate_styles()
        
        # Add title
        title_elem = ET.SubElement(svg, "title")
        title_elem.text = self.title
        
        # Add background
        bg = ET.SubElement(svg, "rect", {
            "width": str(self.width),
            "height": str(self.height),
            "fill": "#FFFFFF"
        })
        
        # Add diagram title
        title_text = ET.SubElement(svg, "text", {
            "x": str(self.width // 2),
            "y": "30",
            "text-anchor": "middle",
            "class": "diagram-title"
        })
        title_text.text = self.title
        
        # Render groups first (background)
        for group in self.plan.get("groups", []):
            self._render_group(svg, group)
        
        # Render connections (before components so they're behind)
        for connection in self.plan.get("connections", []):
            self._render_connection(svg, connection)
        
        # Render components
        for component in self.plan.get("components", []):
            self._render_component(svg, component)
        
        # Render annotations
        for annotation in self.plan.get("annotations", []):
            self._render_annotation(svg, annotation)
        
        self.log("Renderização concluída")
        
        return self._prettify_xml(svg)
    
    def _generate_styles(self) -> str:
        """Gera estilos CSS para o SVG"""
        return """
            .diagram-title {
                font-family: Arial, sans-serif;
                font-size: 24px;
                font-weight: bold;
                fill: #333333;
            }
            .component-label {
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                fill: #FFFFFF;
                text-anchor: middle;
            }
            .connection-label {
                font-family: Arial, sans-serif;
                font-size: 12px;
                fill: #666666;
                text-anchor: middle;
            }
            .group-label {
                font-family: Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                fill: #555555;
            }
            .annotation-text {
                font-family: Arial, sans-serif;
                font-size: 11px;
                fill: #888888;
            }
            .component {
                filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));
            }
        """
    
    def _render_component(self, parent: ET.Element, component: Dict):
        """Renderiza um componente"""
        comp_id = component["id"]
        label = component.get("label", comp_id)
        icon = component.get("icon", "rectangle")
        color = self._validate_color(component.get("color", "#4A90E2"))
        
        x, y = self.positions[comp_id]
        
        # Component group
        g = ET.SubElement(parent, "g", {
            "id": comp_id,
            "class": "component"
        })
        
        # Check if icon is an asset file or a shape
        if icon.startswith("assets/"):
            self._render_asset_icon(g, icon, x, y, color)
        else:
            self._render_shape(g, icon, x, y, color)
        
        # Label
        label_y = y + self.component_height // 2 + 5
        text = ET.SubElement(g, "text", {
            "x": str(x + self.component_width // 2),
            "y": str(label_y),
            "class": "component-label"
        })
        
        # Word wrap for long labels
        words = label.split()
        if len(words) > 2:
            # Multi-line
            tspan1 = ET.SubElement(text, "tspan", {
                "x": str(x + self.component_width // 2),
                "dy": "0"
            })
            tspan1.text = " ".join(words[:len(words)//2])
            
            tspan2 = ET.SubElement(text, "tspan", {
                "x": str(x + self.component_width // 2),
                "dy": "16"
            })
            tspan2.text = " ".join(words[len(words)//2:])
        else:
            text.text = label
        
        self.log(f"Renderizado componente: {comp_id} em ({x}, {y})")
    
    def _render_shape(self, parent: ET.Element, shape: str, x: int, y: int, color: str):
        """Renderiza formas geométricas básicas"""
        if shape == "rectangle":
            ET.SubElement(parent, "rect", {
                "x": str(x),
                "y": str(y),
                "width": str(self.component_width),
                "height": str(self.component_height),
                "fill": color,
                "rx": "8",
                "ry": "8"
            })
        
        elif shape == "circle":
            cx = x + self.component_width // 2
            cy = y + self.component_height // 2
            radius = min(self.component_width, self.component_height) // 2
            ET.SubElement(parent, "circle", {
                "cx": str(cx),
                "cy": str(cy),
                "r": str(radius),
                "fill": color
            })
        
        elif shape == "cylinder":
            # Database icon simplified
            self._render_cylinder(parent, x, y, self.component_width, self.component_height, color)
        
        elif shape == "diamond":
            cx = x + self.component_width // 2
            cy = y + self.component_height // 2
            points = [
                (cx, y),
                (x + self.component_width, cy),
                (cx, y + self.component_height),
                (x, cy)
            ]
            points_str = " ".join([f"{px},{py}" for px, py in points])
            ET.SubElement(parent, "polygon", {
                "points": points_str,
                "fill": color
            })
        
        elif shape == "cloud":
            self._render_cloud(parent, x, y, self.component_width, self.component_height, color)
        
        elif shape == "hexagon":
            self._render_hexagon(parent, x, y, self.component_width, self.component_height, color)
        
        else:
            # Default to rectangle
            ET.SubElement(parent, "rect", {
                "x": str(x),
                "y": str(y),
                "width": str(self.component_width),
                "height": str(self.component_height),
                "fill": color,
                "rx": "8"
            })
    
    def _render_cylinder(self, parent: ET.Element, x: int, y: int, width: int, height: int, color: str):
        """Renderiza um cilindro (database)"""
        ellipse_height = height * 0.15
        
        # Top ellipse
        ET.SubElement(parent, "ellipse", {
            "cx": str(x + width // 2),
            "cy": str(y + ellipse_height),
            "rx": str(width // 2),
            "ry": str(ellipse_height),
            "fill": color
        })
        
        # Body rectangle
        ET.SubElement(parent, "rect", {
            "x": str(x),
            "y": str(y + ellipse_height),
            "width": str(width),
            "height": str(height - ellipse_height * 2),
            "fill": color
        })
        
        # Bottom ellipse
        ET.SubElement(parent, "ellipse", {
            "cx": str(x + width // 2),
            "cy": str(y + height - ellipse_height),
            "rx": str(width // 2),
            "ry": str(ellipse_height),
            "fill": color
        })
    
    def _render_cloud(self, parent: ET.Element, x: int, y: int, width: int, height: int, color: str):
        """Renderiza uma nuvem (external system)"""
        # Simplified cloud using circles
        cx = x + width // 2
        cy = y + height // 2
        
        # Main body
        ET.SubElement(parent, "ellipse", {
            "cx": str(cx),
            "cy": str(cy),
            "rx": str(width // 2),
            "ry": str(height // 3),
            "fill": color
        })
    
    def _render_hexagon(self, parent: ET.Element, x: int, y: int, width: int, height: int, color: str):
        """Renderiza um hexágono"""
        cx = x + width // 2
        cy = y + height // 2
        offset_x = width // 4
        
        points = [
            (x + offset_x, y),
            (x + width - offset_x, y),
            (x + width, cy),
            (x + width - offset_x, y + height),
            (x + offset_x, y + height),
            (x, cy)
        ]
        
        points_str = " ".join([f"{px},{py}" for px, py in points])
        ET.SubElement(parent, "polygon", {
            "points": points_str,
            "fill": color
        })
    
    # SVG elements/attributes blocked during asset sanitization
    _SVG_BLOCKED_TAGS = {
        "script", "foreignObject", "iframe", "object", "embed", "use",
        "animate", "animateMotion", "animateTransform", "set",
    }
    _SVG_BLOCKED_ATTRS = {
        "onload", "onclick", "onmouseover", "onmouseout", "onfocus",
        "onblur", "onerror", "onabort", "onactivate", "onbegin", "onend",
        "href", "xlink:href",
    }

    @staticmethod
    def _validate_color(color: str) -> str:
        """Aceita apenas cores hex (#RGB / #RRGGBB) ou named colors seguras."""
        import re
        if re.fullmatch(r"#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?", color):
            return color
        _SAFE_NAMED = {
            "white", "black", "red", "green", "blue", "gray", "grey",
            "yellow", "orange", "purple", "pink", "brown", "transparent",
        }
        if color.lower() in _SAFE_NAMED:
            return color
        return "#CCCCCC"  # fallback neutro

    def _sanitize_svg_element(self, elem: ET.Element):
        """Remove tags e atributos perigosos de um elemento SVG (recursivo)."""
        # Strip namespace prefix para comparação
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if tag.lower() in self._SVG_BLOCKED_TAGS:
            return None  # sinaliza remoção

        # Remover atributos perigosos
        for attr in list(elem.attrib):
            attr_local = attr.split("}")[-1] if "}" in attr else attr
            if attr_local.lower() in self._SVG_BLOCKED_ATTRS:
                del elem.attrib[attr]

        # Processar filhos recursivamente
        for child in list(elem):
            if self._sanitize_svg_element(child) is None:
                elem.remove(child)

        return elem

    def _render_asset_icon(self, parent: ET.Element, asset_path: str, x: int, y: int, color: str):
        """Renderiza um ícone SVG da pasta assets com validação de path e sanitização."""
        # --- Path Traversal protection ---
        assets_dir = (Path(__file__).parent.parent / "assets").resolve()
        try:
            full_path = assets_dir.joinpath(asset_path.removeprefix("assets/")).resolve()
        except Exception:
            self.log(f"⚠️  Caminho inválido: {asset_path}, usando retângulo")
            self._render_shape(parent, "rectangle", x, y, color)
            return

        # Garante que o path resolvido está dentro de assets/
        if not full_path.is_relative_to(assets_dir):
            self.log(f"⚠️  Path fora de assets/: {asset_path}, usando retângulo")
            self._render_shape(parent, "rectangle", x, y, color)
            return

        if not full_path.exists():
            self.log(f"⚠️  Asset não encontrado: {asset_path}, usando retângulo")
            self._render_shape(parent, "rectangle", x, y, color)
            return

        try:
            # Parse the SVG asset
            tree = ET.parse(full_path)
            root = tree.getroot()

            # --- XSS / Injection protection: sanitize before embedding ---
            self._sanitize_svg_element(root)

            # Create a group for the asset
            g = ET.SubElement(parent, "g", {
                "transform": f"translate({x}, {y}) scale({self.component_width / 100})"
            })

            # Copy sanitized children only
            for child in root:
                g.append(child)

            self.log(f"Asset carregado: {asset_path}")

        except Exception as e:
            self.log(f"❌ Erro ao carregar asset {asset_path}: {e}")
            self._render_shape(parent, "rectangle", x, y, color)
    
    def _render_connection(self, parent: ET.Element, connection: Dict):
        """Renderiza uma conexão entre componentes"""
        from_id = connection["from"]
        to_id = connection["to"]
        label = connection.get("label", "")
        style = connection.get("style", "solid")
        color = self._validate_color(connection.get("color", "#333333"))
        
        if from_id not in self.positions or to_id not in self.positions:
            self.log(f"⚠️  Conexão inválida: {from_id} -> {to_id}")
            return
        
        from_x, from_y = self.positions[from_id]
        to_x, to_y = self.positions[to_id]
        
        # Adjust to component centers
        from_x += self.component_width // 2
        from_y += self.component_height // 2
        to_x += self.component_width // 2
        to_y += self.component_height // 2
        
        # Draw line
        line_attrs = {
            "x1": str(from_x),
            "y1": str(from_y),
            "x2": str(to_x),
            "y2": str(to_y),
            "stroke": color,
            "stroke-width": "2"
        }
        
        if style == "dashed":
            line_attrs["stroke-dasharray"] = "8,4"
        elif style == "dotted":
            line_attrs["stroke-dasharray"] = "2,2"
        
        ET.SubElement(parent, "line", line_attrs)
        
        # Add arrowhead
        self._add_arrowhead(parent, from_x, from_y, to_x, to_y, color, style == "bidirectional")
        
        # Add label
        if label:
            mid_x = (from_x + to_x) // 2
            mid_y = (from_y + to_y) // 2 - 10
            
            # Background for label
            text_width = len(label) * 7
            ET.SubElement(parent, "rect", {
                "x": str(mid_x - text_width // 2),
                "y": str(mid_y - 12),
                "width": str(text_width),
                "height": "18",
                "fill": "#FFFFFF",
                "opacity": "0.9"
            })
            
            text = ET.SubElement(parent, "text", {
                "x": str(mid_x),
                "y": str(mid_y),
                "class": "connection-label"
            })
            text.text = label
        
        self.log(f"Conexão: {from_id} -> {to_id}")
    
    def _add_arrowhead(self, parent: ET.Element, x1: int, y1: int, x2: int, y2: int, color: str, bidirectional: bool = False):
        """Adiciona seta no final da linha"""
        import math
        
        # Calculate angle
        dx = x2 - x1
        dy = y2 - y1
        angle = math.atan2(dy, dx)
        
        # Arrowhead size
        arrow_length = 12
        arrow_width = 8
        
        # Arrowhead points
        tip_x = x2
        tip_y = y2
        
        left_x = tip_x - arrow_length * math.cos(angle) - arrow_width * math.sin(angle)
        left_y = tip_y - arrow_length * math.sin(angle) + arrow_width * math.cos(angle)
        
        right_x = tip_x - arrow_length * math.cos(angle) + arrow_width * math.sin(angle)
        right_y = tip_y - arrow_length * math.sin(angle) - arrow_width * math.cos(angle)
        
        points = f"{tip_x},{tip_y} {left_x},{left_y} {right_x},{right_y}"
        
        ET.SubElement(parent, "polygon", {
            "points": points,
            "fill": color
        })
        
        # Bidirectional: add arrowhead at start too
        if bidirectional:
            tip_x = x1
            tip_y = y1
            angle = angle + math.pi  # Reverse direction
            
            left_x = tip_x - arrow_length * math.cos(angle) - arrow_width * math.sin(angle)
            left_y = tip_y - arrow_length * math.sin(angle) + arrow_width * math.cos(angle)
            
            right_x = tip_x - arrow_length * math.cos(angle) + arrow_width * math.sin(angle)
            right_y = tip_y - arrow_length * math.sin(angle) - arrow_width * math.cos(angle)
            
            points = f"{tip_x},{tip_y} {left_x},{left_y} {right_x},{right_y}"
            
            ET.SubElement(parent, "polygon", {
                "points": points,
                "fill": color
            })
    
    def _render_group(self, parent: ET.Element, group: Dict):
        """Renderiza um grupo/container"""
        group_id = group["id"]
        label = group.get("label", group_id)
        style = group.get("style", "dashed-box")
        color = self._validate_color(group.get("color", "#CCCCCC"))
        contains = group.get("contains", [])
        
        if not contains:
            return
        
        # Calculate bounding box
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = 0, 0
        
        for comp_id in contains:
            if comp_id in self.positions:
                x, y = self.positions[comp_id]
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + self.component_width)
                max_y = max(max_y, y + self.component_height)
        
        if min_x == float('inf'):
            return
        
        # Add padding
        padding = 30
        min_x -= padding
        min_y -= padding
        max_x += padding
        max_y += padding
        
        width = max_x - min_x
        height = max_y - min_y
        
        # Render box
        rect_attrs = {
            "x": str(min_x),
            "y": str(min_y),
            "width": str(width),
            "height": str(height),
            "fill": "none",
            "stroke": color,
            "stroke-width": "2"
        }
        
        if style == "dashed-box":
            rect_attrs["stroke-dasharray"] = "10,5"
        
        ET.SubElement(parent, "rect", rect_attrs)
        
        # Label
        text = ET.SubElement(parent, "text", {
            "x": str(min_x + 10),
            "y": str(min_y + 20),
            "class": "group-label"
        })
        text.text = label
        
        self.log(f"Grupo renderizado: {group_id}")
    
    def _render_annotation(self, parent: ET.Element, annotation: Dict):
        """Renderiza anotações"""
        target = annotation.get("target")
        text = annotation.get("text", "")
        position = annotation.get("position", "top")
        
        if target not in self.positions:
            return
        
        x, y = self.positions[target]
        
        # Position annotation
        if position == "top":
            ann_x = x + self.component_width // 2
            ann_y = y - 15
        elif position == "bottom":
            ann_x = x + self.component_width // 2
            ann_y = y + self.component_height + 25
        elif position == "left":
            ann_x = x - 10
            ann_y = y + self.component_height // 2
        else:  # right
            ann_x = x + self.component_width + 10
            ann_y = y + self.component_height // 2
        
        text_elem = ET.SubElement(parent, "text", {
            "x": str(ann_x),
            "y": str(ann_y),
            "class": "annotation-text",
            "text-anchor": "middle"
        })
        text_elem.text = text
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        """Formata XML para leitura humana"""
        from xml.dom import minidom
        
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


def main():
    parser = argparse.ArgumentParser(
        description="SVG Diagram Generator - Renderiza diagramas SVG a partir de YAML"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Arquivo YAML com o plano do diagrama"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("diagram.svg"),
        help="Arquivo SVG de saída (default: diagram.svg)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Apenas valida o YAML sem gerar SVG"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Modo verbose (mostra log detalhado)"
    )
    parser.add_argument(
        "--no-auto-layout",
        action="store_true",
        help="Desabilita layout automático (usa apenas posições manuais)"
    )
    
    args = parser.parse_args()
    
    # Load YAML
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            plan = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {args.input}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Erro ao parsear YAML: {e}")
        sys.exit(1)
    
    # Validate only mode
    if args.validate_only:
        from yaml_planner import DiagramPlanner
        planner = DiagramPlanner(interactive=False)
        success = planner.validate(args.input)
        sys.exit(0 if success else 1)
    
    # Render SVG
    print(f"📐 Renderizando diagrama: {plan.get('metadata', {}).get('title', 'Untitled')}")
    
    renderer = SVGDiagramRenderer(plan, verbose=args.verbose)
    svg_content = renderer.render_svg()
    
    # Save SVG
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"✅ Diagrama gerado: {args.output}")
    print(f"   Componentes: {len(plan.get('components', []))}")
    print(f"   Conexões: {len(plan.get('connections', []))}")
    print(f"   Dimensões: {renderer.width}x{renderer.height}px")


if __name__ == "__main__":
    main()
