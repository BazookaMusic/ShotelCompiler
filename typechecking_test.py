from compiler import Compiler
from shotel_ast import FnDefinition, BinaryOperation, IntNode, StringNode,UnaryOperation
from typechecker import TypeManager, Environment, BaseType, ArrowType,VariableType

def test_typemgr_bind():
    mgr = TypeManager()

    a = mgr.new_type()
    b = mgr.new_type()

    mgr.bind("FREEDOM", a)
    mgr.bind("Democracy", b)

    assert mgr.bindings['FREEDOM'] is a
    assert mgr.bindings['Democracy'] is b

def test_typemgr_resolve():
    mgr = TypeManager()

    typechain = [mgr.new_type() for _ in range(100)]

    # first is unbound
    for i in range(1,len(typechain)):
        mgr.bind(typechain[i].name, typechain[i-1])

    someType, is_placeholder = mgr.resolve(typechain[-1])
    
    assert someType is typechain[0] and is_placeholder

def test_typemgr_unify_left_placeholder():
    mgr = TypeManager()

    types = [mgr.new_type() for _ in range(10)]

    # equivalence 5 -> 1 -> 0
    # create some bindings for left
    mgr.bind(types[5].name, types[1])
    mgr.bind(types[1].name, types[0])

    # left is a placeholder 
    left = types[5]

    # equivalence 8 -> 6 -> 4
    # some bindings for right
    mgr.bind(types[8].name, types[6])
    mgr.bind(types[6].name, types[4])

    right = types[8]

    mgr.unify(left, right)

    # we expect to add the binding 0 -> 4
    assert mgr.bindings[types[0].name] is types[4]

def test_typemgr_unify_right_placeholder():
    mgr = TypeManager()

    types = [mgr.new_type() for _ in range(10)]

    # equivalence 5 -> 1 -> 0
    # create some bindings for left
    mgr.bind(types[5].name, types[1])
    mgr.bind(types[1].name, types[0])

    # left is no longer a placeholder type after resolve
    mgr.bind(types[0].name, BaseType("Int"))

    # left is a placeholder 
    left = types[5]

    # equivalence 8 -> 6 -> 4
    # some bindings for right
    mgr.bind(types[8].name, types[6])
    mgr.bind(types[6].name, types[4])

    right = types[8]

    mgr.unify(left, right)

    # we expect to add the binding types 4 -> Int
    assert mgr.bindings[types[4].name].name == "Int"

def test_typemgr_unify_arrow_left():
    mgr = TypeManager()

    types = [mgr.new_type() for i in range(10)]

    an_arrow = ArrowType(types[0], types[3])
    another_arrow = ArrowType(types[1], types[4])

    fooType = BaseType("Foo")
    barType = BaseType("Bar")

    mgr.bind(types[0].name, fooType)
    mgr.bind(types[3].name, barType)

    mgr.unify(an_arrow, another_arrow)

    # Foo -> Bar == t1 => t4, so we expect t1 == Foo and t4 == Bar

    assert mgr.bindings[types[1].name].name == fooType.name
    assert mgr.bindings[types[4].name].name == barType.name

def test_typemgr_unify_arrow_right():
    mgr = TypeManager()

    types = [mgr.new_type() for i in range(10)]

    an_arrow = ArrowType(types[0], types[3])
    another_arrow = ArrowType(types[1], types[4])

    fooType = BaseType("Foo")
    barType = BaseType("Bar")

    mgr.bind(types[1].name, fooType)
    mgr.bind(types[4].name, barType)

    mgr.unify(an_arrow, another_arrow)

    # Foo -> Bar == t1 => t4, so we expect t1 == Foo and t4 == Bar

    assert mgr.bindings[types[0].name].name == fooType.name
    assert mgr.bindings[types[3].name].name == barType.name

def test_env():
    environment = Environment()


def ev(text):
    return Compiler.compile_from_text(text)

def env_setup():
    env = Environment()

    int_type = BaseType("Int")
    int_to_int_to_int = ArrowType(int_type, ArrowType(int_type, int_type))

    env.bind(str(BinaryOperation.BinaryOperationKind.PLUS), int_to_int_to_int)
    env.bind(str(BinaryOperation.BinaryOperationKind.MINUS), int_to_int_to_int)
    env.bind(str(UnaryOperation.UnaryOperationKind.NOT), ArrowType(int_type, int_type))

    return env

def test_typecheck_primitives():
    a = IntNode(15)
    b = StringNode("string")

    env = env_setup()
    mgr = TypeManager()

    assert a.typecheck(mgr, env) is IntNode.Type and IntNode.Type.name == "Int"
    assert b.typecheck(mgr,env) is StringNode.Type and StringNode.Type.name == "String"


