# backend_generator/PromptAnalysis/code_generator.py

from typing import List, Dict, Any, Optional
from .models import Role, BusinessRule, UserAccess, PermissionType, BusinessRuleType

class AuthorizationCodeGenerator:
    """
    Generate Node.js authorization code based on roles and business rules
    """
    
    def __init__(self):
        self.middleware_template = """
const jwt = require('jsonwebtoken');
const { User, Role, Permission } = require('../models');

// Role-based access control middleware
const authorize = (requiredPermissions = []) => {
    return async (req, res, next) => {
        try {
            const token = req.headers.authorization?.split(' ')[1];
            if (!token) {
                return res.status(401).json({ error: 'Access token required' });
            }

            const decoded = jwt.verify(token, process.env.JWT_SECRET);
            const user = await User.findById(decoded.userId).populate('roles');
            
            if (!user) {
                return res.status(401).json({ error: 'User not found' });
            }

            // Check if user has required permissions
            const userPermissions = await getUserPermissions(user);
            const hasPermission = requiredPermissions.every(permission => 
                userPermissions.includes(permission)
            );

            if (!hasPermission) {
                return res.status(403).json({ error: 'Insufficient permissions' });
            }

            req.user = user;
            next();
        } catch (error) {
            return res.status(401).json({ error: 'Invalid token' });
        }
    };
};

// Get user permissions from roles
const getUserPermissions = async (user) => {
    const permissions = [];
    for (const role of user.roles) {
        for (const permission of role.permissions) {
            if (!permissions.includes(permission)) {
                permissions.push(permission);
            }
        }
    }
    return permissions;
};

module.exports = { authorize };
"""

        self.model_template = """
import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../db';

// Interface for Role attributes
interface RoleAttributes {
  id: number;
  name: string;
  description: string | null;
  permissions: string[];
  accessLevel: 'public' | 'authenticated' | 'role_based' | 'owner_only' | 'admin_only';
  entityAccess: Record<string, string[]>;
  createdAt: Date;
  updatedAt: Date;
}

// Interface for Role creation attributes
interface RoleCreationAttributes extends Optional<RoleAttributes, 'id' | 'description' | 'entityAccess' | 'createdAt' | 'updatedAt'> {}

// Role model class
export class Role extends Model<RoleAttributes, RoleCreationAttributes> implements RoleAttributes {
  public id!: number;
  public name!: string;
  public description!: string | null;
  public permissions!: string[];
  public accessLevel!: 'public' | 'authenticated' | 'role_based' | 'owner_only' | 'admin_only';
  public entityAccess!: Record<string, string[]>;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

// Initialize the model
Role.init({
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true,
  },
  permissions: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    allowNull: false,
    defaultValue: [],
  },
  accessLevel: {
    type: DataTypes.ENUM('public', 'authenticated', 'role_based', 'owner_only', 'admin_only'),
    allowNull: false,
    defaultValue: 'role_based',
  },
  entityAccess: {
    type: DataTypes.JSONB,
    allowNull: false,
    defaultValue: {},
  },
  createdAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
  updatedAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
}, {
  sequelize,
  tableName: 'roles',
  timestamps: true,
});

// Interface for User attributes
interface UserAttributes {
  id: number;
  username: string;
  email: string;
  password: string;
  customPermissions: string[];
  restrictions: string[];
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Interface for User creation attributes
interface UserCreationAttributes extends Optional<UserAttributes, 'id' | 'customPermissions' | 'restrictions' | 'isActive' | 'createdAt' | 'updatedAt'> {}

// User model class
export class User extends Model<UserAttributes, UserCreationAttributes> implements UserAttributes {
  public id!: number;
  public username!: string;
  public email!: string;
  public password!: string;
  public customPermissions!: string[];
  public restrictions!: string[];
  public isActive!: boolean;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

// Initialize the model
User.init({
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  username: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
  password: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  customPermissions: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    allowNull: false,
    defaultValue: [],
  },
  restrictions: {
    type: DataTypes.ARRAY(DataTypes.STRING),
    allowNull: false,
    defaultValue: [],
  },
  isActive: {
    type: DataTypes.BOOLEAN,
    allowNull: false,
    defaultValue: true,
  },
  createdAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
  updatedAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
}, {
  sequelize,
  tableName: 'users',
  timestamps: true,
});

// Interface for BusinessRule attributes
interface BusinessRuleAttributes {
  id: number;
  name: string;
  description: string | null;
  ruleType: 'validation' | 'authorization' | 'workflow' | 'data_integrity' | 'business_logic' | 'audit';
  entity: string | null;
  condition: string;
  action: string;
  priority: number;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Interface for BusinessRule creation attributes
interface BusinessRuleCreationAttributes extends Optional<BusinessRuleAttributes, 'id' | 'description' | 'entity' | 'priority' | 'isActive' | 'createdAt' | 'updatedAt'> {}

// BusinessRule model class
export class BusinessRule extends Model<BusinessRuleAttributes, BusinessRuleCreationAttributes> implements BusinessRuleAttributes {
  public id!: number;
  public name!: string;
  public description!: string | null;
  public ruleType!: 'validation' | 'authorization' | 'workflow' | 'data_integrity' | 'business_logic' | 'audit';
  public entity!: string | null;
  public condition!: string;
  public action!: string;
  public priority!: number;
  public isActive!: boolean;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

// Initialize the model
BusinessRule.init({
  id: {
    type: DataTypes.INTEGER,
    autoIncrement: true,
    primaryKey: true,
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true,
  },
  ruleType: {
    type: DataTypes.ENUM('validation', 'authorization', 'workflow', 'data_integrity', 'business_logic', 'audit'),
    allowNull: false,
  },
  entity: {
    type: DataTypes.STRING,
    allowNull: true,
  },
  condition: {
    type: DataTypes.TEXT,
    allowNull: false,
  },
  action: {
    type: DataTypes.TEXT,
    allowNull: false,
  },
  priority: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 1,
  },
  isActive: {
    type: DataTypes.BOOLEAN,
    allowNull: false,
    defaultValue: true,
  },
  createdAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
  updatedAt: {
    type: DataTypes.DATE,
    allowNull: false,
    defaultValue: DataTypes.NOW,
  },
}, {
  sequelize,
  tableName: 'business_rules',
  timestamps: true,
});

export default { Role, User, BusinessRule };
"""

        self.route_template = """
const express = require('express');
const { authorize } = require('../middleware/auth');
const { Role, User, BusinessRule } = require('../models');

const router = express.Router();

// Role management routes
router.get('/roles', authorize(['read']), async (req, res) => {
    try {
        const roles = await Role.find();
        res.json(roles);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.post('/roles', authorize(['admin']), async (req, res) => {
    try {
        const role = new Role(req.body);
        await role.save();
        res.status(201).json(role);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Business rules routes
router.get('/business-rules', authorize(['read']), async (req, res) => {
    try {
        const rules = await BusinessRule.find();
        res.json(rules);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

router.post('/business-rules', authorize(['admin']), async (req, res) => {
    try {
        const rule = new BusinessRule(req.body);
        await rule.save();
        res.status(201).json(rule);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

module.exports = router;
"""

    def generate_authorization_code(self, roles: List[Role], business_rules: List[BusinessRule], user_access: List[UserAccess]) -> Dict[str, str]:
        """
        Generate complete authorization code for Node.js backend
        """
        code_files = {}
        
        # Generate middleware
        code_files['middleware/auth.js'] = self._generate_auth_middleware(roles)
        
        # Generate models
        code_files['models/authorization.js'] = self._generate_models(roles, business_rules)
        
        # Generate routes
        code_files['routes/authorization.js'] = self._generate_routes(roles, business_rules)
        
        # Generate business rule engine
        code_files['services/businessRuleEngine.js'] = self._generate_business_rule_engine(business_rules)
        
        # Generate role management service
        code_files['services/roleService.js'] = self._generate_role_service(roles, user_access)
        
        # Generate package.json updates
        code_files['package.json'] = self._generate_package_json()
        
        return code_files
    
    def _generate_auth_middleware(self, roles: List[Role]) -> str:
        """Generate authentication middleware"""
        middleware_code = self.middleware_template
        
        # Add role-specific middleware
        role_middleware = []
        for role in roles:
            role_middleware.append(f"""
// {role.name} role middleware
const require{role.name.title()} = authorize({[f"'{perm.value}'" for perm in role.permissions]});
""")
        
        middleware_code += "\n".join(role_middleware)
        middleware_code += "\nmodule.exports = { authorize" + ", ".join([f", require{role.name.title()}" for role in roles]) + " };"
        
        return middleware_code
    
    def _generate_models(self, roles: List[Role], business_rules: List[BusinessRule]) -> str:
        """Generate Mongoose models"""
        return self.model_template
    
    def _generate_routes(self, roles: List[Role], business_rules: List[BusinessRule]) -> str:
        """Generate authorization routes"""
        return self.route_template
    
    def _generate_business_rule_engine(self, business_rules: List[BusinessRule]) -> str:
        """Generate business rule engine"""
        engine_code = """
const { BusinessRule } = require('../models');

class BusinessRuleEngine {
    constructor() {
        this.rules = new Map();
    }

    async loadRules() {
        const rules = await BusinessRule.find({ isActive: true });
        for (const rule of rules) {
            this.rules.set(rule.name, rule);
        }
    }

    async evaluateRules(context) {
        const results = [];
        
        for (const [ruleName, rule] of this.rules) {
            try {
                const result = await this.evaluateRule(rule, context);
                results.push({
                    ruleName,
                    result,
                    action: rule.action
                });
            } catch (error) {
                console.error(`Error evaluating rule ${ruleName}:`, error);
            }
        }
        
        return results;
    }

    async evaluateRule(rule, context) {
        // Simple rule evaluation - can be extended with more complex logic
        const condition = rule.condition;
        
        // Replace placeholders in condition with context values
        let evaluatedCondition = condition;
        for (const [key, value] of Object.entries(context)) {
            evaluatedCondition = evaluatedCondition.replace(new RegExp(`\\{${key}\\}`, 'g'), value);
        }
        
        // Evaluate the condition (simplified - in production, use a proper expression evaluator)
        return this.safeEval(evaluatedCondition);
    }

    safeEval(expression) {
        // Simplified evaluation - in production, use a proper expression evaluator
        try {
            // Basic boolean expressions
            if (expression.includes('==')) {
                const [left, right] = expression.split('==').map(s => s.trim());
                return left === right;
            }
            if (expression.includes('!=')) {
                const [left, right] = expression.split('!=').map(s => s.trim());
                return left !== right;
            }
            if (expression.includes('>')) {
                const [left, right] = expression.split('>').map(s => s.trim());
                return parseFloat(left) > parseFloat(right);
            }
            if (expression.includes('<')) {
                const [left, right] = expression.split('<').map(s => s.trim());
                return parseFloat(left) < parseFloat(right);
            }
            
            return Boolean(expression);
        } catch (error) {
            return false;
        }
    }
}

module.exports = new BusinessRuleEngine();
"""
        return engine_code
    
    def _generate_role_service(self, roles: List[Role], user_access: List[UserAccess]) -> str:
        """Generate role management service"""
        service_code = """
const { Role, User } = require('../models');

class RoleService {
    async createRole(roleData) {
        const role = new Role(roleData);
        return await role.save();
    }

    async assignRoleToUser(userId, roleId) {
        const user = await User.findById(userId);
        if (!user) {
            throw new Error('User not found');
        }
        
        if (!user.roles.includes(roleId)) {
            user.roles.push(roleId);
            await user.save();
        }
        
        return user;
    }

    async removeRoleFromUser(userId, roleId) {
        const user = await User.findById(userId);
        if (!user) {
            throw new Error('User not found');
        }
        
        user.roles = user.roles.filter(role => role.toString() !== roleId);
        await user.save();
        
        return user;
    }

    async getUserRoles(userId) {
        const user = await User.findById(userId).populate('roles');
        return user.roles;
    }

    async checkUserPermission(userId, permission) {
        const user = await User.findById(userId).populate('roles');
        if (!user) {
            return false;
        }
        
        for (const role of user.roles) {
            if (role.permissions.includes(permission)) {
                return true;
            }
        }
        
        return user.customPermissions.includes(permission);
    }
}

module.exports = new RoleService();
"""
        return service_code
    
    def _generate_package_json(self) -> str:
        """Generate package.json with required dependencies"""
        return """
{
  "name": "authorization-backend",
  "version": "1.0.0",
  "main": "dist/index.js",
  "scripts": {
    "start": "node dist/index.js",
    "dev": "ts-node src/index.ts",
    "build": "tsc",
    "lint": "eslint ."
  },
  "dependencies": {
    "express": "^4.19.2",
    "sequelize": "^6.37.3",
    "pg": "^8.13.1",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "express-validator": "^7.0.1",
    "dotenv": "^16.4.5",
    "morgan": "^1.10.0",
    "compression": "^1.7.4"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "ts-node": "^10.9.0",
    "@types/node": "^20.0.0",
    "@types/express": "^4.17.0",
    "@types/cors": "^2.8.0",
    "@types/bcryptjs": "^2.4.0",
    "@types/jsonwebtoken": "^9.0.0",
    "nodemon": "^3.0.0"
  }
}
"""
    
    def generate_modifications(self, existing_code: str, new_roles: List[Role], new_rules: List[BusinessRule], changes: List[str]) -> str:
        """
        Generate code modifications for existing backend
        """
        modifications = []
        
        # Add new roles to existing code
        if new_roles:
            role_imports = []
            role_middleware = []
            
            for role in new_roles:
                role_imports.append(f"const require{role.name.title()} = require('./middleware/auth').require{role.name.title()};")
                role_middleware.append(f"// {role.name} role middleware added")
            
            modifications.append({
                'file': 'app.js',
                'action': 'add_imports',
                'content': '\n'.join(role_imports)
            })
        
        # Add new business rules
        if new_rules:
            rule_code = []
            for rule in new_rules:
                rule_code.append(f"""
// {rule.name}: {rule.description}
const {rule.name.replace(' ', '_')} = async (context) => {{
    // {rule.condition}
    // Action: {rule.action}
    return true;
}};
""")
            
            modifications.append({
                'file': 'services/businessRules.js',
                'action': 'add_rules',
                'content': '\n'.join(rule_code)
            })
        
        return modifications
    
    def generate_role_hierarchy(self, roles: List[Role], business_rules: List[BusinessRule]) -> Dict[str, str]:
        """
        Generate role hierarchy code
        """
        hierarchy_template = """
const { Role } = require('../models');

class RoleHierarchy {
    constructor() {
        this.hierarchy = {
            // Define role hierarchy
            'super_admin': ['admin', 'manager', 'user'],
            'admin': ['manager', 'user'],
            'manager': ['user'],
            'user': []
        };
    }

    // Check if role has permission through hierarchy
    async hasPermissionThroughHierarchy(userRole, requiredRole) {
        const userHierarchy = this.hierarchy[userRole] || [];
        return userHierarchy.includes(requiredRole) || userRole === requiredRole;
    }

    // Get all roles user can access
    async getUserAccessibleRoles(userRole) {
        return this.hierarchy[userRole] || [];
    }
}

module.exports = new RoleHierarchy();
"""
        
        return {
            'role_hierarchy.js': hierarchy_template
        }
    
    def generate_comprehensive_auth_code(self, routes: List[str]) -> Dict[str, str]:
        """
        Generate comprehensive authorization code for existing routes
        """
        comprehensive_template = """
const jwt = require('jsonwebtoken');
const { User, Role, Permission } = require('../models');

class ComprehensiveAuth {
    constructor() {
        this.routePermissions = {
            // Define route permissions
            '/api/users': ['admin', 'manager'],
            '/api/admin': ['admin'],
            '/api/public': []
        };
    }

    // Middleware for route protection
    protectRoute = (route) => {
        return async (req, res, next) => {
            try {
                const token = req.headers.authorization?.split(' ')[1];
                if (!token) {
                    return res.status(401).json({ error: 'Access token required' });
                }

                const decoded = jwt.verify(token, process.env.JWT_SECRET);
                const user = await User.findById(decoded.userId).populate('roles');
                
                if (!user) {
                    return res.status(401).json({ error: 'User not found' });
                }

                // Check route permissions
                const requiredRoles = this.routePermissions[route] || [];
                if (requiredRoles.length > 0) {
                    const userRoles = user.roles.map(role => role.name);
                    const hasAccess = requiredRoles.some(role => userRoles.includes(role));
                    
                    if (!hasAccess) {
                        return res.status(403).json({ error: 'Insufficient permissions for this route' });
                    }
                }

                req.user = user;
                next();
            } catch (error) {
                return res.status(401).json({ error: 'Invalid token' });
            }
        };
    }
}

module.exports = new ComprehensiveAuth();
"""
        
        return {
            'comprehensive_auth.js': comprehensive_template
        }
