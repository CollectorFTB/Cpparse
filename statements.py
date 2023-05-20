from construct import Struct, Select, Const, GreedyRange, NullTerminated, GreedyBytes, Computed, LazyBound, Debugger, Optional, GreedyString

class NamedStruct(Struct):
    def __init__(self, name, *subcons, **subconskw):
        subcons = tuple(['cls' / Computed(name)] + list(subcons))
        super().__init__(*subcons, **subconskw)


Comment = NamedStruct("Comment", 
    Const(b'//'),
    "data" / NullTerminated(GreedyBytes, term=b'\n', require=False),
)

IncludeStatement = NamedStruct("IncludeStatement",
    Const(b'#include '),
    "filename" / Select(
        NullTerminated(GreedyBytes, term=b'"\n', include=True),
        NullTerminated(GreedyBytes, term=b'>\n', include=True),
    ),
)

OtherPreprocessorStatement = NamedStruct('OtherPreprocessorStatement',
    Const(b'#'),
    'data' / NullTerminated(GreedyBytes, term=b'\n', require=False)
)

PreprocessorStatement = Select(
    IncludeStatement,
    OtherPreprocessorStatement
)

NewLine = Const(b'\n')
Semicolon = Const(b';')

Keyword = Struct(
    'name' / Select(
        Const(b'extern'),
        Const(b'const'),
    ),
    Const(b' ')    
)

TemplatedType = NamedStruct('TemplatedType',
    "name" / NullTerminated(GreedyBytes, term=b'<', include=False),
    "args" / NullTerminated(GreedyBytes, term=b'>', include=False),
    Optional(Const(b' '))
)

CppType = Select(
    TemplatedType,
    NullTerminated(GreedyBytes, term=b' ', include=True),
)

Variable = NamedStruct('Variable',
    'keywords' / GreedyRange(Keyword),
    "type" / CppType,
    "name" / NullTerminated(GreedyBytes, term=b';', consume=False),
    Semicolon,
    NewLine
)

Namespace = (NamedStruct('Namespace',
    Const(b'namespace '),
    'name' / NullTerminated(GreedyBytes, term=b' ', include=True),
    Const(b'{'),
    'inner' / GreedyRange(LazyBound(lambda: Cpp)),
    Const(b'}'),
    NullTerminated(GreedyBytes, term=b'\n', include=True, require=False),
))

Cpp = Select(
    NewLine,
    Comment,
    Variable,
    Namespace,
)

Statement = Select(
    NewLine,
    Comment,
    PreprocessorStatement,
    Namespace,
    Cpp
)

HFile = GreedyRange(Statement)
