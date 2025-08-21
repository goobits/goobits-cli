# 🏗️ Nested Command Implementation Proposal

**Feature Branch:** `feature/nested`  
**Target:** Goobits CLI Framework v2.1.0  
**Status:** Design Phase  

---

## 📋 **Executive Summary**

This proposal outlines a comprehensive implementation plan for **deep nested command support** in the Goobits CLI Framework. Currently, the system supports single-level command groups but has critical limitations with deep nesting (2+ levels) and subcommand arguments.

**Goal:** Enable unlimited depth command hierarchies with full argument/option support at every level.

---

## 🚨 **Current Limitations Analysis**

### ❌ **Critical Issues Identified**

#### 1. **Template Formatting Bugs**
```python
# CURRENT OUTPUT (BROKEN):
sys.exit(exit_code)@main.group()  # Missing newline

# EXPECTED OUTPUT:
sys.exit(exit_code)

@main.group()
```

#### 2. **Schema Mismatch in Subcommands**
```python
# TEMPLATE EXPECTS:
{% for arg in subcommand.arguments %}  # Uses .arguments

# SCHEMA PROVIDES:
subcommand.args  # Uses .args
```

#### 3. **Deep Nesting Not Supported**
```yaml
# THIS BREAKS:
commands:
  database:
    subcommands:
      users:          # Level 1: Works
        subcommands:
          admin:      # Level 2: BREAKS
```

#### 4. **Hook Discovery Complexity**
```python
# GENERATED HOOK NAME:
on_database_users_admin_create()  # Too complex, fails discovery
```

---

## 🎯 **Design Goals**

### **Primary Objectives**
1. **Unlimited Nesting Depth** - Support arbitrarily deep command hierarchies
2. **Full Feature Parity** - Arguments/options work at every level  
3. **Intuitive Hook System** - Simple, discoverable hook naming
4. **Backward Compatibility** - Zero breaking changes to existing CLIs
5. **Performance Optimization** - Minimal overhead for deep structures

### **Success Criteria**
- ✅ Support 5+ levels of nesting without issues
- ✅ Arguments generate correctly at all levels
- ✅ Hook discovery works intuitively 
- ✅ Generated code is clean and readable
- ✅ All existing tests continue to pass

---

## 🏗️ **Proposed Architecture**

### **1. Recursive Template Engine**

**Current:** Flat template with 1-level hardcoded subcommand support  
**Proposed:** Recursive template generator with depth-aware rendering

```python
# NEW: Recursive command generation
def generate_command_recursive(command_data, parent_path=None, depth=0):
    """
    Recursively generate commands with proper nesting support.
    
    Args:
        command_data: Command configuration
        parent_path: Parent command path (e.g., ['database', 'users'])
        depth: Current nesting depth (for optimization)
    """
    pass
```

### **2. Enhanced Schema Support**

**Current:** Basic subcommands dictionary  
**Proposed:** Nested command tree with metadata

```python
class EnhancedCommandSchema(BaseModel):
    """Enhanced command schema with deep nesting support."""
    
    desc: str
    args: Optional[List[ArgumentSchema]] = Field(default_factory=list)
    options: Optional[List[OptionSchema]] = Field(default_factory=list)
    subcommands: Optional[Dict[str, "EnhancedCommandSchema"]] = None
    
    # NEW: Nesting metadata
    parent_path: Optional[List[str]] = Field(default_factory=list)
    depth: int = 0
    hook_name: Optional[str] = None  # Pre-computed hook name
    command_path: Optional[str] = None  # Full command path
```

### **3. Smart Hook Discovery System**

**Current:** Simple name concatenation  
**Proposed:** Intelligent hook resolution with fallbacks

```python
class HookResolver:
    """Intelligent hook discovery with multiple resolution strategies."""
    
    def resolve_hook(self, command_path: List[str]) -> str:
        """
        Resolve hook name with fallback strategies:
        
        1. Exact match: on_database_users_create
        2. Abbreviated: on_db_users_create  
        3. Namespace: on_database__users_create
        4. Generic: on_command_executed
        """
        pass
```

---

## 🔧 **Implementation Plan**

### **Phase 1: Template Engine Fixes** (Week 1)
**Priority:** Critical Bug Fixes  
**Scope:** Fix current broken functionality

#### **1.1 Template Formatting**
- Fix missing newlines between command decorators
- Add proper whitespace handling in recursive sections
- Validate generated Python syntax

