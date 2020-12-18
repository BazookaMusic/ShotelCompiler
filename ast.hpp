#pragma once
#include <memory>
#include <vector>

namespace AST
{
    struct AST
    {
        virtual ~AST() = default;
    };

    using AstPtr = std::unique_ptr<AST>;

    /// integer
    struct IntValue
    {
        int Value;

        IntValue(int value)
            : Value(value)
        {}
    };

    /// lowercase identifier
    struct LowercaseIdentifier
    {
        std::string Id;

        LowercaseIdentifier(std::string id)
            :Id(std::move(id)) {} 
    };

    /// uppercase identifier
    struct UppercaseIdentifier
    {
        std::string Id;

        UppercaseIdentifier(std::string id)
            :Id(std::move(id)) {} 
    };

    /// uppercase identifier
    struct CaseAgnosticIdentifier
    {
        std::string Id;

        CaseAgnosticIdentifier(std::string id)
            :Id(std::move(id)) {} 
    };

    // string
    struct StringLiteral
    {
        std::string Literal;

        StringLiteral(std::string literal)
            :Literal(std::move(literal)) {}
    };


    // Binary Operations
    enum BinaryOperationKind {
        PLUS,
        MINUS,
        TIMES,
        DIVIDE,
        MODULO,
        RSHIFT,
        LSHIFT,
        AND,
        OR,
        XOR,
        EQUALS,
        NEQUALS
    };

    struct BinaryOp
    {
        BinaryOperationKind Kind;
        AstPtr Left;
        AstPtr Right;

        BinaryOp(BinaryOperationKind kind, AstPtr left, AstPtr right)
            : Kind(kind), Left(std::move(left)), Right(std::move(right)) {}
    };

    // Unary operations
    enum UnaryOperationKind {
        NOT
    };

    struct UnaryOP
    {
        UnaryOperationKind Kind;
        AstPtr Operand;

        UnaryOP(UnaryOperationKind kind, AstPtr operand)
            : Kind(kind), Operand(std::move(operand)) {}
    };

    // function application

    struct FunctionApplication
    {
        AstPtr Left;
        AstPtr Right;

        FunctionApplication(AstPtr left, AstPtr right)
            : Left(std::move(left)), Right(std::move(right)) {}
    };

    // Pattern matching

    struct Pattern
    {
        virtual ~Pattern() = default;
    };

    using  PatternPtr = std::unique_ptr<Pattern>;

    // can match a constructor
    struct PatternConstructor
    {
        std::string Constructor;
        std::vector<std::string> Params;

        PatternConstructor(std::string constructorName, std::vector<std::string> params)
            : Constructor(constructorName), Params(std::move(params)) {}
    };

    // or a variable
    struct PatternVar
    {
        std::string Name;
        
        PatternVar(std::string variableName)
            : Name(std::move(variableName)) {}
    };


    struct Branch
    {
        PatternPtr Pattern;
        AstPtr Expression;

        Branch(PatternPtr pattern, AstPtr expression)
            : Pattern(std::move(pattern)), Expression(std::move(expression)) {}
    };

    using  BranchPtr = std::unique_ptr<Branch>;


    struct CaseOf
    {
        AstPtr Of;
        std::vector<BranchPtr> Branches;

        CaseOf(AstPtr ofExpression, std::vector<BranchPtr> branches)
            : Of(std::move(ofExpression)), Branches(std::move(branches)) {}
    };

    // Funtion definition
    struct Definition {
        virtual ~Definition() = default;
    };

    using  DefinitionPtr = std::unique_ptr<Definition>;

    struct Constructor {
        std::string Name;
        std::vector<std::string> Types;

        Constructor(std::string name, std::vector<std::string> types)
            : Name(std::move(name)), Types(std::move(types)) {}
    };

    using  ConstructorPtr = std::unique_ptr<Constructor>;

    struct DefinitionFn {
        std::string Name;
        std::vector<std::string> Params;

        std::vector<ConstructorPtr> data;

        AstPtr Body;

        DefinitionFn(std::string name, std::vector<std::string> params, AstPtr body)
            : Name(std::move(name)), Params(std::move(params)), Body(std::move(body)) {

        }
    };

    struct TypeDefinition
    {
        std::string Name;
        std::vector<ConstructorPtr> Constructors;

        TypeDefinition(std::string name, std::vector<ConstructorPtr> constructors)
            : Name(name), Constructors(std::move(constructors)) {

            }
    };
}