def test_fn_typecheck_first_pass():
    program = ev('''
    fn Test a b c 
    {
        a + b + c
    }
    ''')

    env = env_setup()
    typeManager = TypeManager()

    # one definition
    assert len(program) == 1

    fn: 'FnDefintion' = program[0]

    fn.typecheck_first_pass(typeManager, env)

    return_type = env.bindings["Test"]

    # a -> (b -> c -> TestType)
    assert isinstance(return_type, ArrowType)
    assert isinstance(return_type.left, VariableType)
    assert isinstance(return_type.right, ArrowType)

    assert isinstance(return_type.right.left, VariableType)
    # b -> ( c -> TestType)
    assert isinstance(return_type.right.right, ArrowType)

    assert isinstance(return_type.right.left, VariableType)
    
    # c -> TestType
    assert isinstance(return_type.right.right, ArrowType)

    assert isinstance(return_type.right.right.left, VariableType)

    # TestType
    assert isinstance(return_type.right.right.right, VariableType)

def test_fn_typecheck_first_pass_no_args():
    program = ev('''
    fn Test
    {
        15 + 4
    }
    ''')

    env = env_setup()
    typeManager = TypeManager()

    # one definition
    assert len(program) == 1

    fn: 'FnDefintion' = program[0]

    fn.typecheck_first_pass(typeManager, env)

    return_type = env.bindings["Test"]

    assert isinstance(return_type, VariableType)

def test_fn_typecheck_second_pass():
    program = ev('''
    fn Test a b c 
    {
        a + b + c
    }
    ''')

    env = env_setup()
    typeManager = TypeManager()

    # one definition
    assert len(program) == 1

    fn: 'FnDefintion' = program[0]

    fn.typecheck_first_pass(typeManager, env)

    fn.typecheck_second_pass(typeManager, env)

    # return type is int
    assert typeManager.resolve(fn.return_type)[0].name == "Int"

    for param in fn.param_types:
        assert typeManager.resolve(param)[0].name == 'Int'

    fn_type = env.bindings['Test']

    VerifyArrow(fn_type, len(fn.params), '*')

def test_fn_typecheck_second_pass_no_args():
    program = ev('''
    fn Test
    {
        12
    }
    ''')

    env = env_setup()
    typeManager = TypeManager()

    # one definition
    assert len(program) == 1

    fn: 'FnDefinition' = program[0]

    fn.typecheck_first_pass(typeManager, env)

    fn.typecheck_second_pass(typeManager, env)

    # return type is int
    assert typeManager.resolve(env.bindings['Test'])[0].name == "Int"


def test_type_typecheck_no_params():
    program = ev('''
    type Bool = True, False
    type Cheese = Edam, Cottage, Feta, BlueCheese
    ''')

    env = env_setup()
    typeManager = TypeManager()

    for definition in program:
        definition.typecheck(typeManager, env)

        for cons in definition.constructors:
            assert typeManager.resolve(env.bindings[cons.name])[0].name == definition.name

def test_type_typecheck_params():
    program = ev('''
    type Foo = Bar X Y, Foobar X Y Z, MyBar L M N O P Q R S T U V W X Y Z
    ''')

    env = env_setup()
    typeManager = TypeManager()

    for definition in program:
        definition.typecheck(typeManager, env)
        for cons in definition.constructors:
            VerifyArrow(typeManager.resolve(env.bindings[cons.name])[0], len(cons.types), definition.name)

def test_unary_operation_typechecking():
    program = ev('''
    fn Test
    {
        !1
    }
    ''')

    env = env_setup()
    typeManager = TypeManager()

    fn = program[0]

    unaryOp = fn.body

    type_returned = unaryOp.typecheck(typeManager, env)

    assert typeManager.resolve(type_returned)[0].name == 'Int'

def test_binary_operation_typechecking():
    program = ev('''
    fn Test a b
    {
        a + b
    }
    ''')

    env = env_setup()
    typeManager = TypeManager()

    fn = program[0]

    fn.typecheck(typeManager, env)

    assert typeManager.resolve(fn.return_type)[0].name == 'Int'

    assert typeManager.resolve(fn.param_types[0])[0].name == 'Int'
    assert typeManager.resolve(fn.param_types[1])[0].name == 'Int'

def test_function_application_typechecking():
    program = ev('''
    fn Add a b
    {
        a + b
    }

    fn Test a b
    {
        Add a b
    }
    ''')

    env = env_setup()
    typeManager = TypeManager()

    program.typecheck(typeManager, env)

    add_fn = program[0]
    
    for param_type in add_fn.param_types:
        assert typeManager.resolve(param_type)[0].name == 'Int'
    
    assert typeManager.getResolvedType(add_fn.return_type).name == 'Int'

    test_fn = program[1]

    for param_type in add_fn.param_types:
        assert typeManager.getResolvedType(param_type).name == 'Int'

    assert typeManager.getResolvedType(test_fn.return_type).name == "Int"

    

def VerifyArrow(arrow_type: ArrowType, n_params: int, final_type_name: str):
    temp = arrow_type

    while isinstance(temp, ArrowType):
        n_params -= 1
        assert isinstance(temp.left, VariableType)
        temp = temp.right
    
    assert n_params == 0
    if final_type_name != '*':
        assert temp.name == final_type_name
    



if __name__ == "__main__":
    #test_typemgr_unify_left_placeholder()
    #test_typemgr_unify_right_placeholder()
    #test_fn_typecheck_second_pass_no_args()
    #test_fn_typecheck_second_pass()
    test_function_application_typechecking()