#### **1.2 Schema Consistency**  
- Align template to use `subcommand.args` (not `arguments`)
- Update all template references to match schema
- Add schema validation tests

#### **1.3 Basic Nesting Support**
- Fix 2-level nesting template issues
- Ensure proper decorator generation
- Test with complex examples

**Deliverables:**
- ✅ 2-level nesting works perfectly
- ✅ All syntax errors resolved
- ✅ Arguments generate at all levels

---

### **Phase 2: Recursive Template System** (Week 2-3)
**Priority:** Core Architecture  
**Scope:** Build recursive generation engine

#### **2.1 Template Refactoring**
```jinja2
{# NEW: Recursive command template #}
{% macro generate_command(cmd_name, cmd_config, parent_path=[], depth=0) %}
  {# Generate command with proper nesting #}
  
  {% if cmd_config.subcommands %}
    @{{ parent_path|join('.')|default('main') }}.group()
  {% else %}
    @{{ parent_path|join('.')|default('main') }}.command()
  {% endif %}
  
  {# Generate arguments recursively #}
  {% for arg in cmd_config.args %}
    @click.argument('{{ arg.name.upper() }}')
  {% endfor %}
  
  {# Recursive subcommand generation #}
  {% if cmd_config.subcommands %}
    {% for sub_name, sub_config in cmd_config.subcommands.items() %}
      {{ generate_command(sub_name, sub_config, parent_path + [cmd_name], depth + 1) }}
    {% endfor %}
  {% endif %}
{% endmacro %}
```

#### **2.2 Command Path Tracking**
- Implement parent path tracking through recursion
- Generate proper decorator chains (`@database.command()`)
- Maintain command hierarchy metadata

#### **2.3 Hook Name Generation**
```python
def generate_hook_name(command_path: List[str]) -> str:
    """
    Generate hook names with intelligent abbreviation:
    
    ['database', 'users', 'create'] -> 'on_database_users_create'
    ['api', 'v2', 'auth', 'tokens', 'refresh'] -> 'on_api_auth_tokens_refresh'
    """
    # Abbreviate long paths while maintaining uniqueness
    if len(command_path) > 4:
        return f"on_{command_path[0]}_{command_path[-2]}_{command_path[-1]}"
    return f"on_{'_'.join(command_path)}"
```

**Deliverables:**
- ✅ Recursive template generation
- ✅ Unlimited nesting depth support
- ✅ Clean hook name generation

---

### **Phase 3: Advanced Features** (Week 4)
**Priority:** Enhanced Functionality  
**Scope:** Polish and optimization

#### **3.1 Hook Discovery Enhancement**
```python
class SmartHookDiscovery:
    """Advanced hook discovery with multiple fallback strategies."""
    
    def discover_hook(self, command_path: List[str], hooks_module) -> callable:
        strategies = [
            self._exact_match,
            self._abbreviated_match,
            self._namespace_match,
            self._generic_fallback
        ]
        
        for strategy in strategies:
            hook = strategy(command_path, hooks_module)
            if hook:
                return hook
                
        raise HookNotFoundError(f"No hook found for {command_path}")
```

#### **3.2 Performance Optimization**
- Lazy command loading for deep hierarchies
- Template caching for repeated structures
- Optimized hook resolution

#### **3.3 Developer Experience**
- Auto-generate hook templates in `app_hooks.py`
- Rich help text with command hierarchy
- Intelligent error messages

**Deliverables:**
- ✅ Smart hook discovery system
- ✅ Performance optimizations
- ✅ Enhanced developer experience

---

### **Phase 4: Testing & Documentation** (Week 5)
**Priority:** Quality Assurance  
**Scope:** Comprehensive validation

#### **4.1 Test Suite Enhancement**
```python
class NestedCommandTests:
    """Comprehensive nested command testing."""
    
    def test_deep_nesting_5_levels(self):
        """Test 5-level deep command nesting."""
        
    def test_arguments_at_all_levels(self):
        """Ensure arguments work at every nesting level."""
        
    def test_hook_discovery_fallbacks(self):
        """Test hook discovery strategies."""
```

#### **4.2 Documentation**
- Update YAML schema documentation
- Add nested command examples
- Create migration guide

#### **4.3 Integration Testing**
- Test with all target languages (Python, Node.js, TypeScript, Rust)
- Validate generated CLI functionality
- Performance benchmarking

**Deliverables:**
- ✅ 100% test coverage for nested commands
- ✅ Complete documentation
- ✅ Multi-language validation

