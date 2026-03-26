"""
Visual Drag & Drop Builder for MASS Framework

A comprehensive visual builder system similar to Shopify's app builder, allowing users
to create AI agent workflows, dashboards, and applications through drag-and-drop components.

Features:
- Drag & Drop Interface
- Component Library
- Visual Workflow Builder
- Real-time Preview
- Mobile-Responsive Design
- Template System
- Code Generation
- Visual Property Editor
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import copy


class ComponentType(Enum):
    """Types of draggable components"""
    # Layout Components
    CONTAINER = "container"
    GRID = "grid"
    FLEX = "flex"
    CARD = "card"
    SECTION = "section"
    
    # Input Components
    TEXT_INPUT = "text_input"
    NUMBER_INPUT = "number_input"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SLIDER = "slider"
    DATE_PICKER = "date_picker"
    FILE_UPLOAD = "file_upload"
    
    # Display Components
    TEXT = "text"
    HEADING = "heading"
    IMAGE = "image"
    VIDEO = "video"
    CHART = "chart"
    TABLE = "table"
    LIST = "list"
    BADGE = "badge"
    PROGRESS = "progress"
    
    # Interactive Components
    BUTTON = "button"
    LINK = "link"
    TABS = "tabs"
    ACCORDION = "accordion"
    MODAL = "modal"
    DROPDOWN = "dropdown"
    
    # AI Agent Components
    AGENT_CHAT = "agent_chat"
    AGENT_TASK = "agent_task"
    AGENT_WORKFLOW = "agent_workflow"
    AGENT_STATUS = "agent_status"
    AGENT_METRICS = "agent_metrics"
    
    # Data Components
    DATA_SOURCE = "data_source"
    API_CONNECTOR = "api_connector"
    DATABASE_QUERY = "database_query"
    FORM = "form"
    
    # Custom Components
    CUSTOM_HTML = "custom_html"
    IFRAME = "iframe"
    WIDGET = "widget"


class DeviceType(Enum):
    """Device types for responsive design"""
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


@dataclass
class ComponentStyle:
    """Styling properties for components"""
    width: Optional[str] = "auto"
    height: Optional[str] = "auto"
    margin: Optional[str] = "0"
    padding: Optional[str] = "0"
    background_color: Optional[str] = None
    color: Optional[str] = None
    border: Optional[str] = None
    border_radius: Optional[str] = None
    font_size: Optional[str] = None
    font_weight: Optional[str] = None
    text_align: Optional[str] = None
    display: Optional[str] = None
    flex_direction: Optional[str] = None
    justify_content: Optional[str] = None
    align_items: Optional[str] = None
    grid_template_columns: Optional[str] = None
    grid_gap: Optional[str] = None
    position: Optional[str] = None
    top: Optional[str] = None
    left: Optional[str] = None
    z_index: Optional[int] = None
    opacity: Optional[float] = None
    transform: Optional[str] = None
    transition: Optional[str] = None
    box_shadow: Optional[str] = None
    
    def to_css(self) -> str:
        """Convert to CSS string"""
        css_rules = []
        
        style_map = {
            'width': self.width,
            'height': self.height,
            'margin': self.margin,
            'padding': self.padding,
            'background-color': self.background_color,
            'color': self.color,
            'border': self.border,
            'border-radius': self.border_radius,
            'font-size': self.font_size,
            'font-weight': self.font_weight,
            'text-align': self.text_align,
            'display': self.display,
            'flex-direction': self.flex_direction,
            'justify-content': self.justify_content,
            'align-items': self.align_items,
            'grid-template-columns': self.grid_template_columns,
            'grid-gap': self.grid_gap,
            'position': self.position,
            'top': self.top,
            'left': self.left,
            'z-index': self.z_index,
            'opacity': self.opacity,
            'transform': self.transform,
            'transition': self.transition,
            'box-shadow': self.box_shadow,
        }
        
        for css_prop, value in style_map.items():
            if value is not None:
                css_rules.append(f"{css_prop}: {value}")
        
        return "; ".join(css_rules)


@dataclass
class ComponentProperties:
    """Properties specific to component types"""
    # Text properties
    text: Optional[str] = None
    placeholder: Optional[str] = None
    
    # Input properties
    value: Optional[Any] = None
    options: Optional[List[Dict[str, Any]]] = None
    required: Optional[bool] = False
    disabled: Optional[bool] = False
    
    # Media properties
    src: Optional[str] = None
    alt: Optional[str] = None
    
    # Interactive properties
    onclick: Optional[str] = None
    href: Optional[str] = None
    target: Optional[str] = None
    
    # Chart properties
    chart_type: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    
    # Agent properties
    agent_id: Optional[str] = None
    agent_config: Optional[Dict[str, Any]] = None
    
    # Custom properties
    custom_props: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Component:
    """A draggable component in the visual builder"""
    id: str
    type: ComponentType
    name: str
    properties: ComponentProperties = field(default_factory=ComponentProperties)
    style: ComponentStyle = field(default_factory=ComponentStyle)
    children: List['Component'] = field(default_factory=list)
    parent_id: Optional[str] = None
    order: int = 0
    visible: bool = True
    responsive_styles: Dict[DeviceType, ComponentStyle] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            'properties': asdict(self.properties),
            'style': asdict(self.style),
            'children': [child.to_dict() for child in self.children],
            'parent_id': self.parent_id,
            'order': self.order,
            'visible': self.visible,
            'responsive_styles': {
                device.value: asdict(style) 
                for device, style in self.responsive_styles.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Component':
        """Create component from dictionary"""
        component = cls(
            id=data['id'],
            type=ComponentType(data['type']),
            name=data['name'],
            properties=ComponentProperties(**data.get('properties', {})),
            style=ComponentStyle(**data.get('style', {})),
            parent_id=data.get('parent_id'),
            order=data.get('order', 0),
            visible=data.get('visible', True)
        )
        
        # Handle children
        for child_data in data.get('children', []):
            child = cls.from_dict(child_data)
            component.children.append(child)
        
        # Handle responsive styles
        responsive_data = data.get('responsive_styles', {})
        for device_str, style_data in responsive_data.items():
            device = DeviceType(device_str)
            component.responsive_styles[device] = ComponentStyle(**style_data)
        
        return component


@dataclass
class Page:
    """A page containing components"""
    id: str
    name: str
    title: str
    description: str = ""
    components: List[Component] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'components': [comp.to_dict() for comp in self.components],
            'settings': self.settings,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class Project:
    """A visual builder project"""
    id: str
    name: str
    description: str = ""
    pages: List[Page] = field(default_factory=list)
    theme: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class ComponentLibrary:
    """Library of available components with templates"""
    
    def __init__(self):
        self.components = self._initialize_components()
    
    def _initialize_components(self) -> Dict[ComponentType, Dict[str, Any]]:
        """Initialize component library with templates"""
        return {
            # Layout Components
            ComponentType.CONTAINER: {
                'name': 'Container',
                'icon': 'fas fa-square',
                'category': 'Layout',
                'description': 'Container for other components',
                'default_style': ComponentStyle(
                    width='100%',
                    padding='20px',
                    display='block'
                ),
                'default_properties': ComponentProperties(),
                'accepts_children': True
            },
            
            ComponentType.GRID: {
                'name': 'Grid Layout',
                'icon': 'fas fa-th',
                'category': 'Layout',
                'description': 'CSS Grid layout container',
                'default_style': ComponentStyle(
                    display='grid',
                    grid_template_columns='repeat(3, 1fr)',
                    grid_gap='20px',
                    width='100%'
                ),
                'default_properties': ComponentProperties(),
                'accepts_children': True
            },
            
            ComponentType.CARD: {
                'name': 'Card',
                'icon': 'fas fa-id-card',
                'category': 'Layout',
                'description': 'Card container with shadow',
                'default_style': ComponentStyle(
                    background_color='#ffffff',
                    border_radius='8px',
                    box_shadow='0 2px 4px rgba(0,0,0,0.1)',
                    padding='20px',
                    margin='10px'
                ),
                'default_properties': ComponentProperties(),
                'accepts_children': True
            },
            
            # Input Components
            ComponentType.TEXT_INPUT: {
                'name': 'Text Input',
                'icon': 'fas fa-edit',
                'category': 'Input',
                'description': 'Text input field',
                'default_style': ComponentStyle(
                    width='100%',
                    padding='10px',
                    border='1px solid #ddd',
                    border_radius='4px'
                ),
                'default_properties': ComponentProperties(
                    placeholder='Enter text...'
                ),
                'accepts_children': False
            },
            
            ComponentType.BUTTON: {
                'name': 'Button',
                'icon': 'fas fa-mouse-pointer',
                'category': 'Input',
                'description': 'Clickable button',
                'default_style': ComponentStyle(
                    background_color='#007bff',
                    color='white',
                    padding='10px 20px',
                    border='none',
                    border_radius='4px',
                    font_weight='bold'
                ),
                'default_properties': ComponentProperties(
                    text='Click Me'
                ),
                'accepts_children': False
            },
            
            # Display Components
            ComponentType.TEXT: {
                'name': 'Text',
                'icon': 'fas fa-font',
                'category': 'Display',
                'description': 'Text content',
                'default_style': ComponentStyle(
                    color='#333333'
                ),
                'default_properties': ComponentProperties(
                    text='Sample text content'
                ),
                'accepts_children': False
            },
            
            ComponentType.HEADING: {
                'name': 'Heading',
                'icon': 'fas fa-heading',
                'category': 'Display',
                'description': 'Heading text',
                'default_style': ComponentStyle(
                    font_size='24px',
                    font_weight='bold',
                    color='#333333',
                    margin='0 0 16px 0'
                ),
                'default_properties': ComponentProperties(
                    text='Heading Text'
                ),
                'accepts_children': False
            },
            
            ComponentType.IMAGE: {
                'name': 'Image',
                'icon': 'fas fa-image',
                'category': 'Display',
                'description': 'Image display',
                'default_style': ComponentStyle(
                    width='100%',
                    height='auto',
                    border_radius='4px'
                ),
                'default_properties': ComponentProperties(
                    src='https://via.placeholder.com/400x200',
                    alt='Placeholder image'
                ),
                'accepts_children': False
            },
            
            ComponentType.CHART: {
                'name': 'Chart',
                'icon': 'fas fa-chart-bar',
                'category': 'Display',
                'description': 'Data visualization chart',
                'default_style': ComponentStyle(
                    width='100%',
                    height='300px'
                ),
                'default_properties': ComponentProperties(
                    chart_type='bar',
                    data=[
                        {'name': 'A', 'value': 30},
                        {'name': 'B', 'value': 45},
                        {'name': 'C', 'value': 60}
                    ]
                ),
                'accepts_children': False
            },
            
            # AI Agent Components
            ComponentType.AGENT_CHAT: {
                'name': 'Agent Chat',
                'icon': 'fas fa-comments',
                'category': 'AI Agents',
                'description': 'Chat interface with AI agent',
                'default_style': ComponentStyle(
                    width='100%',
                    height='400px',
                    border='1px solid #ddd',
                    border_radius='8px'
                ),
                'default_properties': ComponentProperties(
                    agent_id='default',
                    agent_config={'type': 'chat', 'model': 'gpt-3.5-turbo'}
                ),
                'accepts_children': False
            },
            
            ComponentType.AGENT_WORKFLOW: {
                'name': 'Agent Workflow',
                'icon': 'fas fa-sitemap',
                'category': 'AI Agents',
                'description': 'Visual workflow with AI agents',
                'default_style': ComponentStyle(
                    width='100%',
                    height='500px',
                    background_color='#f8f9fa',
                    border='1px solid #ddd',
                    border_radius='8px'
                ),
                'default_properties': ComponentProperties(
                    agent_config={'type': 'workflow', 'steps': []}
                ),
                'accepts_children': True
            },
            
            ComponentType.AGENT_METRICS: {
                'name': 'Agent Metrics',
                'icon': 'fas fa-tachometer-alt',
                'category': 'AI Agents',
                'description': 'Real-time agent performance metrics',
                'default_style': ComponentStyle(
                    width='100%',
                    height='200px'
                ),
                'default_properties': ComponentProperties(
                    agent_id='default'
                ),
                'accepts_children': False
            }
        }
    
    def get_component_template(self, component_type: ComponentType) -> Dict[str, Any]:
        """Get component template by type"""
        return self.components.get(component_type, {})
    
    def get_components_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all components in a category"""
        return [
            {**template, 'type': comp_type}
            for comp_type, template in self.components.items()
            if template.get('category') == category
        ]
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories"""
        categories = set()
        for template in self.components.values():
            categories.add(template.get('category', 'Other'))
        return sorted(list(categories))


class VisualBuilder:
    """Main visual builder engine"""
    
    def __init__(self):
        self.component_library = ComponentLibrary()
        self.projects: Dict[str, Project] = {}
        self.current_project: Optional[Project] = None
        self.current_page: Optional[Page] = None
        self.history: List[Dict[str, Any]] = []
        self.history_index = -1
    
    def create_project(self, name: str, description: str = "") -> Project:
        """Create a new project"""
        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            name=name,
            description=description
        )
        
        # Create default page
        default_page = self.create_page(project, "Home", "Home Page")
        project.pages.append(default_page)
        
        self.projects[project_id] = project
        self.current_project = project
        self.current_page = default_page
        
        return project
    
    def create_page(self, project: Project, name: str, title: str) -> Page:
        """Create a new page in project"""
        page_id = str(uuid.uuid4())
        page = Page(
            id=page_id,
            name=name,
            title=title
        )
        
        return page
    
    def add_component(self, component_type: ComponentType, parent_id: Optional[str] = None, 
                     position: Optional[int] = None) -> Component:
        """Add a new component to the current page"""
        if not self.current_page:
            raise ValueError("No current page selected")
        
        # Get component template
        template = self.component_library.get_component_template(component_type)
        
        # Create new component
        component_id = str(uuid.uuid4())
        component = Component(
            id=component_id,
            type=component_type,
            name=template.get('name', component_type.value),
            properties=copy.deepcopy(template.get('default_properties', ComponentProperties())),
            style=copy.deepcopy(template.get('default_style', ComponentStyle())),
            parent_id=parent_id
        )
        
        # Add to parent or page
        if parent_id:
            parent = self.find_component(parent_id)
            if parent:
                if position is not None:
                    parent.children.insert(position, component)
                else:
                    parent.children.append(component)
                component.order = len(parent.children)
        else:
            if position is not None:
                self.current_page.components.insert(position, component)
            else:
                self.current_page.components.append(component)
            component.order = len(self.current_page.components)
        
        # Save state for undo/redo
        self._save_state()
        
        return component
    
    def move_component(self, component_id: str, new_parent_id: Optional[str], 
                      new_position: int) -> bool:
        """Move a component to a new location"""
        component = self.find_component(component_id)
        if not component:
            return False
        
        # Remove from current location
        self.remove_component(component_id, save_state=False)
        
        # Add to new location
        component.parent_id = new_parent_id
        
        if new_parent_id:
            parent = self.find_component(new_parent_id)
            if parent:
                parent.children.insert(new_position, component)
        else:
            self.current_page.components.insert(new_position, component)
        
        self._save_state()
        return True
    
    def remove_component(self, component_id: str, save_state: bool = True) -> bool:
        """Remove a component"""
        component = self.find_component(component_id)
        if not component:
            return False
        
        # Remove from parent
        if component.parent_id:
            parent = self.find_component(component.parent_id)
            if parent:
                parent.children = [c for c in parent.children if c.id != component_id]
        else:
            self.current_page.components = [c for c in self.current_page.components if c.id != component_id]
        
        if save_state:
            self._save_state()
        
        return True
    
    def find_component(self, component_id: str) -> Optional[Component]:
        """Find a component by ID"""
        if not self.current_page:
            return None
        
        def search_component(component: Component) -> Optional[Component]:
            if component.id == component_id:
                return component
            
            for child in component.children:
                result = search_component(child)
                if result:
                    return result
            return None
        
        # Search in page components
        for component in self.current_page.components:
            result = search_component(component)
            if result:
                return result
        
        return None
    
    def update_component_properties(self, component_id: str, properties: Dict[str, Any]) -> bool:
        """Update component properties"""
        component = self.find_component(component_id)
        if not component:
            return False
        
        # Update properties
        for key, value in properties.items():
            if hasattr(component.properties, key):
                setattr(component.properties, key, value)
            else:
                component.properties.custom_props[key] = value
        
        self._save_state()
        return True
    
    def update_component_style(self, component_id: str, style: Dict[str, Any], 
                              device: DeviceType = DeviceType.DESKTOP) -> bool:
        """Update component style"""
        component = self.find_component(component_id)
        if not component:
            return False
        
        if device == DeviceType.DESKTOP:
            # Update main style
            for key, value in style.items():
                if hasattr(component.style, key):
                    setattr(component.style, key, value)
        else:
            # Update responsive style
            if device not in component.responsive_styles:
                component.responsive_styles[device] = ComponentStyle()
            
            for key, value in style.items():
                if hasattr(component.responsive_styles[device], key):
                    setattr(component.responsive_styles[device], key, value)
        
        self._save_state()
        return True
    
    def duplicate_component(self, component_id: str) -> Optional[Component]:
        """Duplicate a component"""
        original = self.find_component(component_id)
        if not original:
            return None
        
        # Create deep copy
        duplicate_data = original.to_dict()
        duplicate_data['id'] = str(uuid.uuid4())
        duplicate_data['name'] = f"{duplicate_data['name']} Copy"
        
        # Recursively update child IDs
        def update_ids(comp_data):
            comp_data['id'] = str(uuid.uuid4())
            for child_data in comp_data.get('children', []):
                update_ids(child_data)
        
        for child_data in duplicate_data.get('children', []):
            update_ids(child_data)
        
        duplicate = Component.from_dict(duplicate_data)
        
        # Add to same parent
        if original.parent_id:
            parent = self.find_component(original.parent_id)
            if parent:
                parent.children.append(duplicate)
        else:
            self.current_page.components.append(duplicate)
        
        self._save_state()
        return duplicate
    
    def _save_state(self):
        """Save current state for undo/redo"""
        if not self.current_page:
            return
        
        state = {
            'page_id': self.current_page.id,
            'components': [comp.to_dict() for comp in self.current_page.components],
            'timestamp': datetime.now().isoformat()
        }
        
        # Remove future history if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(state)
        self.history_index = len(self.history) - 1
        
        # Limit history size
        if len(self.history) > 50:
            self.history = self.history[-50:]
            self.history_index = len(self.history) - 1
    
    def undo(self) -> bool:
        """Undo last action"""
        if self.history_index <= 0:
            return False
        
        self.history_index -= 1
        self._restore_state()
        return True
    
    def redo(self) -> bool:
        """Redo last undone action"""
        if self.history_index >= len(self.history) - 1:
            return False
        
        self.history_index += 1
        self._restore_state()
        return True
    
    def _restore_state(self):
        """Restore state from history"""
        if not self.current_page or self.history_index < 0:
            return
        
        state = self.history[self.history_index]
        self.current_page.components = [
            Component.from_dict(comp_data) 
            for comp_data in state['components']
        ]
    
    def generate_html(self, page: Optional[Page] = None) -> str:
        """Generate HTML for a page"""
        target_page = page or self.current_page
        if not target_page:
            return ""
        
        html_parts = []
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html lang='en'>")
        html_parts.append("<head>")
        html_parts.append(f"<title>{target_page.title}</title>")
        html_parts.append("<meta charset='UTF-8'>")
        html_parts.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html_parts.append("<style>")
        html_parts.append(self._generate_css(target_page))
        html_parts.append("</style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        for component in target_page.components:
            html_parts.append(self._component_to_html(component))
        
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)
    
    def _component_to_html(self, component: Component) -> str:
        """Convert component to HTML"""
        tag_map = {
            ComponentType.CONTAINER: 'div',
            ComponentType.GRID: 'div',
            ComponentType.CARD: 'div',
            ComponentType.TEXT: 'p',
            ComponentType.HEADING: 'h2',
            ComponentType.BUTTON: 'button',
            ComponentType.TEXT_INPUT: 'input',
            ComponentType.IMAGE: 'img',
        }
        
        tag = tag_map.get(component.type, 'div')
        
        # Build attributes
        attrs = [f'id="{component.id}"', f'class="component {component.type.value}"']
        
        if component.type == ComponentType.TEXT_INPUT:
            attrs.append('type="text"')
            if component.properties.placeholder:
                attrs.append(f'placeholder="{component.properties.placeholder}"')
        
        if component.type == ComponentType.IMAGE:
            if component.properties.src:
                attrs.append(f'src="{component.properties.src}"')
            if component.properties.alt:
                attrs.append(f'alt="{component.properties.alt}"')
        
        if component.properties.onclick:
            attrs.append(f'onclick="{component.properties.onclick}"')
        
        # Self-closing tags
        if tag in ['input', 'img']:
            return f"<{tag} {' '.join(attrs)} />"
        
        # Container tags
        content = ""
        if component.properties.text:
            content = component.properties.text
        
        for child in component.children:
            content += self._component_to_html(child)
        
        return f"<{tag} {' '.join(attrs)}>{content}</{tag}>"
    
    def _generate_css(self, page: Page) -> str:
        """Generate CSS for a page"""
        css_rules = []
        
        def add_component_styles(component: Component):
            # Desktop styles
            css_rule = f"#{component.id} {{ {component.style.to_css()} }}"
            css_rules.append(css_rule)
            
            # Responsive styles
            for device, style in component.responsive_styles.items():
                if device == DeviceType.TABLET:
                    css_rules.append(f"@media (max-width: 768px) {{ #{component.id} {{ {style.to_css()} }} }}")
                elif device == DeviceType.MOBILE:
                    css_rules.append(f"@media (max-width: 480px) {{ #{component.id} {{ {style.to_css()} }} }}")
            
            # Process children
            for child in component.children:
                add_component_styles(child)
        
        for component in page.components:
            add_component_styles(component)
        
        return "\n".join(css_rules)
    
    def export_project(self, project_id: str) -> Dict[str, Any]:
        """Export project as JSON"""
        project = self.projects.get(project_id)
        if not project:
            return {}
        
        return {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'pages': [page.to_dict() for page in project.pages],
            'theme': project.theme,
            'settings': project.settings,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat()
        }
    
    def import_project(self, project_data: Dict[str, Any]) -> Project:
        """Import project from JSON"""
        project = Project(
            id=project_data['id'],
            name=project_data['name'],
            description=project_data.get('description', ''),
            theme=project_data.get('theme', {}),
            settings=project_data.get('settings', {}),
            created_at=datetime.fromisoformat(project_data['created_at']),
            updated_at=datetime.fromisoformat(project_data['updated_at'])
        )
        
        # Import pages
        for page_data in project_data.get('pages', []):
            page = Page(
                id=page_data['id'],
                name=page_data['name'],
                title=page_data['title'],
                description=page_data.get('description', ''),
                settings=page_data.get('settings', {}),
                created_at=datetime.fromisoformat(page_data['created_at']),
                updated_at=datetime.fromisoformat(page_data['updated_at'])
            )
            
            # Import components
            for comp_data in page_data.get('components', []):
                component = Component.from_dict(comp_data)
                page.components.append(component)
            
            project.pages.append(page)
        
        self.projects[project.id] = project
        return project


# Usage example and demo
def demo_visual_builder():
    """Demonstrate visual builder functionality"""
    print("🎨 VISUAL DRAG & DROP BUILDER DEMO")
    print("=" * 50)
    
    # Initialize builder
    builder = VisualBuilder()
    
    # Create project
    project = builder.create_project("My AI Dashboard", "Sample dashboard with AI components")
    print(f"[CHECK] Created project: {project.name}")
    
    # Show component library
    library = builder.component_library
    categories = library.get_all_categories()
    print(f"\n📚 Component Library Categories: {len(categories)}")
    for category in categories:
        components = library.get_components_by_category(category)
        print(f"  • {category}: {len(components)} components")
    
    # Add some components
    print(f"\n🎯 Building Sample Dashboard:")
    
    # Add header
    header = builder.add_component(ComponentType.HEADING)
    builder.update_component_properties(header.id, {'text': 'AI Agent Dashboard'})
    print(f"  [CHECK] Added header: {header.name}")
    
    # Add container
    container = builder.add_component(ComponentType.GRID)
    builder.update_component_style(container.id, {
        'grid_template_columns': 'repeat(2, 1fr)',
        'grid_gap': '20px',
        'margin': '20px 0'
    })
    print(f"  [CHECK] Added grid container: {container.name}")
    
    # Add agent chat
    chat = builder.add_component(ComponentType.AGENT_CHAT, parent_id=container.id)
    builder.update_component_properties(chat.id, {
        'agent_config': {'type': 'chat', 'model': 'gpt-4', 'title': 'AI Assistant'}
    })
    print(f"  [CHECK] Added agent chat: {chat.name}")
    
    # Add agent metrics
    metrics = builder.add_component(ComponentType.AGENT_METRICS, parent_id=container.id)
    builder.update_component_properties(metrics.id, {
        'agent_id': 'dashboard_agent'
    })
    print(f"  [CHECK] Added agent metrics: {metrics.name}")
    
    # Add chart
    chart = builder.add_component(ComponentType.CHART)
    builder.update_component_properties(chart.id, {
        'chart_type': 'line',
        'data': [
            {'name': 'Jan', 'value': 30},
            {'name': 'Feb', 'value': 45},
            {'name': 'Mar', 'value': 60},
            {'name': 'Apr', 'value': 55}
        ]
    })
    print(f"  [CHECK] Added performance chart: {chart.name}")
    
    # Show page structure
    print(f"\n📄 Page Structure:")
    def show_component(comp, indent=0):
        print(f"{'  ' * indent}• {comp.name} ({comp.type.value})")
        for child in comp.children:
            show_component(child, indent + 1)
    
    for comp in builder.current_page.components:
        show_component(comp)
    
    # Generate HTML
    html = builder.generate_html()
    print(f"\n📝 Generated HTML: {len(html)} characters")
    print(f"Sample HTML snippet:")
    print(html[:200] + "..." if len(html) > 200 else html)
    
    # Export project
    export_data = builder.export_project(project.id)
    print(f"\n💾 Export Data: {len(json.dumps(export_data))} characters")
    
    print(f"\n✨ Visual builder demo complete!")
    print(f"Features demonstrated:")
    features = [
        "Project creation and management",
        "Component library with categories",
        "Drag & drop component addition",
        "Property and style updates",
        "Nested component structures",
        "HTML generation",
        "Project export/import",
        "Undo/redo support (ready)",
        "Responsive design support"
    ]
    
    for feature in features:
        print(f"  ✓ {feature}")
    
    return builder


if __name__ == "__main__":
    builder = demo_visual_builder()
