from lang.types import *
from lang.ops import *

declarations = {}
errors = []

def check_redeclaration(lineno, var_name):
    if var_name in declarations:
        print('errors:')
        print('\tline {}: cannot redeclare `{}`'.format(lineno, var_name))
        exit(1)

def check_semantics(lineno, value):
    lvalue = value.lhs
    rvalue = value.rhs

    identifier = lvalue.id if isinstance(lvalue, UCIdentifier) else lvalue.lhs.id
    variable = declarations[identifier]

    # check assignment for a variable which is neither UCArrayDeref nor UCRecordDeref
    if isinstance(lvalue, UCIdentifier):
        if isinstance(variable, UCRecord):
            # if the variable is a record, it must be initialized using UCRecordInitializerList
            if not isinstance(rvalue, UCRecordInitializerList):
                errors.append((lineno, 'a record must be initialized using UCRecordInitializerList'))

            # check if there is a nested UCRecordInitializerList, which is not allowed
            elif True in [isinstance(value, UCRecordInitializerList) for value in rvalue.value]:
                errors.append((lineno, 'UCRecordInitializerList cannot contain itself'))

        elif isinstance(variable, UCArray):
            # if the variable is an array, we can only assign a value to a certain index of the array
            errors.append((lineno, 'cannot assign an expression to a variable with array type'))
    else:
        # UCRecordInitializerList can only be assigned to a record
        if isinstance(rvalue, UCRecordInitializerList):
            errors.append((lineno, 'cannot assign UCRecordInitializerList to a non record type'))

        # check for type mismatch for a record
        if isinstance(lvalue, UCRecordDeref) and not isinstance(variable, UCRecord):
            errors.append((lineno, 'cannot assign an expression, `{}` is not a record'.format(identifier)))

        # check for type mismatch for an array
        if isinstance(lvalue, UCArrayDeref) and not isinstance(variable, UCArray):
            errors.append((lineno, 'cannot assign an expression, `{}` is not an array'.format(identifier)))

    __check_rvalue(lineno, rvalue)

def __check_rvalue(lineno, rvalue):
    if isinstance(rvalue, UCRecordInitializerList):
        __check_rvalue(lineno, rvalue.value[0])
        __check_rvalue(lineno, rvalue.value[1])
    elif isinstance(rvalue, UCRecordDeref):
        if not isinstance(declarations[rvalue.lhs.id], UCRecord):
            errors.append((lineno, '`{}` is not a record'.format(rvalue.lhs.id)))
    elif isinstance(rvalue, UCArrayDeref):
        if not isinstance(declarations[rvalue.lhs.id], UCArray):
            errors.append((lineno, '`{}` is not an array'.format(rvalue.lhs.id)))
    elif isinstance(rvalue, UCIdentifier):
        if isinstance(declarations[rvalue.id], UCRecord):
            errors.append((lineno, '`{}` is a record'.format(rvalue.id)))
        if isinstance(declarations[rvalue.id], UCArray):
            errors.append((lineno, '`{}` is an array'.format(rvalue.id)))
    elif isinstance(rvalue, UCNumberLiteral):
        pass
    elif isinstance(rvalue, UCMinus):
        __check_rvalue(lineno, rvalue.opr)
    else:
        __check_rvalue(lineno, rvalue.lhs)
        __check_rvalue(lineno, rvalue.rhs)
