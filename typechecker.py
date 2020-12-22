class TypeBindingError(Exception):
    pass

class UndefinedTypeError(Exception):
    pass

class Type:
    pass

class VariableType(Type):
    def __init__(self, name):
        self.name: str = name

class BaseType(Type):
    def __init__(self, name):
        self.name: str = name

BaseTypes = [BaseType("Int"), BaseType("String")]

class ArrowType(Type):
    def __init__(self, left, right):
        self.left: 'Type' = left
        self.right: 'Type' = right

class TypeManager:
    def __init__(self):
        self.bindings = {}
        self.counter = 0

    def new_typename(self):
        new_name =  f"t_{self.counter}"
        self.counter += 1

        return new_name
    
    def new_type(self):
        return VariableType(self.new_typename())
    
    def new_arrow(self):
        return ArrowType(self.new_type(), self.new_type())
    
    def bind(self, name, someType):
        variable = None

        if isinstance(someType, VariableType):
            variable = someType
        
        if variable is not None and variable.name == name:
            return
        
        self.bindings[name] = someType
    
    def unify(self, left: 'Type', right: 'Type'):
        '''
        Unifies two types by creating new bindings, so that they can be considered equivalent.
        Ex: int -> double (unify) a -> b =====> a = int, b = double
        '''

        left, is_left_placeholder = self.resolve(left)
        right, is_right_placeholder = self.resolve(right)

        # left is bound and a placeholder type, so right should bound with the same name
        if is_left_placeholder:
            self.bind(left.name, right)
            return
        # other way around
        elif is_right_placeholder:
            self.bind(right.name, left)
            return
        # arrow types are equal means that their types must be bound to the same
        elif isinstance(left, ArrowType) and isinstance(right, ArrowType):
            self.unify(left.left, right.left)
            self.unify(left.right, right.right)
            return
        # base types should be bound to the same name
        # binding an int to a double should be an error
        elif isinstance(left, BaseType) and isinstance(right, BaseType):
            if left.name == right.name:
                return
        
        raise TypeBindingError(f"Error while trying to unify types {left} of type {type(left)} and {right} of type {type(right)}.")
        
    
    def resolve(self,someType):
        '''
        Takes a type variable and goes through
        the chain of bindings to find the last.

        Returns the last binding in the chain and if the chain
        ends in a placeholder.

        Ex: a => b, b => c, c => int |> returns c, False
        a1 => a2, a2 => a3 |> returns a3, True 
        '''
        placeHolderType = None

        # skip any other type than TypeVariables
        while isinstance(someType, VariableType):
            binding = self.bindings.get(someType.name)

            # we found a placeholder type
            # return it and its matching type
            if binding is None:
                placeHolderType = someType
                return someType, True
            
            someType = binding
        
        return someType, False

class Environment:
    '''
    An environment of type bindings.
    '''
    def __init__(self, bindings = None, parent = None):
        self.bindings = {} if bindings is None else bindings
        self.parent: 'Environment' = parent
    
    def lookup(self, name):
        '''
        Look for the type bound to the specific name. If current environment
        does not contain it, look for it in parent environments.
        '''
        maybeType = self.bindings.get(name)

        if maybeType is not None:
            return maybeType
        
        if self.parent is not None:
            return self.parent.lookup(item)
        
        return None
    
    def bind(self, name, someType):
        '''Bind a name to a type for this environment'''
        self.bindings[name] = someType

    def new_scope(self):
        '''
        Create a new scope with the current environment as its parent.
        '''
        return Environment({}, self) 
    

    




        
    


    