---

## 📊 **Example Implementations**

### **Complex Nested YAML (Target)**
```yaml
cli:
  commands:
    database:
      desc: "Database operations"
      subcommands:
        users:
          desc: "User management"
          options:
            - name: format
              type: str
              desc: "Output format"
          subcommands:
            create:
              desc: "Create a new user"
              args:
                - name: username
                  desc: "Username for new user"
                - name: email  
                  desc: "Email address"
              options:
                - name: admin
                  type: flag
                  desc: "Make user admin"
            
            permissions:
              desc: "Manage user permissions"
              subcommands:
                grant:
                  desc: "Grant permission to user"
                  args:
                    - name: user_id
                      desc: "User ID"
                    - name: permission
                      desc: "Permission to grant"
                
                revoke:
                  desc: "Revoke permission from user"
                  args:
                    - name: user_id
                      desc: "User ID"
                    - name: permission
                      desc: "Permission to revoke"
```

### **Generated CLI Structure (Target)**
```python
@main.group()
def database(ctx):
    """Database operations"""
    pass

@database.group()
@click.option('--format', type=str, help='Output format')
def users(ctx, format):
    """User management"""
    pass

@users.command()
@click.argument('USERNAME')
@click.argument('EMAIL')
@click.option('--admin', is_flag=True, help='Make user admin')
def create(ctx, username, email, admin):
    """Create a new user"""
    # Hook: on_database_users_create(username, email, admin=False, format=None)

@users.group()
def permissions(ctx):
    """Manage user permissions"""
    pass

@permissions.command()
@click.argument('USER_ID')
@click.argument('PERMISSION')
def grant(ctx, user_id, permission):
    """Grant permission to user"""
    # Hook: on_database_users_permissions_grant(user_id, permission, format=None)
```

### **Hook Implementation (Target)**
```python
# app_hooks.py
def on_database_users_create(username, email, admin=False, format=None):
    """Create a new user with specified permissions."""
    print(f"Creating user {username} with email {email}")
    if admin:
        print("Granting admin privileges")
    return 0

def on_database_users_permissions_grant(user_id, permission, format=None):
    """Grant permission to a user."""
    print(f"Granting {permission} to user {user_id}")
    return 0

# Alternative abbreviated hooks (auto-discovered)
def on_db_users_create(username, email, admin=False):
    """Abbreviated hook name for convenience."""
    return on_database_users_create(username, email, admin)
```

---

## 🎯 **Success Metrics**

### **Functional Requirements**
- [ ] Support 5+ levels of command nesting
- [ ] Arguments/options work at every level
- [ ] Hook discovery works with complex paths
- [ ] Generated code compiles and runs correctly
- [ ] All existing functionality preserved

### **Performance Requirements**
- [ ] <100ms CLI startup time (unchanged)
- [ ] <5ms per nesting level overhead
- [ ] Memory usage scales linearly with depth
- [ ] Template generation <10s for complex hierarchies

### **Developer Experience**
- [ ] Clear error messages for misconfigurations
- [ ] Auto-completion for nested commands
- [ ] Intuitive hook naming conventions
- [ ] Rich help text with command hierarchy

---

## 🚀 **Risk Assessment**

### **High Risk**
- **Template Complexity** - Recursive templates may be hard to debug
- **Hook Discovery** - Complex path resolution may confuse users
- **Performance** - Deep nesting could impact startup time

### **Medium Risk**  
- **Backward Compatibility** - Changes may break existing CLIs
- **Cross-Language** - Implementation complexity across all targets
- **Testing Coverage** - Combinatorial explosion of test cases

### **Mitigation Strategies**
1. **Phased Implementation** - Build incrementally with validation
2. **Feature Flags** - Allow disabling deep nesting if needed
3. **Comprehensive Testing** - Automated testing across all scenarios
4. **Clear Documentation** - Extensive examples and migration guides

---

## 📝 **Next Steps**

### **Immediate Actions**
1. ✅ Create `feature/nested` branch  
2. ✅ Document current limitations
3. ⏳ Begin Phase 1 implementation

### **Week 1 Goals**
- Fix all current template formatting issues
- Achieve working 2-level nesting
- Add comprehensive test coverage

### **Approval Required**
- [ ] Architecture review and approval
- [ ] Resource allocation for 5-week timeline
- [ ] Cross-language implementation strategy

---

**Author:** Claude Code  
**Date:** 2025-08-21  
**Version:** 1.0  
**Review Status:** Draft  