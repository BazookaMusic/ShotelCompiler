from compiler import Compiler
from ast import FnDefinition, BinaryOperation
from typechecker import TypeManager, Environment, BaseType, ArrowType,VariableType

def test_typemgr_bind():
    mgr = TypeManager()

    a = mgr.new_type()
    b = mgr.new_type()

    mgr.bind("FREEDOM", a)
    mgr.bind("Democracy")

    assert mgr.bindings['FREEDOM'] is a
    assert mgr.bindings['Democrary'] is b

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
    int_to_int = ArrowType(int_type, int_type)

    env.bind(str(BinaryOperation.BinaryOperationKind.PLUS), int_type)
    env.bind(str(BinaryOperation.BinaryOperationKind.MINUS), int_type)

    return env

def test_fn_typecheck_simple():
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




if __name__ == "__main__":
    #test_typemgr_unify_left_placeholder()
    #test_typemgr_unify_right_placeholder()
    test_fn_typecheck_simple()

