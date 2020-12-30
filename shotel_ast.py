from enum import Enum
from typechecker import BaseType, ArrowType, TypeBindingError, UndefinedTypeError, VariableUndefinedError

class AST:
    pass

class IntNode(AST):
    def __init__(self, value: int):
        self.value: int = value
        self.isLeaf = True
    
    def typecheck(self, typeManager, env):
        return IntNode.Type
    def __repr__(self):
        return f'INT({self.value})'
    
    Type = BaseType("Int")

class StringNode(AST):
    def __init__(self, value: str):
        self.value: str = value
        self.isLeaf = True
    
    def typecheck(self, typeManager, env):
        return StringNode.Type

    def __repr__(self):
        return f'String({self.value})'
    
    Type = BaseType("String")

class LID(AST):
    def __init__(self, value: str):
        self.value: str = value
        self.isLeaf = True
    
    def typecheck(self, typeManager, env):
        res = env.lookup(self.value)

        if res is None:
            raise VariableUndefinedError(f"Variable '{self.value}' is undefined. Its type cannot be determined.")

        return res


    def __repr__(self):
        return f'LID({self.value})'

class UID(AST):
    def __init__(self, value: str):
        self.value: str = value
        self.isLeaf = True
    
    def typecheck(self, typeManager, env):
        res = env.lookup(self.value)

        if res is None:
            raise VariableUndefinedError(f"Variable '{self.value}' is undefined,so it's type cannot be determined.")
        
        return res

    def __repr__(self):
        return f'UID({self.value})'

class BinaryOperation(AST):
    BinaryOperationKind = Enum("OperationKind", 
    [
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "MODULO",
        "RSHIFT",
        "LSHIFT",
        "AND",
        "OR",
        "XOR",
        "EQUALS",
        "NEQUALS"
    ])

    def __init__(self, kind: Enum, left: 'AST', right: 'AST'):
        self.left: 'AST' = left
        self.right: 'AST' = right
        self.kind: 'Enum' = kind
    
    def typecheck(self, typeManager: 'TypeManager', env):
        # operator type is of the form a => b => c

        # resolve left argument type
        leftType = self.left.typecheck(typeManager, env)

        # resolve right argument type
        rightType = self.right.typecheck(typeManager, env)

        # type of operator should be known
        functionType = env.lookup(str(self.kind))

        # unknown is error
        if functionType is None:
            raise TypeBindingError(f"Could not find a binding for the binary operation {self.kind}.")

        returnType = typeManager.new_type()

        # b => c
        b_to_c = ArrowType(rightType, returnType)

        # a => (b => c)
        a_to_b_to_c = ArrowType(leftType, b_to_c)
        
        typeManager.unify(a_to_b_to_c, functionType)

        return returnType

    def __repr__(self):
        return f"BinaryOp({self.kind})"

class UnaryOperation(AST):

    UnaryOperationKind = Enum("UnaryOp",["NOT"])

    def __init__(self, kind: 'Enum', op: 'AST'):
        self.kind: 'Enum' = kind
        self.op: 'AST' = op

    def __repr__(self):
        return f"UnaryOp({self.kind}"
    
    def typecheck(self, typeManager: 'TypeManager', env: 'Environment'):
        valueType: 'Type' = self.op.typecheck(typeManager, env)
        functionType: 'Type' = env.lookup(str(self.kind))

        returnType: 'ArrowType' = typeManager.new_type()
        arrow = ArrowType(valueType, returnType)

        typeManager.unify(arrow, functionType)

        return returnType


class FunctionApplication(AST):
    def __init__(self, left: 'AST', right: 'AST'):
        self.left: 'AST' = left
        self.right: 'AST' = right

    def __repr__(self):
        return f"Fn"
    
    def typecheck(self, typeManager: 'TypeManager', env: 'Environment'):
        # application has type (a => b) => a => b

        # (a => b => c) a

        left = self.left.typecheck(typeManager, env)
        right = self.right.typecheck(typeManager, env)

        returnType = typeManager.new_type()
        arrow = ArrowType(right, returnType)

        typeManager.unify(arrow, left)

        return returnType

class Pattern:
    pass

class PatternConstructor(Pattern):
    def __init__(self, name: str, params: [str]):
        self.name: str = name
        self.params: [str] = params

    def __repr__(self):
        return f"PatternConstructor({self.name}){self.params}"
    
    def match(self, ofType: 'Type', typeManager, env):
        '''
        Matches someType with the type of all the branches.
        Constructor type is in the form: a->b->c->C, where C should be the type of Of.
        '''
        constructor_type = env.lookup(self.name)
        if constructor_type is None:
            raise UndefinedTypeError(f"Constructor type {self.name} is undefined.")
        
        # Reduce the arrow, binding each param along the way
        # if the constructor type is a->b->c->C
        # first param will be a, second b, third c
        for param in self.params:
            arrow = constructor_type
            if constructor_type is None:
                raise UndefinedTypeError(f"Type {self.name} is undefined.")

            env.bind(param, arrow.left)
            constructor_type = arrow.right
        
        # finally C should be the same type as Of
        typeManager.unify(ofType, constructor_type)

        # constructors are only allowed to be base types
        if not isinstance(constructor_type, BaseType):
            raise TypeBindingError("Constructor {self.name} is not a base type. Pattern constructors can only be base types.")



