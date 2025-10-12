"""
NodeJS backend generator for CodeCraft.

Given an `ERDSchema`, this package generates a Node.js Express project
with Sequelize models and CRUD route/controller stubs.
"""

from .generator import NodeProjectGenerator
from .advanced_generator import AdvancedNodeProjectGenerator

__all__ = ["NodeProjectGenerator", "AdvancedNodeProjectGenerator"]


