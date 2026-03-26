"""
Shopify-Style Visual Builder for MASS Framework
============================================

A comprehensive drag-and-drop visual builder with:
- Mobile-first responsive design
- Touch-friendly interactions
- Real-time preview
- Advanced component library
- Template marketplace
- Undo/redo functionality
- Collaborative editing
- Export to multiple formats
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import asyncio
from datetime import datetime, timezone
import base64
import hashlib

class BuilderTheme(Enum):
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"

class InteractionMode(Enum):
    MOUSE = "mouse"
    TOUCH = "touch"
    KEYBOARD = "keyboard"

class ComponentCategory(Enum):
    LAYOUT = "layout"
    CONTENT = "content"
    MEDIA = "media"
    FORMS = "forms"
    NAVIGATION = "navigation"
    AI_AGENTS = "ai_agents"
    DATA_VIZ = "data_viz"
    ECOMMERCE = "ecommerce"
    SOCIAL = "social"
    ADVANCED = "advanced"

class ResponsiveBreakpoint(Enum):
    MOBILE = "mobile"      # < 768px
    TABLET = "tablet"      # 768px - 1024px
    DESKTOP = "desktop"    # > 1024px
    WIDE = "wide"         # > 1440px

@dataclass
class Position:
    """Represents position with support for relative and absolute positioning"""
    x: float = 0
    y: float = 0
    z_index: int = 0
    position_type: str = "relative"  # relative, absolute, fixed, sticky
    
class Size:
    """Represents size with responsive breakpoints"""
    def __init__(self):
        self.breakpoints = {
            ResponsiveBreakpoint.MOBILE: {"width": "100%", "height": "auto"},
            ResponsiveBreakpoint.TABLET: {"width": "100%", "height": "auto"},
            ResponsiveBreakpoint.DESKTOP: {"width": "auto", "height": "auto"},
            ResponsiveBreakpoint.WIDE: {"width": "auto", "height": "auto"}
        }
    
    def set_size(self, breakpoint: ResponsiveBreakpoint, width: str, height: str):
        self.breakpoints[breakpoint] = {"width": width, "height": height}
    
    def get_size(self, breakpoint: ResponsiveBreakpoint) -> Dict[str, str]:
        return self.breakpoints.get(breakpoint, {"width": "auto", "height": "auto"})

@dataclass
class StyleProperties:
    """Comprehensive styling properties with responsive support"""
    # Colors
    background_color: str = "#ffffff"
    text_color: str = "#000000"
    border_color: str = "#e5e5e5"
    
    # Typography
    font_family: str = "'Inter', sans-serif"
    font_size: str = "16px"
    font_weight: str = "400"
    line_height: str = "1.5"
    text_align: str = "left"
    
    # Spacing
    margin: str = "0"
    padding: str = "16px"
    
    # Border
    border_width: str = "0"
    border_style: str = "solid"
    border_radius: str = "8px"
    
    # Layout
    display: str = "block"
    flex_direction: str = "row"
    justify_content: str = "flex-start"
    align_items: str = "stretch"
    gap: str = "16px"
    
    # Effects
    box_shadow: str = "none"
    opacity: float = 1.0
    transform: str = "none"
    transition: str = "all 0.3s ease"
    
    # Responsive overrides
    responsive_overrides: Dict[ResponsiveBreakpoint, Dict[str, Any]] = field(default_factory=dict)
    
    def get_css(self, breakpoint: ResponsiveBreakpoint = ResponsiveBreakpoint.DESKTOP) -> str:
        """Generate CSS string for the given breakpoint"""
        base_styles = {
            'background-color': self.background_color,
            'color': self.text_color,
            'border-color': self.border_color,
            'font-family': self.font_family,
            'font-size': self.font_size,
            'font-weight': self.font_weight,
            'line-height': self.line_height,
            'text-align': self.text_align,
            'margin': self.margin,
            'padding': self.padding,
            'border-width': self.border_width,
            'border-style': self.border_style,
            'border-radius': self.border_radius,
            'display': self.display,
            'flex-direction': self.flex_direction,
            'justify-content': self.justify_content,
            'align-items': self.align_items,
            'gap': self.gap,
            'box-shadow': self.box_shadow,
            'opacity': str(self.opacity),
            'transform': self.transform,
            'transition': self.transition
        }
        
        # Apply responsive overrides
        if breakpoint in self.responsive_overrides:
            base_styles.update(self.responsive_overrides[breakpoint])
        
        return '; '.join(f"{k}: {v}" for k, v in base_styles.items())

@dataclass
class Animation:
    """Animation properties for components"""
    name: str = ""
    duration: str = "0.3s"
    timing_function: str = "ease"
    delay: str = "0s"
    iteration_count: str = "1"
    direction: str = "normal"
    fill_mode: str = "both"
    
    def to_css(self) -> str:
        if not self.name:
            return ""
        return f"animation: {self.name} {self.duration} {self.timing_function} {self.delay} {self.iteration_count} {self.direction} {self.fill_mode}"

@dataclass
class ComponentAction:
    """Represents an action that can be triggered on a component"""
    action_type: str = "click"  # click, hover, scroll, load, etc.
    target: str = ""  # target component ID or URL
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: List[Dict[str, Any]] = field(default_factory=list)

class ShopifyStyleComponent:
    """Enhanced component with Shopify-style capabilities"""
    
    def __init__(
        self,
        component_type: str,
        name: str = "",
        category: ComponentCategory = ComponentCategory.CONTENT
    ):
        self.id = str(uuid.uuid4())
        self.component_type = component_type
        self.name = name or f"{component_type.title()} Component"
        self.category = category
        
        # Positioning and sizing
        self.position = Position()
        self.size = Size()
        
        # Styling
        self.styles = StyleProperties()
        self.animations = []
        
        # Content and properties
        self.content = {}
        self.properties = {}
        
        # Interactions
        self.actions = []
        self.hover_styles = None
        self.active_styles = None
        
        # Hierarchy
        self.children = []
        self.parent_id = None
        
        # State
        self.is_locked = False
        self.is_hidden = False
        self.is_selected = False
        
        # Metadata
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        self.version = 1
        
        # AI Integration
        self.ai_agent_config = {}
        self.data_bindings = {}
    
    def duplicate(self) -> 'ShopifyStyleComponent':
        """Create a duplicate of this component"""
        new_component = ShopifyStyleComponent(
            self.component_type,
            f"{self.name} Copy",
            self.category
        )
        
        # Copy all properties except ID and timestamps
        new_component.position = Position(**asdict(self.position))
        new_component.size = Size()
        new_component.size.breakpoints = self.size.breakpoints.copy()
        new_component.styles = StyleProperties(**asdict(self.styles))
        new_component.content = self.content.copy()
        new_component.properties = self.properties.copy()
        new_component.actions = [ComponentAction(**asdict(action)) for action in self.actions]
        new_component.ai_agent_config = self.ai_agent_config.copy()
        new_component.data_bindings = self.data_bindings.copy()
        
        return new_component
    
    def add_child(self, child: 'ShopifyStyleComponent'):
        """Add a child component"""
        child.parent_id = self.id
        self.children.append(child)
        self.update_timestamp()
    
    def remove_child(self, child_id: str):
        """Remove a child component"""
        self.children = [child for child in self.children if child.id != child_id]
        self.update_timestamp()
    
    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.version += 1
    
    def to_html(self, breakpoint: ResponsiveBreakpoint = ResponsiveBreakpoint.DESKTOP) -> str:
        """Generate HTML for this component"""
        tag = self._get_html_tag()
        attributes = self._get_html_attributes(breakpoint)
        inner_content = self._get_inner_content(breakpoint)
        
        if tag in ['img', 'input', 'br', 'hr']:
            return f'<{tag} {attributes} />'
        
        children_html = ''.join(child.to_html(breakpoint) for child in self.children)
        return f'<{tag} {attributes}>{inner_content}{children_html}</{tag}>'
    
    def _get_html_tag(self) -> str:
        """Get the appropriate HTML tag for this component"""
        tag_mapping = {
            'container': 'div',
            'text': 'p',
            'heading': 'h2',
            'button': 'button',
            'image': 'img',
            'input': 'input',
            'form': 'form',
            'navigation': 'nav',
            'header': 'header',
            'footer': 'footer',
            'section': 'section',
            'article': 'article',
            'aside': 'aside'
        }
        return tag_mapping.get(self.component_type, 'div')
    
    def _get_html_attributes(self, breakpoint: ResponsiveBreakpoint) -> str:
        """Get HTML attributes for this component"""
        attributes = [
            f'id="{self.id}"',
            f'class="component {self.component_type}"',
            f'style="{self.styles.get_css(breakpoint)}"'
        ]
        
        # Add component-specific attributes
        if self.component_type == 'image' and 'src' in self.content:
            attributes.append(f'src="{self.content["src"]}"')
            attributes.append(f'alt="{self.content.get("alt", "")}"')
        
        if self.component_type == 'input':
            attributes.append(f'type="{self.properties.get("input_type", "text")}"')
            if 'placeholder' in self.properties:
                attributes.append(f'placeholder="{self.properties["placeholder"]}"')
        
        return ' '.join(attributes)
    
    def _get_inner_content(self, breakpoint: ResponsiveBreakpoint) -> str:
        """Get the inner content for this component"""
        if self.component_type in ['text', 'heading', 'button']:
            return self.content.get('text', '')
        return ''

class ComponentTemplate:
    """Pre-built component templates"""
    
    def __init__(self, name: str, description: str, category: ComponentCategory):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.category = category
        self.components = []
        self.preview_image = ""
        self.tags = []
        self.is_premium = False
        self.downloads = 0
        self.rating = 0.0
    
    @classmethod
    def create_hero_section(cls) -> 'ComponentTemplate':
        """Create a hero section template"""
        template = cls(
            "Hero Section",
            "Modern hero section with heading, subtext, and call-to-action",
            ComponentCategory.LAYOUT
        )
        
        # Create hero container
        hero = ShopifyStyleComponent("section", "Hero Section", ComponentCategory.LAYOUT)
        hero.styles.background_color = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        hero.styles.padding = "80px 20px"
        hero.styles.text_align = "center"
        hero.styles.display = "flex"
        hero.styles.flex_direction = "column"
        hero.styles.justify_content = "center"
        hero.styles.align_items = "center"
        
        # Add heading
        heading = ShopifyStyleComponent("heading", "Hero Heading", ComponentCategory.CONTENT)
        heading.content["text"] = "Build Amazing AI Applications"
        heading.styles.font_size = "48px"
        heading.styles.font_weight = "700"
        heading.styles.text_color = "#ffffff"
        heading.styles.margin = "0 0 20px 0"
        
        # Add subtext
        subtext = ShopifyStyleComponent("text", "Hero Subtext", ComponentCategory.CONTENT)
        subtext.content["text"] = "Create powerful AI agents with our intuitive visual builder"
        subtext.styles.font_size = "20px"
        subtext.styles.text_color = "#ffffff"
        subtext.styles.opacity = 0.9
        subtext.styles.margin = "0 0 40px 0"
        
        # Add CTA button
        cta = ShopifyStyleComponent("button", "CTA Button", ComponentCategory.CONTENT)
        cta.content["text"] = "Get Started Free"
        cta.styles.background_color = "#ff6b6b"
        cta.styles.text_color = "#ffffff"
        cta.styles.padding = "16px 32px"
        cta.styles.border_radius = "8px"
        cta.styles.font_size = "18px"
        cta.styles.font_weight = "600"
        cta.styles.border_width = "0"
        
        hero.add_child(heading)
        hero.add_child(subtext)
        hero.add_child(cta)
        
        template.components = [hero]
        template.tags = ["hero", "landing", "cta", "modern"]
        
        return template
    
    @classmethod
    def create_feature_grid(cls) -> 'ComponentTemplate':
        """Create a feature grid template"""
        template = cls(
            "Feature Grid",
            "Responsive grid showcasing key features with icons",
            ComponentCategory.LAYOUT
        )
        
        # Create grid container
        grid = ShopifyStyleComponent("section", "Feature Grid", ComponentCategory.LAYOUT)
        grid.styles.padding = "80px 20px"
        grid.styles.display = "grid"
        grid.styles.gap = "32px"
        
        # Responsive grid
        grid.styles.responsive_overrides = {
            ResponsiveBreakpoint.MOBILE: {"grid-template-columns": "1fr"},
            ResponsiveBreakpoint.TABLET: {"grid-template-columns": "repeat(2, 1fr)"},
            ResponsiveBreakpoint.DESKTOP: {"grid-template-columns": "repeat(3, 1fr)"}
        }
        
        # Create feature cards
        features = [
            ("AI-Powered", "Leverage advanced AI agents for automation"),
            ("Drag & Drop", "Build applications without coding"),
            ("Real-time", "See changes instantly as you build")
        ]
        
        for title, description in features:
            card = ShopifyStyleComponent("container", f"Feature: {title}", ComponentCategory.CONTENT)
            card.styles.padding = "32px"
            card.styles.background_color = "#ffffff"
            card.styles.border_radius = "12px"
            card.styles.box_shadow = "0 4px 6px rgba(0, 0, 0, 0.1)"
            card.styles.text_align = "center"
            
            # Feature title
            card_title = ShopifyStyleComponent("heading", f"{title} Title", ComponentCategory.CONTENT)
            card_title.content["text"] = title
            card_title.styles.font_size = "24px"
            card_title.styles.font_weight = "600"
            card_title.styles.margin = "0 0 16px 0"
            
            # Feature description
            card_desc = ShopifyStyleComponent("text", f"{title} Description", ComponentCategory.CONTENT)
            card_desc.content["text"] = description
            card_desc.styles.text_color = "#666666"
            card_desc.styles.line_height = "1.6"
            
            card.add_child(card_title)
            card.add_child(card_desc)
            grid.add_child(card)
        
        template.components = [grid]
        template.tags = ["features", "grid", "cards", "responsive"]
        
        return template

class ProjectHistory:
    """Manages undo/redo functionality for the project"""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.history = []
        self.current_index = -1
    
    def save_state(self, project_data: Dict[str, Any]):
        """Save the current project state"""
        # Remove any states after current index (when undoing then making new changes)
        self.history = self.history[:self.current_index + 1]
        
        # Add new state
        state = {
            'data': json.dumps(project_data),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.history.append(state)
        
        # Maintain max history limit
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.current_index += 1
    
    def undo(self) -> Optional[Dict[str, Any]]:
        """Undo to previous state"""
        if self.current_index > 0:
            self.current_index -= 1
            return json.loads(self.history[self.current_index]['data'])
        return None
    
    def redo(self) -> Optional[Dict[str, Any]]:
        """Redo to next state"""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return json.loads(self.history[self.current_index]['data'])
        return None
    
    def can_undo(self) -> bool:
        return self.current_index > 0
    
    def can_redo(self) -> bool:
        return self.current_index < len(self.history) - 1

class CollaborationManager:
    """Manages real-time collaboration features"""
    
    def __init__(self):
        self.active_users = {}
        self.component_locks = {}
        self.change_queue = []
    
    def add_user(self, user_id: str, user_info: Dict[str, Any]):
        """Add a collaborative user"""
        self.active_users[user_id] = {
            **user_info,
            'cursor_position': {'x': 0, 'y': 0},
            'selected_components': [],
            'last_activity': datetime.now(timezone.utc).isoformat()
        }
    
    def remove_user(self, user_id: str):
        """Remove a user from collaboration"""
        if user_id in self.active_users:
            # Release any locks held by this user
            components_to_unlock = [
                comp_id for comp_id, lock_user in self.component_locks.items()
                if lock_user == user_id
            ]
            for comp_id in components_to_unlock:
                del self.component_locks[comp_id]
            
            del self.active_users[user_id]
    
    def lock_component(self, component_id: str, user_id: str) -> bool:
        """Lock a component for editing"""
        if component_id not in self.component_locks:
            self.component_locks[component_id] = user_id
            return True
        return self.component_locks[component_id] == user_id
    
    def unlock_component(self, component_id: str, user_id: str):
        """Unlock a component"""
        if self.component_locks.get(component_id) == user_id:
            del self.component_locks[component_id]
    
    def queue_change(self, change: Dict[str, Any]):
        """Queue a change for broadcast to other users"""
        change['timestamp'] = datetime.now(timezone.utc).isoformat()
        self.change_queue.append(change)

class ShopifyStyleBuilder:
    """Main visual builder class with Shopify-style functionality"""
    
    def __init__(self, project_name: str = "New Project"):
        self.project_id = str(uuid.uuid4())
        self.project_name = project_name
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        
        # Components and structure
        self.components = {}
        self.root_components = []
        self.selected_component_ids = []
        
        # Builder state
        self.current_breakpoint = ResponsiveBreakpoint.DESKTOP
        self.theme = BuilderTheme.LIGHT
        self.interaction_mode = InteractionMode.MOUSE
        self.zoom_level = 1.0
        self.canvas_offset = {'x': 0, 'y': 0}
        
        # Tools and panels
        self.active_tool = "select"  # select, text, image, etc.
        self.sidebar_panels = {
            'components': True,
            'layers': True,
            'properties': True,
            'assets': False
        }
        
        # History and collaboration
        self.history = ProjectHistory()
        self.collaboration = CollaborationManager()
        
        # Templates and assets
        self.templates = self._load_default_templates()
        self.assets = {}  # Uploaded images, fonts, etc.
        
        # AI Integration
        self.ai_suggestions = []
        self.auto_layout_enabled = True
        
        # Save initial state
        self.save_history()
    
    def _load_default_templates(self) -> List[ComponentTemplate]:
        """Load default component templates"""
        return [
            ComponentTemplate.create_hero_section(),
            ComponentTemplate.create_feature_grid()
        ]
    
    def add_component(self, component: ShopifyStyleComponent, parent_id: Optional[str] = None) -> str:
        """Add a component to the project"""
        self.components[component.id] = component
        
        if parent_id and parent_id in self.components:
            self.components[parent_id].add_child(component)
        else:
            self.root_components.append(component.id)
        
        self.save_history()
        return component.id
    
    def remove_component(self, component_id: str):
        """Remove a component and all its children"""
        if component_id not in self.components:
            return
        
        component = self.components[component_id]
        
        # Remove from parent
        if component.parent_id and component.parent_id in self.components:
            self.components[component.parent_id].remove_child(component_id)
        elif component_id in self.root_components:
            self.root_components.remove(component_id)
        
        # Remove children recursively
        for child in component.children:
            self.remove_component(child.id)
        
        # Remove from components
        del self.components[component_id]
        
        # Remove from selection
        if component_id in self.selected_component_ids:
            self.selected_component_ids.remove(component_id)
        
        self.save_history()
    
    def duplicate_component(self, component_id: str) -> Optional[str]:
        """Duplicate a component"""
        if component_id not in self.components:
            return None
        
        original = self.components[component_id]
        duplicate = original.duplicate()
        
        # Position slightly offset
        duplicate.position.x += 20
        duplicate.position.y += 20
        
        # Add to same parent
        return self.add_component(duplicate, original.parent_id)
    
    def move_component(self, component_id: str, new_x: float, new_y: float):
        """Move a component to new position"""
        if component_id in self.components:
            component = self.components[component_id]
            component.position.x = new_x
            component.position.y = new_y
            component.update_timestamp()
            self.save_history()
    
    def resize_component(self, component_id: str, new_width: str, new_height: str):
        """Resize a component"""
        if component_id in self.components:
            component = self.components[component_id]
            component.size.set_size(self.current_breakpoint, new_width, new_height)
            component.update_timestamp()
            self.save_history()
    
    def update_component_style(self, component_id: str, style_updates: Dict[str, Any]):
        """Update component styles"""
        if component_id not in self.components:
            return
        
        component = self.components[component_id]
        
        # Update base styles
        for key, value in style_updates.items():
            if hasattr(component.styles, key):
                setattr(component.styles, key, value)
        
        # Handle responsive overrides
        if 'responsive_overrides' in style_updates:
            component.styles.responsive_overrides.update(style_updates['responsive_overrides'])
        
        component.update_timestamp()
        self.save_history()
    
    def select_component(self, component_id: str, multi_select: bool = False):
        """Select a component"""
        if not multi_select:
            self.selected_component_ids.clear()
        
        if component_id in self.components and component_id not in self.selected_component_ids:
            self.selected_component_ids.append(component_id)
    
    def deselect_all(self):
        """Deselect all components"""
        self.selected_component_ids.clear()
    
    def switch_breakpoint(self, breakpoint: ResponsiveBreakpoint):
        """Switch to different responsive breakpoint"""
        self.current_breakpoint = breakpoint
    
    def set_zoom(self, zoom_level: float):
        """Set canvas zoom level"""
        self.zoom_level = max(0.1, min(5.0, zoom_level))
    
    def save_history(self):
        """Save current state to history"""
        project_data = self.export_project()
        self.history.save_state(project_data)
    
    def undo(self):
        """Undo last change"""
        previous_state = self.history.undo()
        if previous_state:
            self.import_project(previous_state)
    
    def redo(self):
        """Redo next change"""
        next_state = self.history.redo()
        if next_state:
            self.import_project(next_state)
    
    def export_project(self) -> Dict[str, Any]:
        """Export project to dictionary"""
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'components': {
                comp_id: {
                    'id': comp.id,
                    'component_type': comp.component_type,
                    'name': comp.name,
                    'category': comp.category.value,
                    'position': asdict(comp.position),
                    'size': comp.size.breakpoints,
                    'styles': asdict(comp.styles),
                    'content': comp.content,
                    'properties': comp.properties,
                    'actions': [asdict(action) for action in comp.actions],
                    'children': [child.id for child in comp.children],
                    'parent_id': comp.parent_id,
                    'is_locked': comp.is_locked,
                    'is_hidden': comp.is_hidden,
                    'created_at': comp.created_at,
                    'updated_at': comp.updated_at,
                    'version': comp.version,
                    'ai_agent_config': comp.ai_agent_config,
                    'data_bindings': comp.data_bindings
                }
                for comp_id, comp in self.components.items()
            },
            'root_components': self.root_components,
            'current_breakpoint': self.current_breakpoint.value,
            'theme': self.theme.value,
            'assets': self.assets
        }
    
    def import_project(self, project_data: Dict[str, Any]):
        """Import project from dictionary"""
        self.project_id = project_data.get('project_id', self.project_id)
        self.project_name = project_data.get('project_name', self.project_name)
        self.created_at = project_data.get('created_at', self.created_at)
        self.updated_at = project_data.get('updated_at', self.updated_at)
        
        # Clear existing components
        self.components.clear()
        self.root_components.clear()
        
        # Import components
        components_data = project_data.get('components', {})
        for comp_id, comp_data in components_data.items():
            component = ShopifyStyleComponent(
                comp_data['component_type'],
                comp_data['name'],
                ComponentCategory(comp_data['category'])
            )
            
            # Restore component data
            component.id = comp_data['id']
            component.position = Position(**comp_data['position'])
            component.size.breakpoints = comp_data['size']
            component.styles = StyleProperties(**comp_data['styles'])
            component.content = comp_data['content']
            component.properties = comp_data['properties']
            component.actions = [ComponentAction(**action_data) for action_data in comp_data['actions']]
            component.parent_id = comp_data['parent_id']
            component.is_locked = comp_data['is_locked']
            component.is_hidden = comp_data['is_hidden']
            component.created_at = comp_data['created_at']
            component.updated_at = comp_data['updated_at']
            component.version = comp_data['version']
            component.ai_agent_config = comp_data['ai_agent_config']
            component.data_bindings = comp_data['data_bindings']
            
            self.components[comp_id] = component
        
        # Restore component hierarchy
        for comp_id, comp_data in components_data.items():
            component = self.components[comp_id]
            for child_id in comp_data['children']:
                if child_id in self.components:
                    component.children.append(self.components[child_id])
        
        self.root_components = project_data.get('root_components', [])
        self.current_breakpoint = ResponsiveBreakpoint(project_data.get('current_breakpoint', 'desktop'))
        self.theme = BuilderTheme(project_data.get('theme', 'light'))
        self.assets = project_data.get('assets', {})
    
    def generate_html(self, include_styles: bool = True) -> str:
        """Generate complete HTML for the project"""
        html_parts = []
        
        if include_styles:
            html_parts.append(self._generate_html_head())
        
        html_parts.append('<body>')
        
        # Generate root components
        for root_id in self.root_components:
            if root_id in self.components:
                html_parts.append(self.components[root_id].to_html(self.current_breakpoint))
        
        if include_styles:
            html_parts.append(self._generate_scripts())
        
        html_parts.append('</body>')
        
        if include_styles:
            html_parts.append('</html>')
        
        return '\n'.join(html_parts)
    
    def _generate_html_head(self) -> str:
        """Generate HTML head section"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.project_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #333333;
        }}
        
        .component {{
            position: relative;
        }}
        
        /* Responsive utilities */
        @media (max-width: 767px) {{
            .mobile-hidden {{ display: none !important; }}
        }}
        
        @media (min-width: 768px) and (max-width: 1023px) {{
            .tablet-hidden {{ display: none !important; }}
        }}
        
        @media (min-width: 1024px) {{
            .desktop-hidden {{ display: none !important; }}
        }}
        
        /* Animation classes */
        .fade-in {{
            animation: fadeIn 0.6s ease-in-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .slide-up {{
            animation: slideUp 0.5s ease-out;
        }}
        
        @keyframes slideUp {{
            from {{ transform: translateY(30px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}
    </style>
</head>"""
    
    def _generate_scripts(self) -> str:
        """Generate JavaScript for interactivity"""
        return """
    <script>
        // Simple interaction handling
        document.addEventListener('DOMContentLoaded', function() {
            // Add click handlers for buttons
            const buttons = document.querySelectorAll('button.component');
            buttons.forEach(button => {
                button.addEventListener('click', function(e) {
                    console.log('Button clicked:', this.id);
                    // Add custom action handling here
                });
            });
            
            // Add intersection observer for animations
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in');
                    }
                });
            });
            
            document.querySelectorAll('.component').forEach(el => {
                observer.observe(el);
            });
        });
    </script>"""
    
    def generate_react_components(self) -> str:
        """Generate React components from the project"""
        react_code = []
        
        react_code.append("import React from 'react';")
        react_code.append("import styled from 'styled-components';")
        react_code.append("")
        
        # Generate styled components
        for comp_id, component in self.components.items():
            styled_name = f"Styled{component.name.replace(' ', '')}"
            base_element = component._get_html_tag()
            
            react_code.append(f"const {styled_name} = styled.{base_element}`")
            react_code.append(f"  {component.styles.get_css()}")
            react_code.append("`;")
            react_code.append("")
        
        # Generate main component
        react_code.append(f"const {self.project_name.replace(' ', '')} = () => {{")
        react_code.append("  return (")
        react_code.append("    <div>")
        
        for root_id in self.root_components:
            if root_id in self.components:
                component = self.components[root_id]
                react_code.append(f"      <Styled{component.name.replace(' ', '')}>")
                react_code.append(f"        {component.content.get('text', '')}")
                react_code.append(f"      </Styled{component.name.replace(' ', '')}>")
        
        react_code.append("    </div>")
        react_code.append("  );")
        react_code.append("};")
        react_code.append("")
        react_code.append(f"export default {self.project_name.replace(' ', '')};")
        
        return '\n'.join(react_code)
    
    def get_ai_suggestions(self, context: str = "") -> List[Dict[str, Any]]:
        """Get AI-powered suggestions for improving the project"""
        suggestions = []
        
        # Analyze current components
        component_count = len(self.components)
        
        if component_count == 0:
            suggestions.append({
                'type': 'template',
                'title': 'Start with a template',
                'description': 'Add a hero section or feature grid to get started quickly',
                'action': 'add_template',
                'priority': 'high'
            })
        
        if component_count > 0:
            # Check for missing responsive design
            responsive_components = sum(
                1 for comp in self.components.values()
                if comp.styles.responsive_overrides
            )
            
            if responsive_components / component_count < 0.5:
                suggestions.append({
                    'type': 'responsive',
                    'title': 'Add responsive design',
                    'description': 'Make your components mobile-friendly with responsive breakpoints',
                    'action': 'add_responsive',
                    'priority': 'medium'
                })
        
        # Check for accessibility
        suggestions.append({
            'type': 'accessibility',
            'title': 'Improve accessibility',
            'description': 'Add alt text to images and proper heading hierarchy',
            'action': 'improve_a11y',
            'priority': 'medium'
        })
        
        return suggestions

# Example usage and demonstration
def demo_shopify_style_builder():
    """Demonstration of the Shopify-style builder"""
    
    print("🏗️  Shopify-Style Visual Builder Demo")
    print("=" * 50)
    
    # Create a new project
    builder = ShopifyStyleBuilder("My Amazing Website")
    
    # Add hero section template
    hero_template = ComponentTemplate.create_hero_section()
    hero_component = hero_template.components[0]
    builder.add_component(hero_component)
    
    # Add feature grid template
    feature_template = ComponentTemplate.create_feature_grid()
    feature_component = feature_template.components[0]
    builder.add_component(feature_component)
    
    print(f"[CHECK] Created project: {builder.project_name}")
    print(f"📱 Components: {len(builder.components)}")
    print(f"🎨 Templates: {len(builder.templates)}")
    
    # Switch to mobile view
    builder.switch_breakpoint(ResponsiveBreakpoint.MOBILE)
    print(f"📱 Switched to mobile breakpoint")
    
    # Get AI suggestions
    suggestions = builder.get_ai_suggestions()
    print(f"🤖 AI Suggestions: {len(suggestions)}")
    for suggestion in suggestions:
        print(f"   • {suggestion['title']}: {suggestion['description']}")
    
    # Generate outputs
    html_output = builder.generate_html()
    react_output = builder.generate_react_components()
    
    print(f"📄 Generated HTML ({len(html_output)} characters)")
    print(f"⚛️  Generated React ({len(react_output)} characters)")
    
    # Test undo/redo
    builder.save_history()
    original_count = len(builder.components)
    
    # Add a test component
    test_component = ShopifyStyleComponent("text", "Test Component")
    builder.add_component(test_component)
    
    print(f"➕ Added component (total: {len(builder.components)})")
    
    # Undo
    builder.undo()
    print(f"↩️  Undone (total: {len(builder.components)})")
    
    # Export project
    project_data = builder.export_project()
    print(f"💾 Exported project data ({len(json.dumps(project_data))} bytes)")
    
    return builder

if __name__ == "__main__":
    demo_builder = demo_shopify_style_builder()