class PatternVar(Pattern):
    def __init__(self, name: str):
        self.name: str = name

    def __repr__(self):
        return f"PatternVar({self.name})"
    
    def match(self, someType, typeManager, env):
        env.bind(self.name, someType)

class Branch:
    def __init__(self, pattern: 'Pattern', expresion: 'AST'):
        self.pattern: 'Pattern' = pattern
        self.expression: 'AST' = expresion

    def __repr__(self):
        return "Branch"

class CaseOf(AST):
    def __init__(self, Of: 'AST', branches: ['AST']):
        self.Of = Of
        self.branches: ['Branch'] = branches
    
    def typecheck(self, typeManager: 'TypeManager', env: 'Environment'):
        '''
        Typechecks a case statement.
        '''

        # First determine type of the Of
        of_type = self.Of.typecheck(typeManager, env)

        # create a new type, the type of the branches
        branch_type = typeManager.new_type()

        for branch in self.branches:
            # each branch is in a new scope, they don't share variables
            new_env = env.new_scope()

            # pattern should be same type as Of
            branch.pattern.match(of_type, typeManager, new_env)

            # all branches should return the same type, equal with the new type we created
            curr_branch_type = branch.expression.typecheck(typeManager, new_env)
            typeManager.unify(branch_type, curr_branch_type)
        
        return branch_type


    def __repr__(self):
        return "CaseOf"

class Constructor:
    def __init__(self, name: str, types: [str]):
        self.name: str = name
        self.types: [str] = types

    def __repr__(self):
        return f"Constructor({self.name}){self.types}"

class Definition:
    def typecheck(self, typeManager: 'TypeManager', env:'Environment'):
        self.typecheck_first_pass(typeManager, env)
        self.typecheck_second_pass(typeManager, env)

class FnDefinition(Definition):
    def __init__(self, name: str, params: [str], body: 'AST'):
        self.name: str = name
        self.params: [str] = params
        self.body: 'AST' = body
        self.return_type = None
        self.param_types = []

    def typecheck_first_pass(self, typeManager, env):
        '''
        First typechecking pass.
        Binds a generic function type of the form a1->a2->a3->return_type,
        where a1,a2,..,an are a new type for each variable and 'return_type' a new type
        for the return type of the function.
        '''
        self.return_type = typeManager.new_type()
        full_type = self.return_type

        for param in self.params:
            new_type = typeManager.new_type()
            self.param_types.append(new_type)

        length = len(self.param_types)
        for i in range(length):
            param_type = self.param_types[length - i - 1]
            full_type = ArrowType(param_type, full_type)
        
        env.bind(self.name, full_type)
    
    def typecheck_second_pass(self, typeManager, env):
        new_env = env.new_scope()

        last_param = len(self.params) - 1
        for i in range(len(self.param_types)):
            new_env.bind(self.params[i], self.param_types[i])
        
        body_type = self.body.typecheck(typeManager, new_env)
        typeManager.unify(body_type, self.return_type)

    def __repr__(self):
        return f"DefinitionFn({self.name}){self.params}"

class TypeDefinition(Definition):
    def __init__(self, name: str, constructors: ['Constructor']):
        self.name: str = name
        self.constructors: ['Constructor'] = constructors

    def __repr__(self):
        return f"DefinitionType({self.name}){self.constructors}"
    
    def typecheck_first_pass(self, typeManager: 'TypeManager', env: 'Environment'):
        return_type = BaseType(self.name)

        for constructor in self.constructors:
            full_type = return_type
            
            for param in constructor.types:
                param_type = typeManager.new_type()
                full_type = ArrowType(param_type, full_type)
            
            env.bind(constructor.name, full_type)
    
    def typecheck_second_pass(self, typeManager: 'TypeManager', env: 'Environment'):
        pass

class Program:
    def __init__(self, definitions):
        self.definitions: ['Definition'] = definitions
    
    def typecheck(self, typeManager, env):
        for definition in self.definitions:
            definition.typecheck_first_pass(typeManager, env)
        
        for definition in self.definitions:
            definition.typecheck_second_pass(typeManager, env)
    
    def __getitem__(self, index):
        return self.definitions[index]



        
            
        
        