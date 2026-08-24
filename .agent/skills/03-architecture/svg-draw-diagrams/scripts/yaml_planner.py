#!/usr/bin/env python3
"""
YAML Diagram Planner
Gerador interativo de planos YAML para diagramas SVG
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml


class DiagramPlanner:
    """Planejador interativo de diagramas"""
    
    DIAGRAM_TYPES = ["architecture", "flow", "component", "sequence"]
    ORIENTATIONS = ["horizontal", "vertical", "hierarchical"]
    SHAPE_TYPES = ["rectangle", "circle", "cylinder", "diamond", "cloud", "hexagon"]
    
    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        self.plan: Dict = {
            "metadata": {},
            "components": [],
            "connections": [],
            "groups": [],
            "annotations": []
        }
    
    def ask(self, question: str, options: Optional[List[str]] = None, default: str = "") -> str:
        """Faz uma pergunta ao usuário"""
        if not self.interactive:
            return default
        
        if options:
            print(f"\n{question}")
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")
            
            while True:
                choice = input(f"Escolha (1-{len(options)}): ").strip()
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(options):
                        return options[idx]
                except ValueError:
                    pass
                print("Opção inválida. Tente novamente.")
        else:
            response = input(f"{question} [{default}]: ").strip()
            return response or default
    
    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Pergunta sim/não"""
        if not self.interactive:
            return default
        
        default_str = "S/n" if default else "s/N"
        response = input(f"{question} [{default_str}]: ").strip().lower()
        
        if not response:
            return default
        return response in ['s', 'sim', 'y', 'yes']
    
    def build_plan(self) -> Dict:
        """Constrói o plano do diagrama interativamente"""
        
        print("=" * 60)
        print("SVG DIAGRAM PLANNER")
        print("=" * 60)
        
        # Metadata
        print("\n📋 METADADOS DO DIAGRAMA")
        self.plan["metadata"]["title"] = self.ask("Título do diagrama", default="Architecture Diagram")
        self.plan["metadata"]["type"] = self.ask("Tipo de diagrama", self.DIAGRAM_TYPES, "architecture")
        self.plan["metadata"]["orientation"] = self.ask("Orientação", self.ORIENTATIONS, "horizontal")
        
        # Dimensions
        use_custom_size = self.ask_yes_no("Usar dimensões customizadas?", False)
        if use_custom_size:
            width = int(self.ask("Largura (px)", default="1200"))
            height = int(self.ask("Altura (px)", default="800"))
            self.plan["metadata"]["dimensions"] = {"width": width, "height": height}
        else:
            self.plan["metadata"]["dimensions"] = {"width": 1200, "height": 800}
        
        # Assets vs Basic Shapes
        print("\n🎨 ESTILO DE COMPONENTES")
        use_assets = self.ask_yes_no("Usar ícones customizados da pasta assets/?", False)
        
        # Components
        print("\n🔷 COMPONENTES")
        print("Digite os componentes principais (um por linha, linha vazia para finalizar)")
        
        component_count = 1
        while True:
            label = input(f"Componente #{component_count} (ou Enter para finalizar): ").strip()
            if not label:
                break
            
            comp_id = label.lower().replace(" ", "-").replace("_", "-")
            
            component = {
                "id": comp_id,
                "label": label,
                "type": "service"
            }
            
            if use_assets:
                icon_name = self.ask(f"  Nome do arquivo de ícone (em assets/)", default=f"{comp_id}-icon.svg")
                component["icon"] = f"assets/{icon_name}"
            else:
                shape = self.ask(f"  Forma geométrica para '{label}'", self.SHAPE_TYPES, "rectangle")
                component["icon"] = shape
            
            color = self.ask(f"  Cor (hex) para '{label}'", default=self._auto_color(component_count))
            component["color"] = color
            
            component["position"] = "auto"
            
            self.plan["components"].append(component)
            component_count += 1
        
        if len(self.plan["components"]) < 2:
            print("\n⚠️  Aviso: Adicione pelo menos 2 componentes para criar conexões.")
            return self.plan
        
        # Connections
        print("\n🔗 CONEXÕES")
        print("Defina as conexões entre componentes")
        print("Componentes disponíveis:", ", ".join([c["id"] for c in self.plan["components"]]))
        
        add_connections = self.ask_yes_no("Adicionar conexões?", True)
        
        connection_count = 1
        while add_connections:
            print(f"\nConexão #{connection_count}")
            from_id = self.ask("  De (ID do componente)")
            to_id = self.ask("  Para (ID do componente)")
            
            # Validate IDs
            valid_ids = [c["id"] for c in self.plan["components"]]
            if from_id not in valid_ids or to_id not in valid_ids:
                print(f"  ⚠️  IDs inválidos. Use um destes: {', '.join(valid_ids)}")
                continue
            
            label = self.ask("  Label da conexão (opcional)", default="")
            style = self.ask("  Estilo", ["solid", "dashed", "dotted", "bidirectional"], "solid")
            
            connection = {
                "from": from_id,
                "to": to_id,
                "style": style
            }
            
            if label:
                connection["label"] = label
            
            self.plan["connections"].append(connection)
            connection_count += 1
            
            add_connections = self.ask_yes_no("Adicionar outra conexão?", False)
        
        # Groups (optional)
        print("\n📦 GRUPOS (Opcional)")
        add_groups = self.ask_yes_no("Adicionar grupos/containers?", False)
        
        if add_groups:
            print("Grupos agrupam componentes visualmente (ex: VPC, Kubernetes Cluster)")
            while True:
                group_label = input("Nome do grupo (ou Enter para finalizar): ").strip()
                if not group_label:
                    break
                
                group_id = group_label.lower().replace(" ", "-")
                components_in_group = self.ask(f"  IDs dos componentes (separados por vírgula)").split(",")
                components_in_group = [c.strip() for c in components_in_group]
                
                group = {
                    "id": group_id,
                    "label": group_label,
                    "style": "dashed-box",
                    "contains": components_in_group
                }
                
                self.plan["groups"].append(group)
        
        return self.plan
    
    def _auto_color(self, index: int) -> str:
        """Gera cores automáticas para componentes"""
        colors = [
            "#4A90E2",  # Blue
            "#E94B3C",  # Red
            "#50C878",  # Green
            "#F5A623",  # Orange
            "#9013FE",  # Purple
            "#50E3C2",  # Cyan
            "#D0021B",  # Dark Red
            "#7ED321",  # Lime
        ]
        return colors[(index - 1) % len(colors)]
    
    def save(self, output_path: Path):
        """Salva o plano em arquivo YAML"""
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.plan, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"\n✅ Plano salvo em: {output_path}")
        print(f"\nPróximo passo:")
        print(f"  python scripts/svg_diagram_generator.py {output_path} -o diagram.svg")
    
    def validate(self, yaml_path: Path) -> bool:
        """Valida um arquivo YAML existente"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                plan = yaml.safe_load(f)
            
            errors = []
            
            # Required fields
            if "metadata" not in plan:
                errors.append("Campo 'metadata' obrigatório")
            else:
                required_meta = ["title", "type", "orientation"]
                for field in required_meta:
                    if field not in plan["metadata"]:
                        errors.append(f"Campo 'metadata.{field}' obrigatório")
            
            if "components" not in plan or not plan["components"]:
                errors.append("Deve haver pelo menos 1 componente")
            
            # Validate component IDs
            if "components" in plan:
                ids = [c.get("id") for c in plan["components"]]
                if len(ids) != len(set(ids)):
                    errors.append("IDs de componentes devem ser únicos")
                
                for comp in plan["components"]:
                    if "id" not in comp:
                        errors.append(f"Componente sem ID: {comp}")
                    if "label" not in comp:
                        errors.append(f"Componente '{comp.get('id')}' sem label")
            
            # Validate connections
            if "connections" in plan:
                component_ids = [c["id"] for c in plan.get("components", [])]
                for conn in plan["connections"]:
                    if "from" not in conn or "to" not in conn:
                        errors.append(f"Conexão inválida: {conn}")
                    elif conn["from"] not in component_ids:
                        errors.append(f"Conexão referencia ID inexistente: {conn['from']}")
                    elif conn["to"] not in component_ids:
                        errors.append(f"Conexão referencia ID inexistente: {conn['to']}")
            
            if errors:
                print("❌ ERROS DE VALIDAÇÃO:")
                for error in errors:
                    print(f"  - {error}")
                return False
            
            print("✅ YAML válido!")
            print(f"  - {len(plan.get('components', []))} componentes")
            print(f"  - {len(plan.get('connections', []))} conexões")
            print(f"  - {len(plan.get('groups', []))} grupos")
            return True
            
        except yaml.YAMLError as e:
            print(f"❌ Erro de parsing YAML: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro ao validar: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="YAML Diagram Planner - Gerador interativo de planos para diagramas SVG"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("diagram-plan.yml"),
        help="Arquivo de saída para o plano YAML (default: diagram-plan.yml)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=True,
        help="Modo interativo (padrão)"
    )
    parser.add_argument(
        "-t", "--title",
        type=str,
        help="Título do diagrama (pula modo interativo para metadata)"
    )
    parser.add_argument(
        "--validate",
        type=Path,
        help="Valida um arquivo YAML existente sem gerar novo"
    )
    
    args = parser.parse_args()
    
    planner = DiagramPlanner(interactive=args.interactive)
    
    # Validation mode
    if args.validate:
        success = planner.validate(args.validate)
        sys.exit(0 if success else 1)
    
    # Generation mode
    plan = planner.build_plan()
    planner.save(args.output)
    
    # Auto-validate
    print("\n🔍 Validando plano gerado...")
    planner.validate(args.output)


if __name__ == "__main__":
    main()
